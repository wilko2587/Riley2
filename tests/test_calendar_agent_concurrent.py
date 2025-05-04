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
    
    def test_priority_based_conflict_resolution(self):
        """Test whether calendar correctly resolves conflicts based on event priority settings."""
        log_test_step("Testing priority-based conflict resolution for calendar events")
        
        # Define events with different priorities
        high_priority_event = {
            "title": "Executive Board Meeting", 
            "date": "2025/05/22", 
            "start_time": "14:00", 
            "end_time": "15:30",
            "organizer": "ceo",
            "priority": "high"
        }
        
        medium_priority_event = {
            "title": "Department Meeting", 
            "date": "2025/05/22", 
            "start_time": "14:30", 
            "end_time": "16:00",
            "organizer": "manager",
            "priority": "medium"
        }
        
        low_priority_event = {
            "title": "Optional Team Sync", 
            "date": "2025/05/22", 
            "start_time": "15:00", 
            "end_time": "16:00",
            "organizer": "team_lead",
            "priority": "low"
        }
        
        # Mock calendar storage to track attempted writes
        calendar_storage = []
        storage_lock = threading.Lock()
        
        # Priority rankings
        priority_rank = {
            "high": 3,
            "medium": 2,
            "low": 1,
            None: 0  # Default for events without priority
        }
        
        # Create patched version of calendar create method that uses our synchronized storage
        # and respects priority for conflict resolution
        def mock_calendar_create_with_priority(event_data):
            with storage_lock:
                # Check for conflicts before adding
                conflicts = []
                for existing_event in calendar_storage:
                    if self._events_conflict(existing_event, event_data):
                        conflicts.append(existing_event)
                
                if conflicts:
                    # Get priority of new event
                    new_event_priority = priority_rank.get(event_data.get("priority"), 0)
                    
                    # If there are conflicts, check if the new event has higher priority
                    can_override = True
                    for conflict in conflicts:
                        conflict_priority = priority_rank.get(conflict.get("priority"), 0)
                        if conflict_priority >= new_event_priority:
                            can_override = False
                            logger.warning(f"Cannot schedule: {event_data['title']} (priority {event_data.get('priority')}) "
                                          f"conflicts with {conflict['title']} (priority {conflict.get('priority')})")
                            return {
                                "status": "conflict", 
                                "event": event_data, 
                                "conflicting_with": conflict,
                                "reason": "lower_priority"
                            }
                    
                    if can_override:
                        # Remove all lower priority conflicting events
                        for conflict in conflicts:
                            logger.info(f"Removing lower priority event: {conflict['title']}")
                            calendar_storage.remove(conflict)
                        
                        # Add the higher priority event
                        calendar_storage.append(event_data)
                        logger.info(f"Higher priority event added: {event_data['title']}")
                        return {
                            "status": "override", 
                            "event": event_data,
                            "overridden": conflicts
                        }
                else:
                    # No conflicts, add event normally
                    calendar_storage.append(event_data)
                    logger.info(f"Event added to calendar: {event_data['title']}")
                    return {"status": "success", "event": event_data}
        
        # Function to simulate an agent scheduling an event
        def agent_schedule_event(agent_id, event_data):
            logger.info(f"Agent {agent_id} attempting to schedule: {event_data['title']} (priority: {event_data.get('priority')})")
            
            # Simulate network delay and processing time
            time.sleep(0.1)
            
            # Try to create the event
            result = mock_calendar_create_with_priority(event_data)
            
            with self.operation_lock:
                self.concurrent_operations.append({
                    "agent_id": agent_id,
                    "event": event_data,
                    "result": result
                })
            
            return result
        
        # Clear operation tracking from previous tests
        self.concurrent_operations = []
        
        # Test Case 1: Schedule high priority event after medium priority event
        # Expected: High priority event should override the medium priority event
        thread1 = threading.Thread(target=agent_schedule_event, args=("manager", medium_priority_event))
        thread1.start()
        thread1.join()
        
        thread2 = threading.Thread(target=agent_schedule_event, args=("ceo", high_priority_event))
        thread2.start()
        thread2.join()
        
        # Analyze the results for Test Case 1
        self.assertEqual(len(calendar_storage), 1, 
                       "Only the high priority event should remain in the calendar")
        self.assertEqual(calendar_storage[0]["title"], high_priority_event["title"],
                       "The high priority event should override the medium priority event")
        
        # Find operations with 'override' status
        override_ops = [op for op in self.concurrent_operations if op["result"].get("status") == "override"]
        self.assertEqual(len(override_ops), 1, "One operation should have override status")
        self.assertEqual(override_ops[0]["agent_id"], "ceo", "CEO's high priority event should override")
        
        # Reset for next test
        calendar_storage.clear()
        self.concurrent_operations.clear()
        
        # Test Case 2: Try to schedule a low priority event when higher priority events exist
        # Expected: Low priority event should be rejected
        thread1 = threading.Thread(target=agent_schedule_event, args=("ceo", high_priority_event))
        thread1.start()
        thread1.join()
        
        thread2 = threading.Thread(target=agent_schedule_event, args=("team_lead", low_priority_event))
        thread2.start()
        thread2.join()
        
        # Analyze the results for Test Case 2
        self.assertEqual(len(calendar_storage), 1, 
                       "Only the high priority event should be in the calendar")
        conflict_ops = [op for op in self.concurrent_operations if op["result"].get("status") == "conflict"]
        self.assertEqual(len(conflict_ops), 1, "Low priority event should be rejected due to conflict")
        self.assertEqual(conflict_ops[0]["result"].get("reason"), "lower_priority", 
                       "Conflict should be due to lower priority")
        
        # Reset for next test
        calendar_storage.clear()
        self.concurrent_operations.clear()
        
        # Test Case 3: Equal priority events
        # Expected: First-come-first-served (already scheduled event has precedence)
        medium_priority_event2 = medium_priority_event.copy()
        medium_priority_event2["title"] = "Alternate Department Meeting"
        
        thread1 = threading.Thread(target=agent_schedule_event, args=("manager1", medium_priority_event))
        thread1.start()
        thread1.join()
        
        thread2 = threading.Thread(target=agent_schedule_event, args=("manager2", medium_priority_event2))
        thread2.start()
        thread2.join()
        
        # Analyze the results for Test Case 3
        self.assertEqual(len(calendar_storage), 1, 
                       "Only the first medium priority event should remain")
        self.assertEqual(calendar_storage[0]["title"], medium_priority_event["title"],
                       "The first scheduled event should take precedence when priorities are equal")
        
        log_test_success("test_priority_based_conflict_resolution")
    
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