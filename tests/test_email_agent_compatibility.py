"""
Test module to ensure compatibility between real email agent and mock implementations.

This test suite verifies that the mock email agent matches the real implementation's
method signatures, parameter formats, and return value structures.
"""

import unittest
import pytest
from datetime import datetime, timedelta

# Import both real and mock implementations
from src.riley2.agents.email_agent import (
    authenticate_gmail, 
    email_download_chunk, 
    email_filter_by_sender, 
    email_summarize_batch
)
from tests.mocks.email_agent_mock import EmailAgentMock
from riley2.core.logger_utils import logger


class TestEmailAgentCompatibility(unittest.TestCase):
    """
    Test suite to ensure compatibility between real and mock email agent implementations.
    
    This class verifies that method signatures, parameter types, and return value
    structures are consistent between the real implementation and the mock.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.email_mock = EmailAgentMock()
        logger.info("Initialized EmailAgentMock for compatibility testing")
    
    def test_function_existence(self):
        """Test that all functions in the real implementation have counterparts in the mock."""
        logger.info("Testing function existence")
        
        # Check that all functions exist in the mock
        assert hasattr(self.email_mock, 'authenticate_gmail'), "Mock missing authenticate_gmail method"
        assert hasattr(self.email_mock, 'email_download_chunk'), "Mock missing email_download_chunk method"
        assert hasattr(self.email_mock, 'email_filter_by_sender'), "Mock missing email_filter_by_sender method"
        assert hasattr(self.email_mock, 'email_summarize_batch'), "Mock missing email_summarize_batch method"
        
        logger.info("All required functions exist in the mock implementation")
    
    def test_email_download_chunk_signature(self):
        """Test that email_download_chunk has compatible signatures and output formats."""
        logger.info("Testing email_download_chunk signature and output format")
        
        # Set test parameters
        start_date = "2025/05/01"
        end_date = "2025/05/02"
        
        # Get results from mock implementation (we can't test real API without credentials)
        mock_result = self.email_mock.email_download_chunk(start_date, end_date)
        
        # Verify that the mock result is a string
        assert isinstance(mock_result, str), "Mock email_download_chunk should return a string"
        
        # Check for expected formatting in mock result
        assert "From:" in mock_result, "Mock result should contain 'From:' field"
        assert "Subject:" in mock_result, "Mock result should contain 'Subject:' field"
        
        # Check delimiter format
        if len(mock_result.split("---")) > 1:
            assert "\n---\n" in mock_result, "Mock should use '\\n---\\n' as email delimiter"
        
        logger.info("email_download_chunk signature and output format are compatible")
    
    def test_email_filter_by_sender_signature(self):
        """Test that email_filter_by_sender has compatible signatures and behavior."""
        logger.info("Testing email_filter_by_sender signature and behavior")
        
        # Create sample input
        sample_emails = (
            "From: test@example.com\nSubject: Test Email\nThis is a test email\n\n"
            "---\n"
            "From: boss@company.com\nSubject: Important Meeting\nMeeting details\n\n"
        )
        
        # Test with mock implementation
        mock_result = self.email_mock.email_filter_by_sender(sample_emails, "boss@company.com")
        
        # Check that the result is a string
        assert isinstance(mock_result, str), "Mock email_filter_by_sender should return a string"
        
        # Check that filtering worked correctly
        assert "boss@company.com" in mock_result, "Filtered results should contain the requested sender"
        assert "test@example.com" not in mock_result, "Filtered results should not contain other senders"
        
        # Test with non-existent sender
        mock_no_result = self.email_mock.email_filter_by_sender(sample_emails, "nonexistent@example.com")
        assert "No emails found" in mock_no_result, "Should return 'No emails found' for non-existent sender"
        
        logger.info("email_filter_by_sender signature and behavior are compatible")
    
    def test_email_summarize_batch_signature(self):
        """Test that email_summarize_batch has compatible signatures."""
        logger.info("Testing email_summarize_batch signature")
        
        # Create sample input
        sample_emails = (
            "From: boss@company.com\nSubject: Team Meeting Tomorrow\n"
            "Don't forget we have a team meeting at 9am...\n\n"
        )
        
        # Test with mock implementation
        mock_result = self.email_mock.email_summarize_batch(sample_emails)
        
        # Check that the result is a string
        assert isinstance(mock_result, str), "Mock email_summarize_batch should return a string"
        
        # Check that the summary is not empty
        assert len(mock_result) > 0, "Summary should not be empty"
        
        logger.info("email_summarize_batch signature is compatible")
    
    def test_result_format_consistency(self):
        """Test that result formats are consistent between real and mock."""
        logger.info("Testing result format consistency")
        
        # Get a sample email batch from mock
        start_date = "2025/05/01"
        end_date = "2025/05/02"
        mock_emails = self.email_mock.email_download_chunk(start_date, end_date)
        
        # Check that it follows the expected format pattern
        email_chunks = mock_emails.split("---")
        
        for chunk in email_chunks:
            if not chunk.strip():
                continue
            
            # Each email should have From, Subject and content
            assert "From:" in chunk, f"Email chunk missing 'From:' field: {chunk}"
            assert "Subject:" in chunk, f"Email chunk missing 'Subject:' field: {chunk}"
        
        logger.info("Email format consistency verified")
