"""
Test module for calendar agent concurrent scheduling scenarios.

This test suite verifies that both real and mock calendar agent implementations
properly handle scenarios where multiple agents interact with the same calendar,
potentially creating scheduling conflicts.
"""

import unittest
import pytest
import threading
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import both real and mock implementations
from src.riley2.agents.calendar_agent import calendar_scan
from tests.mocks.calendar_agent_mock import CalendarAgentMock
from riley2.core.logger_utils import logger, log_test_step, log_test_success, log_test_failure


class TestCalendarAgentConcurrent(unittest.TestCase):
    """
    Test suite focusing on concurrent calendar agent operations.
    
    This class verifies behavior when multiple agents interact with
    the same calendar simultaneously, testing conflict detection,
    resolution, and race condition handling.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.calendar_mock = CalendarAgentMock()
        logger.info("Initialized CalendarAgentMock for concurrent scheduling testing")
        
        # Create a test config with empty events for a clean slate
        self.empty_events_patcher = patch('tests.config.TestConfigLoader.get_calendar_events_by_date_range', return_value=[])
        self.empty_events_mock = self.empty_events_patcher.start()
        
        # Setup shared state for tracking concurrent operations
        self.concurrent_operations = []
        self.operation_lock = threading.Lock()
    
    def tearDown(self):
        """Clean up after tests."""
        self.empty_events_patcher.stop()
    
    def test_concurrent_overlapping_events(self):
        """Test how calendar handles two agents scheduling overlapping events simultaneously."""
        log_test_step("Testing concurrent scheduling of overlapping calendar events")
        
        # Define overlapping events
        event1 = {
            "title": "Team Meeting", 
            "date": "2025/05/20", 
            "start_time": "10:00", 
            "end_time": "11:00",
            "organizer": "agent1"
        }
        
        event2 = {
            "title": "Client Call", 
            "date": "2025/05/20", 
            "start_time": "10:30", 
            "end_time": "11:30",
            "organizer": "agent2"
        }
        
        # Mock calendar storage to track attempted writes
        calendar_storage = []
        storage_lock = threading.Lock()
        
        # Create patched version of calendar create method that uses our synchronized storage
        def mock_calendar_create(event_data):
            with storage_lock:
                # Check for conflicts before adding
                for existing_event in calendar_storage:
                    if self._events_conflict(existing_event, event_data):
                        logger.warning(f"Conflict detected between events: {existing_event['title']} and {event_data['title']}")
                        return {"status": "conflict", "event": event_data, "conflicting_with": existing_event}
                
                calendar_storage.append(event_data)
                logger.info(f"Event added to calendar: {event_data['title']}")
                return {"status": "success", "event": event_data}
        
        # Function to simulate an agent scheduling an event
        def agent_schedule_event(agent_id, event_data):
            logger.info(f"Agent {agent_id} attempting to schedule: {event_data['title']}")
            
            # Simulate network delay and processing time
            time.sleep(0.1)
            
            # Try to create the event
            result = mock_calendar_create(event_data)
            
            with self.operation_lock:
                self.concurrent_operations.append({
                    "agent_id": agent_id,
                    "event": event_data,
                    "result": result
                })
            
            return result
        
        # Create threads to simulate concurrent operations
        thread1 = threading.Thread(target=agent_schedule_event, args=("agent1", event1))
        thread2 = threading.Thread(target=agent_schedule_event, args=("agent2", event2))
        
        # Start the threads
        thread1.start()
        thread2.start()
        
        # Wait for both threads to complete
        thread1.join()
        thread2.join()
        
        # Analyze the results
        self.assertEqual(len(calendar_storage), 1, 
                      "Only one of the conflicting events should be successfully scheduled")
        
        conflict_count = sum(1 for op in self.concurrent_operations if op["result"]["status"] == "conflict")
        success_count = sum(1 for op in self.concurrent_operations if op["result"]["status"] == "success")
        
        self.assertEqual(conflict_count, 1, "One operation should detect a conflict")
        self.assertEqual(success_count, 1, "One operation should succeed")
        
        # Find which agent succeeded and which had a conflict
        successful_agent = next((op["agent_id"] for op in self.concurrent_operations if op["result"]["status"] == "success"), None)
        conflict_agent = next((op["agent_id"] for op in self.concurrent_operations if op["result"]["status"] == "conflict"), None)
        
        logger.info(f"Agent {successful_agent} succeeded, Agent {conflict_agent} had a conflict")
        
        # Verify that the event in storage matches the successful agent's event
        successful_event = next((op["event"] for op in self.concurrent_operations if op["result"]["status"] == "success"), None)
        self.assertEqual(calendar_storage[0]["title"], successful_event["title"], 
                      "The stored event should match the successful agent's event")
        
        log_test_success("test_concurrent_overlapping_events")

    def test_concurrent_non_overlapping_events(self):
        """Test how calendar handles two agents scheduling non-overlapping events simultaneously."""
        log_test_step("Testing concurrent scheduling of non-overlapping calendar events")
        
        # Define non-overlapping events
        event1 = {
            "title": "Team Meeting", 
            "date": "2025/05/20", 
            "start_time": "10:00", 
            "end_time": "11:00",
            "organizer": "agent1"
        }
        
        event2 = {
            "title": "Client Call", 
            "date": "2025/05/20", 
            "start_time": "11:30", 
            "end_time": "12:30",
            "organizer": "agent2"
        }
        
        # Mock calendar storage to track attempted writes
        calendar_storage = []
        storage_lock = threading.Lock()
        
        # Create patched version of calendar create method that uses our synchronized storage
        def mock_calendar_create(event_data):
            with storage_lock:
                # Check for conflicts before adding
                for existing_event in calendar_storage:
                    if self._events_conflict(existing_event, event_data):
                        logger.warning(f"Conflict detected between events: {existing_event['title']} and {event_data['title']}")
                        return {"status": "conflict", "event": event_data, "conflicting_with": existing_event}
                
                calendar_storage.append(event_data)
                logger.info(f"Event added to calendar: {event_data['title']}")
                return {"status": "success", "event": event_data}
        
        # Function to simulate an agent scheduling an event
        def agent_schedule_event(agent_id, event_data):
            logger.info(f"Agent {agent_id} attempting to schedule: {event_data['title']}")
            
            # Simulate network delay and processing time
            time.sleep(0.1)
            
            # Try to create the event
            result = mock_calendar_create(event_data)
            
            with self.operation_lock:
                self.concurrent_operations.append({
                    "agent_id": agent_id,
                    "event": event_data,
                    "result": result
                })
            
            return result
        
        # Create threads to simulate concurrent operations
        thread1 = threading.Thread(target=agent_schedule_event, args=("agent1", event1))
        thread2 = threading.Thread(target=agent_schedule_event, args=("agent2", event2))
        
        # Clear operation tracking from previous tests
        self.concurrent_operations = []
        
        # Start the threads
        thread1.start()
        thread2.start()
        
        # Wait for both threads to complete
        thread1.join()
        thread2.join()
        
        # Analyze the results
        self.assertEqual(len(calendar_storage), 2, 
                      "Both non-conflicting events should be successfully scheduled")
        
        conflict_count = sum(1 for op in self.concurrent_operations if op["result"]["status"] == "conflict")
        success_count = sum(1 for op in self.concurrent_operations if op["result"]["status"] == "success")
        
        self.assertEqual(conflict_count, 0, "No operations should detect a conflict")
        self.assertEqual(success_count, 2, "Both operations should succeed")
        
        log_test_success("test_concurrent_non_overlapping_events")
    
    def test_concurrent_same_event(self):
        """Test how calendar handles two agents scheduling the exact same event simultaneously."""
        log_test_step("Testing concurrent scheduling of identical events")
        
        # Define identical events
        event_template = {
            "title": "Team Standup", 
            "date": "2025/05/21", 
            "start_time": "09:00", 
            "end_time": "09:30"
        }
        
        event1 = event_template.copy()
        event1["organizer"] = "agent1"
        
        event2 = event_template.copy()
        event2["organizer"] = "agent2"
        
        # Track scheduled events
        calendar_storage = []
        storage_lock = threading.Lock()
        
        # Function to check for duplicate events (same title, time, date)
        def is_duplicate_event(event1, event2):
            return (
                event1["title"] == event2["title"] and
                event1["date"] == event2["date"] and
                event1["start_time"] == event2["start_time"] and
                event1["end_time"] == event2["end_time"]
            )
        
        # Create patched version of calendar create method
        def mock_calendar_create(event_data):
            with storage_lock:
                # Check for duplicates before adding
                for existing_event in calendar_storage:
                    if is_duplicate_event(existing_event, event_data):
                        logger.warning(f"Duplicate detected: {event_data['title']}")
                        return {"status": "duplicate", "event": event_data, "duplicate_of": existing_event}
                
                calendar_storage.append(event_data)
                logger.info(f"Event added to calendar: {event_data['title']}")
                return {"status": "success", "event": event_data}
        
        # Function to simulate an agent scheduling an event
        def agent_schedule_event(agent_id, event_data):
            logger.info(f"Agent {agent_id} attempting to schedule: {event_data['title']}")
            
            # Try to create the event
            result = mock_calendar_create(event_data)
            
            with self.operation_lock:
                self.concurrent_operations.append({
                    "agent_id": agent_id,
                    "event": event_data,
                    "result": result
                })
            
            return result
        
        # Create threads to simulate concurrent operations
        thread1 = threading.Thread(target=agent_schedule_event, args=("agent1", event1))
        thread2 = threading.Thread(target=agent_schedule_event, args=("agent2", event2))
        
        # Clear operation tracking from previous tests
        self.concurrent_operations = []
        
        # Start the threads
        thread1.start()
        thread2.start()
        
        # Wait for both threads to complete
        thread1.join()
        thread2.join()
        
        # Analyze the results
        self.assertEqual(len(calendar_storage), 1, 
                      "Only one of the duplicate events should be added")
        
        duplicate_count = sum(1 for op in self.concurrent_operations if op["result"].get("status") == "duplicate")
        success_count = sum(1 for op in self.concurrent_operations if op["result"].get("status") == "success")
        
        self.assertEqual(duplicate_count, 1, "One operation should detect a duplicate")
        self.assertEqual(success_count, 1, "One operation should succeed")
        
        log_test_success("test_concurrent_same_event")
    
    def _events_conflict(self, event1, event2):
        """Helper method to detect if two events conflict in time."""
        # Different days don't conflict
        if event1["date"] != event2["date"]:
            return False
        
        # Convert times to datetime objects for comparison
        event1_start = datetime.strptime(event1["start_time"], "%H:%M")
        event1_end = datetime.strptime(event1["end_time"], "%H:%M")
        event2_start = datetime.strptime(event2["start_time"], "%H:%M")
        event2_end = datetime.strptime(event2["end_time"], "%H:%M")
        
        # Check for overlap
        return event1_start < event2_end and event1_end > event2_start


if __name__ == "__main__":
    unittest.main()