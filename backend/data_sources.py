# backend/data_sources.py

"""
Unified Data Source Management
Handles multiple air quality APIs and data sources
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AirQualityDataSource(ABC):
    """Abstract base class for all air quality data sources"""
    
    @abstractmethod
    def get_station_data(self, region: str) -> List[Dict[str, Any]]:
        """Fetch station data for a specific region"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Return the name of this data source"""
        pass
    
    @abstractmethod
    def get_supported_regions(self) -> List[str]:
        """Return list of supported regions/cities"""
        pass

class WAQIDataSource(AirQualityDataSource):
    """World Air Quality Index data source"""
    
    def __init__(self):
        # Use relative imports for package structure
        try:
            # When run as module (uvicorn backend.main:app)
            from .waqi_stations import fetch_berlin_stations_detailed
        except ImportError:
            # Fallback for direct execution (development)
            from waqi_stations import fetch_berlin_stations_detailed
        self.fetch_function = fetch_berlin_stations_detailed
    
    def get_station_data(self, region: str = "berlin") -> List[Dict[str, Any]]:
        """Fetch WAQI station data"""
        try:
            if region.lower() != "berlin":
                logger.warning(f"WAQI source currently only supports Berlin, got: {region}")
                return []
            
            stations_data = self.fetch_function()
            return stations_data.get('features', [])
        except Exception as e:
            logger.error(f"WAQI data fetch failed: {e}")
            return []
    
    def get_source_name(self) -> str:
        return "waqi_api"
    
    def get_supported_regions(self) -> List[str]:
        return ["berlin"]

class OpenAQDataSource(AirQualityDataSource):
    """OpenAQ data source (placeholder for future implementation)"""
    
    def get_station_data(self, region: str) -> List[Dict[str, Any]]:
        """Fetch OpenAQ station data - TODO: Implement"""
        logger.info(f"OpenAQ source not yet implemented for region: {region}")
        return []
    
    def get_source_name(self) -> str:
        return "openaq_api"
    
    def get_supported_regions(self) -> List[str]:
        return []  # TODO: Add supported regions

class UmweltBundesamtDataSource(AirQualityDataSource):
    """German Umweltbundesamt data source (placeholder for future implementation)"""
    
    def get_station_data(self, region: str) -> List[Dict[str, Any]]:
        """Fetch UBA station data - TODO: Implement"""
        logger.info(f"UBA source not yet implemented for region: {region}")
        return []
    
    def get_source_name(self) -> str:
        return "uba_api"
    
    def get_supported_regions(self) -> List[str]:
        return []  # TODO: Add German cities

class DataSourceManager:
    """Manages multiple data sources and provides unified access"""
    
    def __init__(self):
        self.sources = {
            'waqi': WAQIDataSource(),
            'openaq': OpenAQDataSource(),
            'uba': UmweltBundesamtDataSource(),
        }
        self.active_sources = ['waqi']  # Currently active sources
    
    def get_available_sources(self) -> List[str]:
        """Get list of all available data sources"""
        return list(self.sources.keys())
    
    def get_active_sources(self) -> List[str]:
        """Get list of currently active data sources"""
        return self.active_sources
    
    def add_source(self, name: str, source: AirQualityDataSource):
        """Add a new data source"""
        self.sources[name] = source
        logger.info(f"Added data source: {name}")
    
    def activate_source(self, source_name: str):
        """Activate a data source"""
        if source_name in self.sources and source_name not in self.active_sources:
            self.active_sources.append(source_name)
            logger.info(f"Activated data source: {source_name}")
    
    def deactivate_source(self, source_name: str):
        """Deactivate a data source"""
        if source_name in self.active_sources:
            self.active_sources.remove(source_name)
            logger.info(f"Deactivated data source: {source_name}")
    
    def collect_all_data(self, region: str) -> Dict[str, List[Dict[str, Any]]]:
        """Collect data from all active sources for a region"""
        all_data = {}
        
        for source_name in self.active_sources:
            source = self.sources[source_name]
            if region.lower() in [r.lower() for r in source.get_supported_regions()]:
                try:
                    data = source.get_station_data(region)
                    all_data[source_name] = data
                    logger.info(f"Collected {len(data)} stations from {source_name}")
                except Exception as e:
                    logger.error(f"Failed to collect from {source_name}: {e}")
                    all_data[source_name] = []
            else:
                logger.debug(f"Source {source_name} doesn't support region {region}")
        
        return all_data

# Global instance
data_source_manager = DataSourceManager()

def get_data_source_manager() -> DataSourceManager:
    """Get the global data source manager instance"""
    return data_source_manager
