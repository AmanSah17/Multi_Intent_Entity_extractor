

import spacy
from spacy.matcher import Matcher
import re
from typing import List, Dict, Optional


"""
nlp_interpreter.py
-------------------
Lightweight NLP Interpreter using spaCy for intent and entity extraction
for maritime vessel monitoring queries.

Example:
    "Show the last known position of INS Kolkata."
    "Predict where MSC Flaminia will be after 30 minutes."
"""

class MaritimeNLPInterpreter:
    """
    A class to interpret natural language queries related to maritime vessel data.
    Extracts:
        - Intent (SHOW / PREDICT / VERIFY)
        - Vessel name
        - Time horizon (e.g., 'after 30 minutes')
        - Optional identifiers (MMSI, CallSign, IMO)
    """

    def __init__(self, vessel_list: Optional[List[str]] = None):
        """
        Initialize NLP model and rule patterns.
        Args:
            vessel_list (List[str]): Known vessel names from the database.
        """
        self.vessel_list = [v.lower() for v in vessel_list] if vessel_list else []
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)
        self._register_patterns()

        # Intent keyword mapping
        self.intent_keywords = {
            "show": ["show", "display", "find", "locate", "fetch", "retrieve"],
            "predict": ["predict", "forecast", "estimate", "project"],
            "verify": ["check", "validate", "verify", "compare", "confirm"],
        }

    def _register_patterns(self):
        """Register pattern rules for time expressions, MMSI, etc."""
        # Time horizon pattern
        pattern_time = [
            {"LOWER": {"IN": ["after", "in"]}},
            {"IS_DIGIT": True},
            {"LOWER": {"IN": ["minutes", "minute", "hours", "hour"]}},
        ]
        self.matcher.add("TIME_HORIZON", [pattern_time])

    # ---------------- CORE METHOD ---------------- #
    def parse_query(self, text: str) -> Dict[str, Optional[str]]:
        """
        Parse the given text and extract structured intent and entities.

        Args:
            text (str): Natural language query from user.

        Returns:
            dict: Structured info with intent, vessel_name, time_horizon, identifiers.
        """
        doc = self.nlp(text.lower())
        text_lower = text.lower()

        return {
            "intent": self._extract_intent(text_lower),
            "vessel_name": self._extract_vessel_name(text_lower),
            "time_horizon": self._extract_time_horizon(doc),
            "identifiers": self._extract_identifiers(text_lower),
        }

    # ---------------- SUBCOMPONENTS ---------------- #
    def _extract_intent(self, text_lower: str) -> Optional[str]:
        """Detect the user's intent using keyword mapping."""
        for intent, words in self.intent_keywords.items():
            if any(word in text_lower for word in words):
                return intent.upper()
        return None

    def _extract_vessel_name(self, text_lower: str) -> Optional[str]:
        """Find a vessel name by matching against known vessel list."""
        for vessel in self.vessel_list:
            if vessel in text_lower:
                # Return the properly capitalized name
                return next(v for v in self.vessel_list if v == vessel)
        return None

    def _extract_time_horizon(self, doc) -> Optional[str]:
        """Find time-related expressions like 'after 30 minutes'."""
        matches = self.matcher(doc)
        for _, start, end in matches:
            return doc[start:end].text
        return None

    def _extract_identifiers(self, text_lower: str) -> Dict[str, Optional[str]]:
        """
        Extract optional vessel identifiers such as MMSI, IMO, or CallSign.
        """
        identifiers = {}

        # MMSI (9-digit number)
        mmsi_match = re.search(r"\b\d{9}\b", text_lower)
        identifiers["mmsi"] = mmsi_match.group() if mmsi_match else None

        # IMO (starts with IMO, followed by digits)
        imo_match = re.search(r"imo\s*\d+", text_lower)
        identifiers["imo"] = (
            imo_match.group().replace("imo", "").strip() if imo_match else None
        )

        # CallSign (alphanumeric, 3–7 chars, preceded by 'callsign')
        call_match = re.search(r"callsign\s+([a-z0-9]{3,7})", text_lower)
        identifiers["call_sign"] = call_match.group(1).upper() if call_match else None

        return identifiers



        