    
    # Parquet Schema (actual columns from the file)
    col_timestamp: str = "BaseDateTime"
    col_latitude: str = "LAT"
    col_longitude: str = "LON"
    col_mmsi: str = "MMSI"
    col_sog: str = "SOG"
    col_cog: str = "COG"
    col_interpolated: str = "interpolated"
    
    # Service Configuration
    max_conversation_history: int = 10
    default_result_limit: int = 50
    
    # Loitering Detection Parameters
    loitering_speed_threshold_knots: float = 2.0
    loitering_dwell_time_hours: float = 4.0
    coastal_distance_nm: float = 12.0  # Nautical miles
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
