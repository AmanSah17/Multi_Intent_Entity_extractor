import pandas as pd
import dateparser
from typing import List, Dict, Optional
from datetime import datetime

PARQUET_FILE = "/home/crimsondeepdarshak/Desktop/Deep_Darshak/AIS_data_demo/processed/10_Day_US_interpolated_15min.parquet"

class DataService:
    def __init__(self):
        self.df = None
        self._load_data()

    def _load_data(self):
        try:
            print(f"Loading Parquet data from {PARQUET_FILE}...")
            self.df = pd.read_parquet(PARQUET_FILE)
            # Ensure BASEDATETIME is datetime
            self.df['BASEDATETIME'] = pd.to_datetime(self.df['BASEDATETIME'])
            print(f"Data loaded. Rows: {len(self.df)}")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()

    def fetch_vessel_data(self, mmsi: str, time_horizon: str) -> List[Dict]:
        """
        Fetches data for a given MMSI within the time horizon.
        parses 'From X To Y' or 'Between X and Y' or single dates.
        """
        if self.df.empty:
            return []

        try:
            mmsi_int = int(mmsi)
        except ValueError:
            print(f"Invalid MMSI: {mmsi}")
            return []

        # 1. Parse Time Horizon to Start/End timestamps
        start_dt, end_dt = self._parse_time_range(time_horizon)
        
        if not start_dt or not end_dt:
            print(f"Could not parse time range from: {time_horizon}")
            return []

        print(f"Querying Data: MMSI={mmsi_int}, Start={start_dt}, End={end_dt}")

        # 2. Filter DataFrame
        mask = (
            (self.df['MMSI'] == mmsi_int) &
            (self.df['BASEDATETIME'] >= start_dt) &
            (self.df['BASEDATETIME'] <= end_dt)
        )
        
        subset = self.df.loc[mask].sort_values('BASEDATETIME')
        
        # 3. Convert to List of Dicts
        records = []
        for _, row in subset.iterrows():
            records.append({
                "timestamp": row['BASEDATETIME'].strftime('%Y-%m-%d %H:%M:%S'),
                "lat": float(row['LAT']),
                "lon": float(row['LON']),
                "sog": float(row['SOG']),
                "cog": float(row['COG'])
            })
            
        return records

    def _parse_time_range(self, time_str: str) -> (Optional[datetime], Optional[datetime]):
        if not time_str:
            return None, None
            
        # Clean string
        clean = time_str.lower().replace("from", "").replace("between", "").replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
        
        # Split by 'to' or 'and'
        parts = []
        if "to" in clean:
            parts = clean.split("to")
        elif "and" in clean:
            parts = clean.split("and")
            
        if len(parts) == 2:
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            
            start_dt = dateparser.parse(start_str)
            end_dt = dateparser.parse(end_str)
            
            # If end date has no time, assume end of day? 
            # ideally dateparser handles this, but let's just return what we get.
            # If user says "Jan 15th", typically implies the whole day up to 23:59:59 if inclusive?
            # For now, simplistic parsing.
            if end_dt and end_dt.hour == 0 and end_dt.minute == 0:
                 # Set to end of day
                 end_dt = end_dt.replace(hour=23, minute=59, second=59)

            return start_dt, end_dt
            
        # Handle single date? "On January 3rd" -> Whole day
        single_dt = dateparser.parse(clean)
        if single_dt:
             start_dt = single_dt.replace(hour=0, minute=0, second=0)
             end_dt = single_dt.replace(hour=23, minute=59, second=59)
             return start_dt, end_dt

        return None, None

data_service = DataService()
