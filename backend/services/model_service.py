import spacy
from spacy.matcher import Matcher
from transformers import pipeline
import re
from typing import List, Dict, Any, Optional
import dateparser




class ModelService:
    def __init__(self):
        self.intent_classifier = None
        self.nlp = None
        self.matcher = None
        # Mock database of known vessels
        self.vessel_list = [
            "ins kolkata", "ins vishakhapatnam", "msc flaminia", 
            "saint cruise ship", "ever given", "maersk alabama",
            "saina maria"
        ]

    def load_models(self):
        if self.intent_classifier is None:
            print("Loading Hugging Face Intent Model...")
            self.intent_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        if self.nlp is None:
            print("Loading Spacy Model...")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                from spacy.cli import download
                download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")

            self.matcher = Matcher(self.nlp.vocab)
            self._register_patterns()
        
        print("Models loaded successfully.")

    def _register_patterns(self):
        # Time horizon pattern: "after 30 minutes", "in 2 hours"
        pattern_time_horizon = [
            {"LOWER": {"IN": ["after", "in"]}},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": ["minutes", "minute", "hours", "hour", "days", "day"]}},
        ]
        self.matcher.add("TIME_HORIZON", [pattern_time_horizon])

    def get_intent_classifier(self):
        if not self.intent_classifier:
            self.load_models()
        return self.intent_classifier

    def predict(self, text: str, candidate_labels: List[str]) -> Dict[str, Any]:
        # Ensure models are loaded
        self.load_models()
        
        text_lower = text.lower()
        doc = self.nlp(text)

        # 1. Intent Extraction (Hybrid: Rules > HF)
        intent = self._extract_intent_hybrid(text_lower, candidate_labels)

        # 2. Vessel Name Extraction (Rule-based lookup)
        vessel_name = self._extract_vessel_name(text_lower)

        # 3. Identifiers (Regex) - Extract FIRST to avoid confusion with time
        identifiers = self._extract_identifiers(text_lower)

        # 4. Time Horizon / Date Extraction (Spacy + Regex + Validation)
        # Pass identifiers to exclude them from time extraction
        time_result = self._extract_time_info(doc, text_lower, identifiers)
        
        return {
            "intent": intent,
            "vessel_name": vessel_name,
            "time_horizon": time_result["time_horizon"],
            "identifiers": identifiers,
            "validation_error": time_result["validation_error"]
        }

    def _extract_intent_hybrid(self, text_lower: str, candidate_labels: List[str]) -> str:
        # Rule overrides for strong signals
        if "show" in text_lower or "find" in text_lower or "where is" in text_lower:
            return "SHOW" # or SEARCH
        if "predict" in text_lower or "forecast" in text_lower:
            return "PREDICT"
        
        # Fallback to HF Zero-Shot
        result = self.intent_classifier(text_lower, candidate_labels)
        return result["labels"][0].upper()

    def _extract_vessel_name(self, text_lower: str) -> Optional[str]:
        for vessel in self.vessel_list:
            if vessel in text_lower:
                # Capitalize for display
                return vessel.title()
        return None

    def _extract_time_info(self, doc, text_lower: str, identifiers: Dict) -> Dict[str, Optional[str]]:
        """
        Extracts time horizon and validates dates. 
        Returns {"time_horizon": str, "validation_error": str}
        """
        extracted_time = None
        validation_error = None

        # 1. Regex for Ranges (Priority)
        # Matches: "between <date1> and/to <date2>" or "from <date1> to <date2>"
        # Using non-greedy match for the first part to allow 'to' or 'and' to split roughly correct
        range_match = re.search(r"(between|from)\s+(.+?)\s+(and|to)\s+(.+)", text_lower)
        if range_match:
            date1 = range_match.group(2).strip()
            date2 = range_match.group(4).strip()
            
            # Basic cleanup if regex captured too much or trailing punctuation
            date1 = date1.rstrip(',').rstrip('.')
            date2 = date2.rstrip(',').rstrip('.')
            
            # Since regex is basic, let's verify if date1/date2 contain identifiers (avoid capturing them)
            if self._is_identifier(date1, identifiers) or self._is_identifier(date2, identifiers):
                pass # Fall through to other methods if identifier caught in crossfire
            else:
                valid_1 = self._is_valid_date(date1)
                valid_2 = self._is_valid_date(date2)

                if valid_1 and valid_2:
                    return {"time_horizon": f"From {date1} To {date2}", "validation_error": None}
                else:
                    invalid_d = date1 if not valid_1 else date2
                    return {"time_horizon": f"{date1} to {date2}", "validation_error": f"Invalid date detected: '{invalid_d}'. Please check input."}

        # 2. Matcher for "after X minutes"
        matches = self.matcher(doc)
        for _, start, end in matches:
            return {"time_horizon": doc[start:end].text, "validation_error": None}

        # 3. Single Date Extraction (Spacy)
        for ent in doc.ents:
            if ent.label_ == "DATE":
                candidate = ent.text
                
                if self._is_identifier(candidate, identifiers):
                    continue
                
                # Check for just a raw number that Spacy mistook for a year/date
                if re.match(r"^\d+$", candidate):
                    # Only allow 4 digit years
                    if len(candidate) != 4: 
                        continue

                if self._is_valid_date(candidate):
                     return {"time_horizon": candidate, "validation_error": None}
                else:
                     return {"time_horizon": candidate, "validation_error": f"Invalid date detected: '{candidate}'. Please check input."}
        
        return {"time_horizon": None, "validation_error": None}

    def _is_identifier(self, text: str, identifiers: Dict) -> bool:
        """Check if text matches any extracted identifier"""
        clean_text = text.lower().replace(" ", "")
        for key, val in identifiers.items():
            if val and val == clean_text:
                return True
            if val and val in clean_text:
                return True
        return False

    def _is_valid_date(self, date_str: str) -> bool:
        """Validate date string, handling ordinal suffixes and invalid numbers."""
        # 1. Remove ordinal suffixes (st, nd, rd, th) to help parsing
        # e.g. "august 71th" -> "august 71"
        clean_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)
        
        # 2. Heuristic Check: Are there any days > 31?
        # Extract all integer sequences
        numbers = re.findall(r"\d+", clean_str)
        for num in numbers:
            val = int(num)
            if val > 31:
                # Allow years: 19XX or 20XX or 21XX. length 4.
                if len(num) == 4 and (num.startswith("19") or num.startswith("20") or num.startswith("21")):
                    continue
                # If we have a number > 31 and it's NOT a year, it's likely an invalid day or identifier spam
                return False

        # 3. DateParser Attempt
        # Settings: strict parsing is hard, but we can assume English
        parsed = dateparser.parse(clean_str, settings={'STRICT_PARSING': False})
        return parsed is not None

    def _extract_identifiers(self, text_lower: str) -> Dict[str, Optional[str]]:
        identifiers = {"mmsi": None, "imo": None, "call_sign": None}

        # MMSI (9 digits)
        mmsi_match = re.search(r"\b\d{9}\b", text_lower)
        if mmsi_match:
            identifiers["mmsi"] = mmsi_match.group()

        # IMO
        imo_match = re.search(r"imo\s*\d+", text_lower)
        if imo_match:
             identifiers["imo"] = imo_match.group().replace("imo", "").strip()

        # Call Sign
        call_match = re.search(r"callsign\s+([a-z0-9]{3,7})", text_lower)
        if call_match:
            identifiers["call_sign"] = call_match.group(1).upper()
            
        return identifiers

model_service = ModelService()
