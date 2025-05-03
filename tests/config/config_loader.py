"""
Test Configuration Loader

This module provides utilities for loading test configuration files for mocks.
It simplifies access to test data and ensures consistent behavior across tests.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger("riley2")

class TestConfigLoader:
    """Utility class for loading test configuration data"""
    
    # Base directory for test configurations
    BASE_CONFIG_DIR = Path(__file__).parent
    MOCK_CONFIG_DIR = BASE_CONFIG_DIR / "mocks"
    
    @classmethod
    def load_config(cls, config_name: str) -> Dict[str, Any]:
        """
        Load a configuration file by name (without .json extension)
        
        Args:
            config_name: Name of the config file without extension
            
        Returns:
            Dict containing the configuration data
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        file_path = cls.MOCK_CONFIG_DIR / f"{config_name}.json"
        
        if not file_path.exists():
            logger.error(f"Test configuration not found: {file_path}")
            raise FileNotFoundError(f"Test configuration '{config_name}.json' not found")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                logger.debug(f"Loaded test configuration from {file_path}")
                return config_data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in test configuration: {file_path}: {e}")
            raise
    
    @classmethod
    def get_calendar_events(cls) -> List[Dict[str, Any]]:
        """Load and return calendar events for testing"""
        config = cls.load_config("calendar_events")
        return config.get("events", [])
    
    @classmethod
    def get_emails_by_date(cls) -> Dict[str, List[Dict[str, Any]]]:
        """Load and return emails organized by date"""
        config = cls.load_config("email_data")
        return config.get("emails", {})
    
    @classmethod
    def get_knowledge_base(cls) -> List[Dict[str, Any]]:
        """Load and return knowledge base entries for testing"""
        config = cls.load_config("knowledge_base")
        return config.get("entries", [])
    
    @classmethod
    def get_email_by_query(cls, query: str, date_range: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search emails based on query and optional date range
        
        Args:
            query: Search term to look for in email fields
            date_range: Optional list of [start_date, end_date] in format "YYYY/MM/DD"
            
        Returns:
            List of matching email dictionaries
        """
        all_emails_by_date = cls.get_emails_by_date()
        results = []
        
        # Handle date filtering
        if date_range and len(date_range) == 2:
            from datetime import datetime
            start_date = datetime.strptime(date_range[0], "%Y/%m/%d")
            end_date = datetime.strptime(date_range[1], "%Y/%m/%d")
            
            # Filter dates in range
            filtered_dates = {}
            for date_str, emails in all_emails_by_date.items():
                curr_date = datetime.strptime(date_str, "%Y/%m/%d")
                if start_date <= curr_date <= end_date:
                    filtered_dates[date_str] = emails
            
            all_emails_by_date = filtered_dates
        
        # Extract all emails from the date dictionary
        all_emails = []
        for date_str, emails in all_emails_by_date.items():
            for email in emails:
                email_with_date = email.copy()
                email_with_date["date"] = date_str
                all_emails.append(email_with_date)
        
        # Filter by query
        query = query.lower()
        for email in all_emails:
            if (query in email.get("subject", "").lower() or 
                query in email.get("sender", "").lower() or 
                query in email.get("body", "").lower() or
                query in email.get("snippet", "").lower()):
                results.append(email)
        
        return results
    
    @classmethod
    def get_calendar_events_by_date_range(cls, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Get calendar events within a date range
        
        Args:
            start_date: Start date in format "YYYY/MM/DD" or "YYYY-MM-DD"
            end_date: End date in format "YYYY/MM/DD" or "YYYY-MM-DD"
            
        Returns:
            List of calendar events in the specified range
        """
        from datetime import datetime
        
        all_events = cls.get_calendar_events()
        
        # Handle both date formats (YYYY/MM/DD and YYYY-MM-DD)
        try:
            start = datetime.strptime(start_date, "%Y/%m/%d")
        except ValueError:
            # Try alternate format with hyphens
            start = datetime.strptime(start_date, "%Y-%m-%d")
        
        try:
            end = datetime.strptime(end_date, "%Y/%m/%d")
        except ValueError:
            # Try alternate format with hyphens
            end = datetime.strptime(end_date, "%Y-%m-%d")
        
        results = []
        for event in all_events:
            event_date = datetime.strptime(event["date"], "%Y/%m/%d")
            
            # Handle multi-day events
            if event.get("all_day", False) and event.get("end_date"):
                event_end_date = datetime.strptime(event["end_date"], "%Y/%m/%d")
                if (start <= event_date <= end) or (start <= event_end_date <= end) or \
                   (event_date <= start and event_end_date >= end):
                    results.append(event)
            # Handle single-day events
            elif start <= event_date <= end:
                results.append(event)
                
        return results

# Initialize with default configurations
def initialize_test_configs():
    """Validate all test configurations on import"""
    try:
        TestConfigLoader.get_calendar_events()
        TestConfigLoader.get_emails_by_date()
        TestConfigLoader.get_knowledge_base()
        logger.info("Test configurations loaded and validated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize test configurations: {e}")
        return False

# Validate configs on module import
configs_valid = initialize_test_configs()