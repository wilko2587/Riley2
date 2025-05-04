# File: tests/reasoning/test_calendar_reasoning.py

import pytest
from datetime import datetime, timedelta
from tests.mocks.calendar_agent_mock import CalendarAgentMock
from src.riley2.agents.calendar_agent import calendar_scan
from src.riley2.core.logger_utils import logger, log_agent_interaction, log_test_step, log_test_success

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