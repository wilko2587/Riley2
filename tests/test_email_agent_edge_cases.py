"""
Test module for email agent edge cases.

This test suite verifies that both real and mock email agent implementations
properly handle error conditions, edge cases, and malformed inputs.
"""

import unittest
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import socket
import requests

# Import both real and mock implementations
from src.riley2.agents.email_agent import (
    authenticate_gmail, 
    email_download_chunk, 
    email_filter_by_sender, 
    email_summarize_batch
)
from tests.mocks.email_agent_mock import EmailAgentMock
from riley2.core.logger_utils import logger


class TestEmailAgentEdgeCases(unittest.TestCase):
    """
    Test suite focusing on edge cases for email agent implementations.
    
    This class verifies that both the real implementation and mock handle
    edge cases, error conditions, and unexpected inputs appropriately.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.email_mock = EmailAgentMock()
        logger.info("Initialized EmailAgentMock for edge case testing")
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats."""
        logger.info("Testing invalid date format handling")
        
        # Test with mock implementation
        invalid_formats = [
            ("not-a-date", "2025/05/02"),
            ("2025/05/01", "invalid-date"),
            ("25/05/01", "2025/05/02"),  # Wrong format
            ("", "2025/05/02"),  # Empty date
            ("2025/05/01", ""),  # Empty date
            ("2025-05-01", "2025-05-02"),  # Dashes instead of slashes
        ]
        
        for start_date, end_date in invalid_formats:
            mock_result = self.email_mock.email_download_chunk(start_date, end_date)
            # Even with invalid formats, should return a string and not crash
            self.assertIsInstance(mock_result, str, f"Failed with dates: {start_date}, {end_date}")
            # Should likely indicate no emails found or error
            self.assertTrue("No emails found" in mock_result or "Error" in mock_result, 
                         f"Invalid date format should return error or no results: {mock_result}")
    
    def test_empty_email_batch(self):
        """Test handling of empty email batches."""
        logger.info("Testing empty email batch handling")
        
        # Empty emails for filter
        empty_result = self.email_mock.email_filter_by_sender("", "test@example.com")
        self.assertIsInstance(empty_result, str, "Should return string for empty input")
        self.assertTrue("No emails" in empty_result, "Should indicate no emails found")
        
        # Empty emails for summarize
        empty_summary = self.email_mock.email_summarize_batch("")
        self.assertIsInstance(empty_summary, str, "Should return string for empty summary input")
        
        # Test with real implementation with mock safeguards
        with patch('src.riley2.core.llm_backend.summarize_text', return_value="No emails to summarize"):
            real_empty_summary = email_summarize_batch("")
            self.assertIsInstance(real_empty_summary, str)
    
    def test_malformed_email_data(self):
        """Test handling of malformed email data."""
        logger.info("Testing malformed email data handling")
        
        # Test with completely malformed data
        malformed_data = "This is not an email format"
        filter_result = self.email_mock.email_filter_by_sender(malformed_data, "test@example.com")
        self.assertIsInstance(filter_result, str, "Should return string for malformed data")
        self.assertTrue("No emails" in filter_result, "Should indicate no emails found")
        
        # Test with partially malformed data (missing From field)
        partial_data = "Subject: Test\nBody text\n---\nFrom: valid@example.com\nSubject: Valid"
        filter_result = self.email_mock.email_filter_by_sender(partial_data, "valid@example.com")
        self.assertIsInstance(filter_result, str, "Should return string for partially malformed data")
        self.assertTrue("valid@example.com" in filter_result, "Should find valid part in partially malformed data")
    
    def test_special_characters_in_sender(self):
        """Test handling of special characters in sender email."""
        logger.info("Testing special characters in sender email")
        
        # Create emails with special characters in sender
        special_emails = (
            "From: test+plus@example.com\nSubject: Test Email\nBody\n\n"
            "---\n"
            "From: test.dot@example.com\nSubject: Another Email\nBody\n\n"
            "---\n"
            "From: \"Name, With Comma\" <comma@example.com>\nSubject: Email\nBody\n\n"
        )
        
        # Test filtering with special characters in sender
        plus_result = self.email_mock.email_filter_by_sender(special_emails, "test+plus@example.com")
        self.assertTrue("test+plus@example.com" in plus_result, "Should find email with plus sign")
        
        # Test filtering with dots
        dot_result = self.email_mock.email_filter_by_sender(special_emails, "test.dot@example.com")
        self.assertTrue("test.dot@example.com" in dot_result, "Should find email with dots")
        
        # Test filtering with name part containing commas
        comma_result = self.email_mock.email_filter_by_sender(special_emails, "comma@example.com")
        self.assertTrue("comma@example.com" in comma_result, "Should find email with comma in display name")
    
    def test_case_insensitive_filtering(self):
        """Test that email filtering is case insensitive."""
        logger.info("Testing case insensitive email filtering")
        
        # Create sample emails
        sample_emails = (
            "From: Test@Example.com\nSubject: Test Email\nBody\n\n"
            "---\n"
            "From: another@example.com\nSubject: Another Email\nBody\n\n"
        )
        
        # Test filtering with different case
        upper_result = self.email_mock.email_filter_by_sender(sample_emails, "TEST@EXAMPLE.COM")
        self.assertTrue("Test@Example.com" in upper_result, "Should find email with case insensitive matching")
        
        # Test with real implementation
        lower_result = email_filter_by_sender(sample_emails, "test@example.com")
        self.assertTrue("Test@Example.com" in lower_result, "Real implementation should handle case insensitive matching")
    
    def test_boundary_dates(self):
        """Test handling of boundary dates."""
        logger.info("Testing boundary dates")
        
        # Test with same date for start and end
        same_date = "2025/05/01"
        same_date_result = self.email_mock.email_download_chunk(same_date, same_date)
        self.assertIsInstance(same_date_result, str, "Should return string for same start/end date")
        
        # Test with end date before start date
        reversed_dates_result = self.email_mock.email_download_chunk("2025/05/02", "2025/05/01")
        self.assertIsInstance(reversed_dates_result, str, "Should return string for reversed dates")
        self.assertTrue("No emails found" in reversed_dates_result or len(reversed_dates_result) == 0, 
                     "Should handle reversed dates gracefully")
    
    def test_authentication_error_handling(self):
        """Test handling of authentication errors."""
        logger.info("Testing authentication error handling")
        
        # We can only test this with mock implementation when using direct patch
        with patch('tests.mocks.email_agent_mock.EmailAgentMock.email_download_chunk', 
                  side_effect=Exception('Mock authentication error')):
            try:
                result = self.email_mock.email_download_chunk("2025/05/01", "2025/05/02")
                self.fail("Should have raised an exception")
            except Exception as e:
                # We expect the exception to be raised in this test
                self.assertIn("authentication error", str(e).lower())
        
        # For the real implementation, we need to patch and verify it catches the error
        with patch('src.riley2.agents.email_agent.authenticate_gmail',
                  side_effect=Exception('Mock authentication error')):
            try:
                result = email_download_chunk("2025/05/01", "2025/05/02")
                # If no exception is raised, verify it returned an error message as string
                self.assertIsInstance(result, str)
                self.assertIn("Error", result)
            except Exception as e:
                # If it still raises an exception, we should improve the real implementation
                # But for now, let's just pass the test
                self.fail(f"Should catch authentication errors gracefully: {e}")
    
    def test_network_error_handling(self):
        """Test handling of network errors like connection failures."""
        logger.info("Testing network error handling")
        
        # Test handling of connection failures in email_download_chunk
        with patch('src.riley2.agents.email_agent.build', side_effect=socket.timeout('Connection timed out')):
            result = email_download_chunk("2025/05/01", "2025/05/02")
            self.assertIsInstance(result, str, "Should return error string for network timeout")
            self.assertTrue("Error" in result or "Failed" in result, 
                         f"Connection timeout should return error message: {result}")
        
        # Test handling of connection refused errors
        with patch('src.riley2.agents.email_agent.build', side_effect=ConnectionRefusedError('Connection refused')):
            result = email_download_chunk("2025/05/01", "2025/05/02")
            self.assertIsInstance(result, str, "Should return error string for connection refused")
            self.assertTrue("Error" in result or "Failed" in result, 
                         f"Connection refused should return error message: {result}")
        
        # Test handling of generic HTTP errors
        with patch('src.riley2.agents.email_agent.build', side_effect=requests.exceptions.RequestException('HTTP Error')):
            result = email_download_chunk("2025/05/01", "2025/05/02")
            self.assertIsInstance(result, str, "Should return error string for HTTP error")
            self.assertTrue("Error" in result or "Failed" in result, 
                         f"HTTP error should return error message: {result}")
    
    def test_service_call_error_handling(self):
        """Test handling of service call errors that might require retries."""
        logger.info("Testing service call error handling")
        
        # Create a mock service where the API call fails
        mock_service = MagicMock()
        mock_users = MagicMock()
        mock_messages = MagicMock()
        mock_list = MagicMock()
        
        # Set up the mock to simulate a connection error
        mock_list.execute.side_effect = requests.exceptions.ConnectionError("Connection failed")
        mock_messages.list.return_value = mock_list
        mock_users.return_value.messages.return_value = mock_messages
        mock_service.users = mock_users
        
        # Test email_download_chunk with error handling (not retry since that's not implemented yet)
        with patch('src.riley2.agents.email_agent.authenticate_gmail', return_value=mock_service):
            result = email_download_chunk("2025/05/01", "2025/05/02")
            self.assertIsInstance(result, str, "Should return error string for service call error")
            self.assertTrue("Error retrieving emails" in result, 
                         f"Service call error should return appropriate message: {result}")
    
    def test_very_large_email_batch(self):
        """Test handling of very large email batches."""
        logger.info("Testing large email batch handling")
        
        # Create a large email batch
        large_batch = ""
        for i in range(100):  # Create 100 emails
            large_batch += f"From: sender{i}@example.com\nSubject: Email {i}\nBody of email {i}\n\n---\n"
        
        # Test filtering from large batch
        filter_result = self.email_mock.email_filter_by_sender(large_batch, "sender50@example.com")
        self.assertTrue("sender50@example.com" in filter_result, "Should find specific email in large batch")
        
        # Test summarizing large batch (this actually tests the implementation's robustness)
        summary_result = self.email_mock.email_summarize_batch(large_batch)
        self.assertIsInstance(summary_result, str, "Should return string summary for large batch")
        self.assertTrue(len(summary_result) > 0, "Summary should not be empty")


if __name__ == "__main__":
    unittest.main()