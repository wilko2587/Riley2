# File: tests/mocks/calendar_agent_mock.py

from datetime import datetime, timedelta
from riley2.core.logger_utils import logger
from tests.config import TestConfigLoader

class CalendarAgentMock:
    """
    CalendarAgentMock
    -----------------
    This mock simulates the behavior of the real CalendarAgent interfacing with Google Calendar API.
    Now using the TestConfigLoader to load events from JSON configuration.
    """
    
    def __init__(self):
        """Initialize with events from test configuration"""
        try:
            # Load events from configuration
            self.events = self._convert_config_events(TestConfigLoader.get_calendar_events())
            logger.debug(f"Initialized CalendarAgentMock with {len(self.events)} events from config")
        except Exception as e:
            logger.error(f"Failed to load calendar config: {e}")
            # Fallback to default events if config loading fails
            logger.warning("Using fallback calendar events")
            self.events = [
                {"title": "Dinner with Friends", "date": "2025/04/26"},
                {"title": "Work Conference", "date": "2025/05/05"},
                {"title": "Board Game Night", "date": "2025/05/12"},
                {"title": "Holiday Italy", "date": "2025/05/15"}
            ]
    
    def _convert_config_events(self, config_events):
        """Convert events from config format to internal format"""
        # The config format already matches our internal format
        return config_events
    
    def calendar_scan(self, start_date, end_date, query=None):
        """
        Scans the calendar for events between the start and end dates that match the query.
        Uses the exact same interface and return format as the real calendar_scan function.
        
        Args:
            start_date (str): Start date in "YYYY/MM/DD" format
            end_date (str): End date in "YYYY/MM/DD" format
            query (str, optional): Text to search for in event titles
            
        Returns:
            str: Formatted string with matching events or "No matching events found."
        """
        logger.debug(f"Mock: Scanning calendar from {start_date} to {end_date} with query: {query}")
        
        # Use the config loader's helper function to get events in date range
        events = TestConfigLoader.get_calendar_events_by_date_range(start_date, end_date)
        
        if query:
            # Filter by query
            query = query.lower()
            matched = []
            for event in events:
                if query in event["title"].lower():
                    matched.append(event)
        else:
            matched = events
                    
        logger.info(f"Mock: Found {len(matched)} calendar events matching criteria")
        
        if not matched:
            return "No matching events found."

        return f"Found events: {matched}"
    
    # Keep legacy methods for backward compatibility with existing tests
    def get_events_for_month(self, year: int, month: int):
        """Legacy method - Searches the configured events for the given month"""
        start_date = f"{year}/{month:02d}/01"
        # Calculate the last day of the month
        if month == 12:
            next_month_year = year + 1
            next_month = 1
        else:
            next_month_year = year
            next_month = month + 1
            
        # Get the first day of next month and subtract one day
        next_month_start = datetime(next_month_year, next_month, 1)
        last_day = (next_month_start - timedelta(days=1)).day
        end_date = f"{year}/{month:02d}/{last_day}"
        
        # Get events in this date range
        events = TestConfigLoader.get_calendar_events_by_date_range(start_date, end_date)
        
        # Convert to old format for backward compatibility
        monthly_events = []
        for event in events:
            old_format = {
                "summary": event["title"],
                "start": {"date": event["date"].replace("/", "-")},
                "end": {"date": event.get("end_date", event["date"]).replace("/", "-")}
            }
            monthly_events.append(old_format)
            
        return monthly_events

    def get_events_for_day(self, year: int, month: int, day: int):
        """Legacy method - Searches events for the specific day"""
        target_date = f"{year}/{month:02d}/{day:02d}"
        events = TestConfigLoader.get_calendar_events_by_date_range(target_date, target_date)
        
        # Convert to old format
        daily_events = []
        for event in events:
            old_format = {
                "summary": event["title"],
                "start": {"date": event["date"].replace("/", "-")},
                "end": {"date": event.get("end_date", event["date"]).replace("/", "-")}
            }
            daily_events.append(old_format)
            
        return daily_events

    def __getattr__(self, item):
        raise AttributeError(f"CalendarAgentMock does not implement method: {item}")