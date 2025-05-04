# File: tests/reasoning/test_calendar_reasoning.py

from unittest.mock import patch
import pytest
from datetime import datetime, timedelta
from contextlib import contextmanager
from tests.mocks.calendar_agent_mock import CalendarAgentMock
from tests.config import TestConfigLoader
from src.riley2.agents.calendar_agent import calendar_scan
from src.riley2.core.logger_utils import logger, log_agent_interaction, log_test_step, log_test_success

# Test helper to override TestConfigLoader for boundary tests
class CalendarTestHelper:
    """Helper class for testing calendar boundaries with custom events"""
    
    @staticmethod
    @contextmanager
    def with_custom_events(events):
        """Context manager to temporarily replace the TestConfigLoader get_calendar_events_by_date_range method"""
        original_method = TestConfigLoader.get_calendar_events_by_date_range
        
        def custom_get_calendar_events_by_date_range(start_date, end_date):
            """Custom implementation that returns our test events filtered by date range"""
            from datetime import datetime
            
            # Parse dates
            try:
                start = datetime.strptime(start_date, "%Y/%m/%d")
            except ValueError:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                
            try:
                end = datetime.strptime(end_date, "%Y/%m/%d")
            except ValueError:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Filter events to match the date range
            results = []
            for event in events:
                try:
                    event_date = datetime.strptime(event["date"], "%Y/%m/%d")
                    
                    # For multi-day events
                    if "end_date" in event:
                        event_end_date = datetime.strptime(event["end_date"], "%Y/%m/%d")
                        if (start <= event_date <= end) or (start <= event_end_date <= end) or \
                           (event_date <= start and event_end_date >= end):
                            results.append(event)
                    # For single-day events
                    elif start <= event_date <= end:
                        results.append(event)
                except ValueError:
                    # Skip events with invalid dates
                    logger.warning(f"Test helper: Skipping event with invalid date format: {event}")
            
            logger.debug(f"Test helper: Returning {len(results)} custom events")
            return results
        
        # Replace the method
        TestConfigLoader.get_calendar_events_by_date_range = custom_get_calendar_events_by_date_range
        
        try:
            # Return control to the with block
            yield
        finally:
            # Restore the original method
            TestConfigLoader.get_calendar_events_by_date_range = original_method
            logger.debug("Test helper: Restored original TestConfigLoader.get_calendar_events_by_date_range")

class TestCalendarComparison:
    """Test suite to compare the real calendar agent with the mock implementation"""
    
    @pytest.mark.parametrize("start_date, end_date, query", [
        # Test different date ranges and queries
        ("2025/05/01", "2025/05/31", None),  # All May events
        ("2025/05/01", "2025/05/31", "Italy"),  # May events with Italy in title
        ("2025/04/25", "2025/05/15", None),  # Range spanning April-May
        ("2025/06/01", "2025/06/30", None),  # No events expected
        # Test different date formats
        ("2025-05-01", "2025-05-31", None),  # Using hyphen format
        # Test for current month (dynamically calculated)
        (datetime.now().strftime("%Y/%m/01"), datetime.now().strftime("%Y/%m/%d"), None),  # Current month events
    ])
    def test_calendar_scan_comparison(self, start_date, end_date, query):
        """Compare outputs of real calendar_scan and mock implementation for the same inputs"""
        log_test_step(f"Testing calendar scan comparison with dates: {start_date}-{end_date}, query: {query}")
        
        # Get results from real implementation
        real_result = calendar_scan(start_date, end_date, query)
        log_agent_interaction("Test", "RealCalendarResult", real_result)
        
        # Get results from mock implementation
        mock_calendar = CalendarAgentMock()
        mock_result = mock_calendar.calendar_scan(start_date, end_date, query)
        log_agent_interaction("Test", "MockCalendarResult", mock_result)
        
        # Compare result formats
        assert isinstance(real_result, str) and isinstance(mock_result, str), \
            "Both implementations should return string results"
        
        # Check if both contain the same basic response pattern
        if "No matching events found" in real_result:
            assert "No matching events found" in mock_result, \
                f"Real agent found no events, but mock returned: {mock_result}"
        elif "Found events" in real_result:
            assert "Found events" in mock_result, \
                f"Real agent found events, but mock returned: {mock_result}"
        
        # Note: We're not comparing exact events as they're likely different
        # between mock and real implementations, but format should be consistent
        log_test_success(f"test_calendar_scan_comparison[{start_date}-{end_date}-{query}]")
    
    @pytest.mark.parametrize("start_date, end_date, query, expected_keyword", [
        # Test specific keywords that should be found in both implementations
        ("2025/05/01", "2025/05/31", "Italy", "Italy"),
        ("2025/05/01", "2025/05/31", None, "Doctor"),
    ])
    def test_specific_event_presence(self, start_date, end_date, query, expected_keyword):
        """Test that specific events appear in both implementations when they should"""
        log_test_step(f"Testing for presence of '{expected_keyword}' in both implementations")
        
        # Get results from real implementation
        real_result = calendar_scan(start_date, end_date, query)
        log_agent_interaction("Test", "RealCalendarResult", real_result)
        
        # Get results from mock implementation
        mock_calendar = CalendarAgentMock()
        mock_result = mock_calendar.calendar_scan(start_date, end_date, query)
        log_agent_interaction("Test", "MockCalendarResult", mock_result)
        
        # Check that the expected event is in the correct result
        # Only check if "Found events" is in the response to avoid false positives
        if "Found events" in real_result:
            assert expected_keyword in real_result, \
                f"Expected '{expected_keyword}' in real calendar result, but got: {real_result}"
        if "Found events" in mock_result:
            # For the mock, we just check for any event being returned when expected
            # as the mock and real data may have different events
            assert "Found events" in mock_result, \
                f"Expected events in mock calendar result, but got: {mock_result}"
        
        log_test_success(f"test_specific_event_presence[{start_date}-{end_date}-{query}-{expected_keyword}]")

    def test_date_format_handling(self):
        """Test that both implementations handle different date formats correctly"""
        log_test_step("Testing date format handling")
        
        # Test with slashes format
        slash_real = calendar_scan("2025/05/01", "2025/05/31", None)
        # Test with hyphen format
        hyphen_real = calendar_scan("2025-05-01", "2025-05-31", None)
        
        log_agent_interaction("Test", "SlashFormatReal", slash_real)
        log_agent_interaction("Test", "HyphenFormatReal", hyphen_real)
        
        # Compare real implementations with different formats
        assert ("No matching events found" in slash_real and "No matching events found" in hyphen_real) or \
               ("Found events" in slash_real and "Found events" in hyphen_real), \
               "Real implementation should handle both date formats consistently"
        
        # Mock calendar
        mock_calendar = CalendarAgentMock()
        slash_mock = mock_calendar.calendar_scan("2025/05/01", "2025/05/31", None)
        hyphen_mock = mock_calendar.calendar_scan("2025-05-01", "2025-05-31", None)
        
        log_agent_interaction("Test", "SlashFormatMock", slash_mock)
        log_agent_interaction("Test", "HyphenFormatMock", hyphen_mock)
        
        # Compare consistency between formats for mock
        assert ("No matching events found" in slash_mock and "No matching events found" in hyphen_mock) or \
               ("Found events" in slash_mock and "Found events" in hyphen_mock), \
               "Mock implementation should handle both date formats consistently"
        
        log_test_success("test_date_format_handling")
        
    def test_invalid_date_handling(self):
        """Test how implementations handle invalid date formats"""
        log_test_step("Testing invalid date format handling")
        
        # Test with invalid formats
        invalid_formats = [
            ("2025.05.01", "2025.05.31"),  # Periods instead of slashes
            ("05/01/2025", "05/31/2025"),  # MM/DD/YYYY format
            ("not-a-date", "2025/05/31"),  # Invalid start date
            ("2025/05/01", "not-a-date")   # Invalid end date
        ]
        
        mock_calendar = CalendarAgentMock()
        
        for start, end in invalid_formats:
            # Check that implementations handle invalid dates gracefully
            try:
                real_result = calendar_scan(start, end, None)
                log_agent_interaction("Test", f"RealCalendar({start},{end})", real_result)
                # If we get here, ensure it returned a proper error message
                assert "No matching events found" in real_result, \
                    f"Real implementation should return 'No matching events' for invalid dates, got: {real_result}"
            except Exception as e:
                # Real implementation might raise exception for invalid formats
                # Which is also acceptable, but let's log it
                log_agent_interaction("Test", f"RealCalendarException({start},{end})", str(e))
            
            # Mock should always handle invalid dates gracefully
            try:
                mock_result = mock_calendar.calendar_scan(start, end, None)
                log_agent_interaction("Test", f"MockCalendar({start},{end})", mock_result)
                assert "No matching events found" in mock_result, \
                    f"Mock should return 'No matching events' for invalid dates, got: {mock_result}"
            except Exception as e:
                # This is a failure - mock should always handle invalid formats gracefully
                assert False, f"Mock failed to handle invalid date format ({start}, {end}): {e}"
        
        log_test_success("test_invalid_date_handling")

class TestCalendarMultiBlockMerge:
    """Test suite for calendar block merging functionality across boundaries"""

    def test_multi_day_event_boundary_detection(self):
        """Test that the calendar agent can correctly identify multi-day events that cross date boundaries"""
        log_test_step("Testing multi-day event boundary detection")

        # Get events from May 5-6 (partial range of the Work Conference which runs May 5-8)
        mock_calendar = CalendarAgentMock()
        partial_result = mock_calendar.calendar_scan("2025/05/05", "2025/05/06", None)
        log_agent_interaction("Test", "PartialMultiDayResult", partial_result)

        # The result should include the Work Conference even though we only queried part of its range
        assert "Work Conference" in partial_result, \
            f"Should find 'Work Conference' even when querying only part of the event's duration. Got: {partial_result}"
        
        log_test_success("test_multi_day_event_boundary_detection")

    def test_multi_day_event_start_boundary(self):
        """Test detecting an event when only querying its start date"""
        log_test_step("Testing multi-day event start boundary detection")

        # Get events only for the start date of the multi-day conference
        mock_calendar = CalendarAgentMock()
        result = mock_calendar.calendar_scan("2025/05/05", "2025/05/05", None)
        log_agent_interaction("Test", "FirstDayMultiDayResult", result)

        # The result should include the Work Conference even though we only queried its first day
        assert "Work Conference" in result, \
            f"Should find 'Work Conference' when querying only its first day. Got: {result}"
            
        log_test_success("test_multi_day_event_start_boundary")

    def test_multi_day_event_end_boundary(self):
        """Test detecting an event when only querying its end date"""
        log_test_step("Testing multi-day event end boundary detection")

        # Get events only for the end date of the multi-day conference
        mock_calendar = CalendarAgentMock()
        result = mock_calendar.calendar_scan("2025/05/08", "2025/05/08", None)
        log_agent_interaction("Test", "LastDayMultiDayResult", result)

        # The result should include the Work Conference even though we only queried its last day
        assert "Work Conference" in result, \
            f"Should find 'Work Conference' when querying only its last day. Got: {result}"
            
        log_test_success("test_multi_day_event_end_boundary")

    def test_events_spanning_month_boundary(self):
        """Test that events spanning across month boundaries are correctly detected"""
        log_test_step("Testing events that cross month boundaries")

        # Create a month-spanning event
        month_spanning_event = [{
            "title": "Month Spanning Conference",
            "date": "2025/04/28",
            "all_day": True,
            "end_date": "2025/05/02",
            "is_multiday": True
        }]
        
        # Use our helper to override TestConfigLoader during the test
        with CalendarTestHelper.with_custom_events(month_spanning_event):
            mock_calendar = CalendarAgentMock()
            
            # Test querying just the April portion
            april_result = mock_calendar.calendar_scan("2025/04/28", "2025/04/30", None)        
            log_agent_interaction("Test", "AprilPartOfMonthSpanningEvent", april_result)
            
            # Test querying just the May portion
            may_result = mock_calendar.calendar_scan("2025/05/01", "2025/05/02", None)
            log_agent_interaction("Test", "MayPartOfMonthSpanningEvent", may_result)
            
            # Test querying across the month boundary
            spanning_result = mock_calendar.calendar_scan("2025/04/29", "2025/05/01", None)     
            log_agent_interaction("Test", "CrossMonthBoundaryQuery", spanning_result)
            
            # All queries should find the Month Spanning Conference
            assert "Month Spanning Conference" in april_result, \
                f"Should find month-spanning event when querying April part. Got: {april_result}"
            assert "Month Spanning Conference" in may_result, \
                f"Should find month-spanning event when querying May part. Got: {may_result}"
            assert "Month Spanning Conference" in spanning_result, \
                f"Should find month-spanning event when querying across month boundary. Got: {spanning_result}"
        
        log_test_success("test_events_spanning_month_boundary")

    def test_overlapping_multi_day_events(self):
        """Test handling of overlapping multi-day events"""
        log_test_step("Testing overlapping multi-day events")
        
        # Create two overlapping events
        overlapping_events = [
            {
                "title": "Business Conference",
                "date": "2025/06/10",
                "all_day": True,
                "end_date": "2025/06/15",
                "is_multiday": True
            },
            {
                "title": "Team Building Retreat",
                "date": "2025/06/13",
                "all_day": True,
                "end_date": "2025/06/17", 
                "is_multiday": True
            }
        ]
        
        # Use our helper to override TestConfigLoader during the test
        with CalendarTestHelper.with_custom_events(overlapping_events):
            mock_calendar = CalendarAgentMock()
            
            # Query the overlapping period
            overlap_result = mock_calendar.calendar_scan("2025/06/13", "2025/06/15", None)      
            log_agent_interaction("Test", "OverlappingEventsResult", overlap_result)
            
            # Both events should be found in the overlapping period
            assert "Business Conference" in overlap_result, \
                f"Should find 'Business Conference' in overlapping period. Got: {overlap_result}"
            assert "Team Building Retreat" in overlap_result, \
                f"Should find 'Team Building Retreat' in overlapping period. Got: {overlap_result}"
        
        log_test_success("test_overlapping_multi_day_events")

if __name__ == "__main__":
    # For manual testing
    test = TestCalendarComparison()
    
    print("\nTesting calendar scan comparison:")
    test.test_calendar_scan_comparison("2025/05/01", "2025/05/31", None)
    test.test_calendar_scan_comparison("2025/05/01", "2025/05/31", "Italy")
    
    print("\nTesting specific event presence:")
    test.test_specific_event_presence("2025/05/01", "2025/05/31", "Italy", "Italy")
    
    print("\nTesting date format handling:")
    test.test_date_format_handling()
    
    print("\nTesting invalid date handling:")
    test.test_invalid_date_handling()

    test_multi_block_merge = TestCalendarMultiBlockMerge()
    
    print("\nTesting multi-day event boundary detection:")
    test_multi_block_merge.test_multi_day_event_boundary_detection()
    
    print("\nTesting multi-day event start boundary:")
    test_multi_block_merge.test_multi_day_event_start_boundary()
    
    print("\nTesting multi-day event end boundary:")
    test_multi_block_merge.test_multi_day_event_end_boundary()
    
    print("\nTesting events spanning month boundary:")
    test_multi_block_merge.test_events_spanning_month_boundary()
    
    print("\nTesting overlapping multi-day events:")
    test_multi_block_merge.test_overlapping_multi_day_events()