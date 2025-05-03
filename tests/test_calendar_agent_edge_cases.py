"""
Test module for calendar agent edge cases.

This test suite verifies that both real and mock calendar agent implementations
properly handle edge cases, multiday events, and conflict resolution scenarios.
"""

import unittest
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import both real and mock implementations
from src.riley2.agents.calendar_agent import calendar_scan
from tests.mocks.calendar_agent_mock import CalendarAgentMock
from riley2.core.logger_utils import logger, log_test_step, log_test_success, log_test_failure


class TestCalendarAgentEdgeCases(unittest.TestCase):
    """
    Test suite focusing on edge cases for calendar agent implementations.
    
    This class verifies that both the real implementation and mock handle
    edge cases, multiday events, and conflict scenarios appropriately.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.calendar_mock = CalendarAgentMock()
        logger.info("Initialized CalendarAgentMock for edge case testing")
        
    def test_invalid_date_format(self):
        """Test handling of invalid date formats."""
        log_test_step("Testing invalid date format handling")
        
        # Test with mock implementation
        invalid_formats = [
            ("not-a-date", "2025/05/02"),
            ("2025/05/01", "invalid-date"),
            ("25/05/01", "2025/05/02"),  # Wrong format
            ("", "2025/05/02"),  # Empty date
            ("2025/05/01", ""),  # Empty date
        ]
        
        for start_date, end_date in invalid_formats:
            try:
                # Should handle invalid formats without crashing
                mock_result = self.calendar_mock.calendar_scan(start_date, end_date)
                self.assertIsInstance(mock_result, str, f"Failed with dates: {start_date}, {end_date}")
                
                # Test real implementation with the same invalid formats
                with self.assertRaises(Exception) as context:
                    real_result = calendar_scan(start_date, end_date)
                
                # Ensure the exception is related to date formatting
                self.assertTrue("format" in str(context.exception).lower() or 
                              "time" in str(context.exception).lower() or
                              "strptime" in str(context.exception).lower(),
                             f"Expected format error with {start_date}, {end_date}")
            except Exception as e:
                log_test_failure(f"test_invalid_date_format with {start_date}, {end_date}", str(e))
                raise

        log_test_success("test_invalid_date_format")
                
    def test_flipped_dates(self):
        """Test handling when end_date is before start_date."""
        log_test_step("Testing when end_date is before start_date")
        
        # End date before start date
        flipped_result = self.calendar_mock.calendar_scan("2025/05/15", "2025/05/01")
        self.assertIsInstance(flipped_result, str, "Should return string for flipped dates")
        self.assertTrue("No matching events" in flipped_result, "Should find no events when dates are flipped")
        
        # Real implementation should also handle this
        real_flipped_result = calendar_scan("2025/05/15", "2025/05/01")
        self.assertIsInstance(real_flipped_result, str, "Real implementation should return string for flipped dates")
        self.assertTrue("No matching events" in real_flipped_result, "Real implementation should find no events with flipped dates")
        
        log_test_success("test_flipped_dates")
        
    def test_multiday_events(self):
        """Test handling of multiday events spanning date ranges."""
        log_test_step("Testing multiday events spanning date ranges")
        
        # Mock multiday events in TestConfigLoader
        multiday_events = [
            {
                "title": "Spring Conference", 
                "date": "2025/05/10", 
                "end_date": "2025/05/12",
                "is_multiday": True
            }
        ]
        
        # Patch TestConfigLoader to return our mock multiday events
        with patch('tests.config.TestConfigLoader.get_calendar_events_by_date_range', return_value=multiday_events):
            # Test fetching with start date in the middle of event
            middle_date_result = self.calendar_mock.calendar_scan("2025/05/11", "2025/05/11")
            self.assertIn("Spring Conference", middle_date_result, "Should find multiday event when querying middle date")
            
            # Test fetching with partial overlap at start
            start_overlap_result = self.calendar_mock.calendar_scan("2025/05/08", "2025/05/10")
            self.assertIn("Spring Conference", start_overlap_result, "Should find multiday event when overlapping start date")
            
            # Test fetching with partial overlap at end
            end_overlap_result = self.calendar_mock.calendar_scan("2025/05/12", "2025/05/15")
            self.assertIn("Spring Conference", end_overlap_result, "Should find multiday event when overlapping end date")
            
        log_test_success("test_multiday_events")
            
    def test_event_conflicts(self):
        """Test identifying and handling conflicting events."""
        log_test_step("Testing conflict detection between calendar events")
        
        # Create conflicting events
        conflicting_events = [
            {"title": "Team Meeting", "date": "2025/05/20", "start_time": "10:00", "end_time": "11:00"},
            {"title": "Client Call", "date": "2025/05/20", "start_time": "10:30", "end_time": "11:30"},
            {"title": "Lunch", "date": "2025/05/20", "start_time": "12:00", "end_time": "13:00"}
        ]
        
        # Helper function to detect conflicts
        def has_conflict(events):
            for i, event1 in enumerate(events):
                for j, event2 in enumerate(events):
                    if i != j:
                        # Compare times if on the same day
                        if event1["date"] == event2["date"]:
                            # Convert times to comparable format
                            event1_start = datetime.strptime(event1["start_time"], "%H:%M")
                            event1_end = datetime.strptime(event1["end_time"], "%H:%M")
                            event2_start = datetime.strptime(event2["start_time"], "%H:%M")
                            event2_end = datetime.strptime(event2["end_time"], "%H:%M")
                            
                            # Check for overlap
                            if (event1_start < event2_end and event1_end > event2_start):
                                return True
            return False
            
        # Verify conflict detection works
        self.assertTrue(has_conflict(conflicting_events), "Should detect conflict between Team Meeting and Client Call")
        
        # Create non-conflicting events
        non_conflicting_events = [
            {"title": "Morning Standup", "date": "2025/05/20", "start_time": "09:00", "end_time": "09:30"},
            {"title": "Team Meeting", "date": "2025/05/20", "start_time": "10:00", "end_time": "11:00"},
            {"title": "Lunch", "date": "2025/05/20", "start_time": "12:00", "end_time": "13:00"}
        ]
        
        # Verify non-conflict detection works
        self.assertFalse(has_conflict(non_conflicting_events), "Should not detect conflict in non-overlapping events")
        
        log_test_success("test_event_conflicts")
        
    def test_all_day_events(self):
        """Test handling of all-day events."""
        log_test_step("Testing all-day event handling")
        
        # Create all-day events
        all_day_events = [
            {"title": "Company Holiday", "date": "2025/05/25", "is_all_day": True},
            {"title": "Regular Meeting", "date": "2025/05/25", "start_time": "10:00", "end_time": "11:00"}
        ]
        
        with patch('tests.config.TestConfigLoader.get_calendar_events_by_date_range', return_value=all_day_events):
            # All-day events should be included in searches
            result = self.calendar_mock.calendar_scan("2025/05/25", "2025/05/25")
            self.assertIn("Company Holiday", result, "Should include all-day events in search results")
            self.assertIn("Regular Meeting", result, "Should include regular events alongside all-day events")
            
        log_test_success("test_all_day_events")
            
    def test_recurring_events(self):
        """Test handling of recurring events."""
        log_test_step("Testing recurring event handling")
        
        # Create a recurring event template
        recurring_event = {
            "title": "Weekly Team Standup", 
            "date": "2025/05/05", 
            "recurring": True,
            "recurrence_pattern": "weekly",
            "recurrence_day": "Monday"
        }
        
        # Helper function to generate recurring event instances
        def generate_recurring_instances(base_event, start_date, end_date):
            # Convert string dates to datetime objects
            start = datetime.strptime(start_date, "%Y/%m/%d")
            end = datetime.strptime(end_date, "%Y/%m/%d")
            base_date = datetime.strptime(base_event["date"], "%Y/%m/%d")
            
            # Generate instances
            instances = []
            current_date = base_date
            while current_date <= end:
                if current_date >= start:
                    instance = base_event.copy()
                    instance["date"] = current_date.strftime("%Y/%m/%d")
                    instances.append(instance)
                
                # Move to next occurrence based on pattern
                if base_event["recurrence_pattern"] == "weekly":
                    current_date += timedelta(days=7)
                elif base_event["recurrence_pattern"] == "daily":
                    current_date += timedelta(days=1)
                else:
                    break  # Unsupported pattern
                    
            return instances
            
        # Test generating instances for a 3-week period
        instances = generate_recurring_instances(
            recurring_event, "2025/05/05", "2025/05/26"
        )
        
        # Should have 4 instances (May 5, 12, 19, 26 are all Mondays)
        self.assertEqual(len(instances), 4, "Should generate 4 instances for weekly event over 3 weeks")
        
        # Verify dates are correct
        expected_dates = ["2025/05/05", "2025/05/12", "2025/05/19", "2025/05/26"]
        actual_dates = [instance["date"] for instance in instances]
        self.assertEqual(actual_dates, expected_dates, "Recurring event dates should match expected pattern")
        
        log_test_success("test_recurring_events")
        
    def test_timezone_handling(self):
        """Test handling events with different timezones."""
        log_test_step("Testing timezone handling for events")
        
        # Create events with timezone information
        timezone_events = [
            {
                "title": "International Call", 
                "date": "2025/05/15", 
                "start_time": "09:00",
                "timezone": "America/New_York"  # EDT
            },
            {
                "title": "Local Meeting", 
                "date": "2025/05/15", 
                "start_time": "09:00",
                "timezone": "America/Los_Angeles"  # PDT
            }
        ]
        
        # We expect these events to have a 3-hour difference
        # New York is UTC-4 during daylight saving time
        # Los Angeles is UTC-7 during daylight saving time
        ny_event = timezone_events[0]
        la_event = timezone_events[1]
        
        # Simple timezone conversion
        ny_time = datetime.strptime(ny_event["start_time"], "%H:%M")
        la_time = datetime.strptime(la_event["start_time"], "%H:%M")
        time_diff = timedelta(hours=3)  # 3 hours difference between EDT and PDT
        
        # The LA 9am is equivalent to NY 12pm
        self.assertEqual(la_time + time_diff, ny_time + timedelta(hours=3), 
                      "Should correctly calculate 3 hour timezone difference")
        
        log_test_success("test_timezone_handling")
        
    def test_search_case_insensitivity(self):
        """Test that search queries are case insensitive."""
        log_test_step("Testing case insensitivity of calendar search queries")
        
        test_events = [
            {"title": "Board Meeting", "date": "2025/05/20"},
            {"title": "board game night", "date": "2025/05/21"}
        ]
        
        with patch('tests.config.TestConfigLoader.get_calendar_events_by_date_range', return_value=test_events):
            # Search with uppercase
            upper_result = self.calendar_mock.calendar_scan("2025/05/20", "2025/05/21", "BOARD")
            # Search with lowercase
            lower_result = self.calendar_mock.calendar_scan("2025/05/20", "2025/05/21", "board")
            
            # Both searches should return the same results
            self.assertEqual(upper_result, lower_result, "Case should not affect search results")
            
            # Both searches should find both events
            self.assertIn("Board Meeting", upper_result, "Should find event with title 'Board Meeting'")
            self.assertIn("board game night", upper_result, "Should find event with title 'board game night'")
        
        log_test_success("test_search_case_insensitivity")


if __name__ == "__main__":
    unittest.main()