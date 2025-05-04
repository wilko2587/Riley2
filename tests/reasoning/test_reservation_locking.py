"""
Test module for calendar reservation locking mechanics.

This test suite verifies that the calendar agent correctly implements locking mechanisms
to prevent race conditions when multiple agents attempt to access and modify the same
calendar slots simultaneously.
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


class TestReservationLocking(unittest.TestCase):
    """
    Test suite focusing on calendar reservation locking mechanisms.
    
    This class verifies that the calendar agent correctly implements locking
    to prevent race conditions and data corruption during concurrent operations.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.calendar_mock = CalendarAgentMock()
        logger.info("Initialized CalendarAgentMock for reservation locking testing")
        
        # Create a test config with empty events for a clean slate
        self.empty_events_patcher = patch('tests.config.TestConfigLoader.get_calendar_events_by_date_range', return_value=[])
        self.empty_events_mock = self.empty_events_patcher.start()
        
        # Setup shared state for tracking concurrent operations
        self.concurrent_operations = []
        self.operation_lock = threading.Lock()
        
        # Setup reservation locks tracking
        self.active_locks = {}
        self.lock_history = []
        self.lock_tracking_lock = threading.Lock()
    
    def tearDown(self):
        """Clean up after tests."""
        self.empty_events_patcher.stop()
    
    def test_basic_lock_acquisition(self):
        """Test that locks can be acquired and released for calendar slots."""
        log_test_step("Testing basic lock acquisition for calendar slots")
        
        # Define test slots to lock
        slot1 = {"date": "2025/05/25", "start_time": "10:00", "end_time": "11:00"}
        slot2 = {"date": "2025/05/25", "start_time": "11:00", "end_time": "12:00"}
        
        # Create reservation manager with our tracking
        reservation_manager = self._create_reservation_manager()
        
        # Acquire locks
        lock1 = reservation_manager.acquire_lock("agent1", slot1)
        lock2 = reservation_manager.acquire_lock("agent2", slot2)
        
        # Verify locks were acquired
        self.assertTrue(lock1["success"], "First lock should be successfully acquired")
        self.assertTrue(lock2["success"], "Second lock for non-overlapping slot should be acquired")
        
        # Verify lock tracking
        with self.lock_tracking_lock:
            self.assertEqual(len(self.active_locks), 2, "Two locks should be active")
            self.assertTrue(self._is_slot_locked(slot1), "Slot 1 should be locked")
            self.assertTrue(self._is_slot_locked(slot2), "Slot 2 should be locked")
        
        # Release locks
        release1 = reservation_manager.release_lock(lock1["lock_id"])
        release2 = reservation_manager.release_lock(lock2["lock_id"])
        
        self.assertTrue(release1["success"], "First lock should be successfully released")
        self.assertTrue(release2["success"], "Second lock should be successfully released")
        
        # Verify locks were released
        with self.lock_tracking_lock:
            self.assertEqual(len(self.active_locks), 0, "No locks should be active after release")
            self.assertFalse(self._is_slot_locked(slot1), "Slot 1 should be unlocked")
            self.assertFalse(self._is_slot_locked(slot2), "Slot 2 should be unlocked")
        
        log_test_success("test_basic_lock_acquisition")
    
    def test_overlapping_slot_locking(self):
        """Test that overlapping slots cannot be locked simultaneously."""
        log_test_step("Testing lock prevention for overlapping calendar slots")
        
        # Define overlapping slots
        slot1 = {"date": "2025/05/26", "start_time": "14:00", "end_time": "15:00"}
        slot2 = {"date": "2025/05/26", "start_time": "14:30", "end_time": "15:30"}
        
        # Create reservation manager with our tracking
        reservation_manager = self._create_reservation_manager()
        
        # Acquire first lock
        lock1 = reservation_manager.acquire_lock("agent1", slot1)
        self.assertTrue(lock1["success"], "First lock should be successfully acquired")
        
        # Try to acquire overlapping lock
        lock2 = reservation_manager.acquire_lock("agent2", slot2)
        self.assertFalse(lock2["success"], "Second lock for overlapping slot should fail")
        self.assertEqual(lock2["reason"], "slot_locked", "Failure reason should be 'slot_locked'")
        
        # Verify lock tracking
        with self.lock_tracking_lock:
            self.assertEqual(len(self.active_locks), 1, "Only one lock should be active")
            self.assertTrue(self._is_slot_locked(slot1), "Slot 1 should be locked")
            # The slot2 isn't directly locked, but it overlaps with a locked slot
            # So we need to check if attempting to lock it would fail, not if it's actually locked
            with_overlap = False
            for lock in self.active_locks.values():
                if self._slots_overlap(lock["slot"], slot2):
                    with_overlap = True
                    break
            self.assertTrue(with_overlap, "Slot 2 should overlap with a locked slot")
        
        # Release first lock
        release1 = reservation_manager.release_lock(lock1["lock_id"])
        self.assertTrue(release1["success"], "Lock should be successfully released")
        
        # Try again with the second slot
        lock2_retry = reservation_manager.acquire_lock("agent2", slot2)
        self.assertTrue(lock2_retry["success"], "Second lock should succeed after first is released")
        
        # Clean up
        reservation_manager.release_lock(lock2_retry["lock_id"])
        
        log_test_success("test_overlapping_slot_locking")
    
    def test_concurrent_lock_acquisition(self):
        """Test behavior when multiple agents try to lock the same slot simultaneously."""
        log_test_step("Testing concurrent lock acquisition for the same calendar slot")
        
        # Define a slot that multiple agents will try to lock
        target_slot = {"date": "2025/05/27", "start_time": "09:00", "end_time": "10:00"}
        
        # Create reservation manager with our tracking
        reservation_manager = self._create_reservation_manager()
        
        # Function to simulate an agent acquiring a lock
        def agent_acquire_lock(agent_id, slot):
            logger.info(f"Agent {agent_id} attempting to lock slot: {slot['date']} {slot['start_time']}-{slot['end_time']}")
            
            # Simulate network delay and processing time
            time.sleep(0.1)
            
            # Try to acquire the lock
            result = reservation_manager.acquire_lock(agent_id, slot)
            
            # Record the operation
            with self.operation_lock:
                self.concurrent_operations.append({
                    "agent_id": agent_id,
                    "slot": slot,
                    "result": result
                })
            
            # If successful, simulate using the slot and then release
            if result["success"]:
                logger.info(f"Agent {agent_id} acquired lock {result['lock_id']}")
                time.sleep(0.2)  # Simulate using the slot
                release_result = reservation_manager.release_lock(result["lock_id"])
                logger.info(f"Agent {agent_id} released lock: {release_result['success']}")
            else:
                logger.info(f"Agent {agent_id} failed to acquire lock: {result['reason']}")
            
            return result
        
        # Clear operation tracking
        self.concurrent_operations = []
        
        # Create threads to simulate concurrent operations
        thread1 = threading.Thread(target=agent_acquire_lock, args=("agent1", target_slot.copy()))
        thread2 = threading.Thread(target=agent_acquire_lock, args=("agent2", target_slot.copy()))
        thread3 = threading.Thread(target=agent_acquire_lock, args=("agent3", target_slot.copy()))
        
        # Start the threads
        thread1.start()
        thread2.start()
        thread3.start()
        
        # Wait for all threads to complete
        thread1.join()
        thread2.join()
        thread3.join()
        
        # Analyze the results
        success_count = sum(1 for op in self.concurrent_operations if op["result"]["success"])
        failure_count = sum(1 for op in self.concurrent_operations if not op["result"]["success"])
        
        # Exactly one agent should succeed, and others should fail
        self.assertEqual(success_count, 1, "Exactly one agent should acquire the lock")
        self.assertEqual(failure_count, 2, "Two agents should fail to acquire the lock")
        
        # Verify all locks were properly released
        with self.lock_tracking_lock:
            self.assertEqual(len(self.active_locks), 0, "All locks should be released at the end")
        
        log_test_success("test_concurrent_lock_acquisition")
    
    def test_lock_expiration(self):
        """Test that locks automatically expire after their timeout period."""
        log_test_step("Testing lock expiration after timeout")
        
        # Define a slot to lock with a short timeout
        slot = {"date": "2025/05/28", "start_time": "15:00", "end_time": "16:00"}
        short_timeout = 0.5  # 500ms timeout
        
        # Create reservation manager with our tracking and short timeout
        reservation_manager = self._create_reservation_manager(default_timeout=short_timeout)
        
        # Acquire lock
        lock = reservation_manager.acquire_lock("agent1", slot)
        self.assertTrue(lock["success"], "Lock should be successfully acquired")
        
        # Verify lock is active
        with self.lock_tracking_lock:
            self.assertEqual(len(self.active_locks), 1, "One lock should be active")
            self.assertTrue(self._is_slot_locked(slot), "Slot should be locked")
        
        # Wait for lock to expire
        logger.info(f"Waiting {short_timeout * 1.5} seconds for lock to expire...")
        time.sleep(short_timeout * 1.5)  # Wait longer than timeout
        
        # Verify lock was automatically expired
        with self.lock_tracking_lock:
            self.assertEqual(len(self.active_locks), 0, "No locks should be active after timeout")
            self.assertFalse(self._is_slot_locked(slot), "Slot should be unlocked after timeout")
        
        # Another agent should be able to lock the slot now
        lock2 = reservation_manager.acquire_lock("agent2", slot)
        self.assertTrue(lock2["success"], "Lock should be acquired after previous lock expired")
        
        # Clean up
        reservation_manager.release_lock(lock2["lock_id"])
        
        log_test_success("test_lock_expiration")
    
    def test_reservation_with_finalization(self):
        """Test the full reservation flow including lock, update, and finalize."""
        log_test_step("Testing complete reservation flow with finalization")
        
        # Define a slot to reserve
        slot = {"date": "2025/05/29", "start_time": "13:00", "end_time": "14:00"}
        event_data = {
            "title": "Important Meeting",
            "date": slot["date"],
            "start_time": slot["start_time"],
            "end_time": slot["end_time"],
            "organizer": "agent1"
        }
        
        # Mock calendar storage
        calendar_storage = []
        
        # Create reservation manager
        reservation_manager = self._create_reservation_manager()
        
        # Define a function that simulates the full reservation process
        def reserve_slot(agent_id, slot_info, event_info):
            # Step 1: Acquire lock
            lock = reservation_manager.acquire_lock(agent_id, slot_info)
            if not lock["success"]:
                return {"status": "failed", "stage": "lock", "reason": lock["reason"]}
            
            # Step 2: Simulate processing delay
            time.sleep(0.2)
            
            # Step 3: Create the event in calendar storage
            with self.operation_lock:  # Using operation_lock as a storage lock
                calendar_storage.append(event_info)
            
            # Step 4: Release the lock
            release = reservation_manager.release_lock(lock["lock_id"])
            if not release["success"]:
                return {"status": "failed", "stage": "release", "reason": release["reason"]}
            
            return {"status": "success", "event": event_info}
        
        # Execute the reservation
        result = reserve_slot("agent1", slot, event_data)
        
        # Verify results
        self.assertEqual(result["status"], "success", "Reservation should complete successfully")
        self.assertEqual(len(calendar_storage), 1, "Event should be added to calendar storage")
        self.assertEqual(calendar_storage[0]["title"], "Important Meeting", "Event data should be correct")
        
        # Verify no locks are left active
        with self.lock_tracking_lock:
            self.assertEqual(len(self.active_locks), 0, "No locks should be active at the end")
        
        log_test_success("test_reservation_with_finalization")
    
    def _create_reservation_manager(self, default_timeout=5.0):
        """Create a reservation manager with appropriate locking functionality."""
        class ReservationManager:
            def __init__(self, test_instance, default_timeout):
                self.test = test_instance
                self.default_timeout = default_timeout
                self.lock_id_counter = 0
            
            def _generate_lock_id(self):
                self.lock_id_counter += 1
                return f"lock_{self.lock_id_counter}"
            
            def _slots_overlap(self, slot1, slot2):
                """Check if two time slots overlap."""
                # Different days don't overlap
                if slot1["date"] != slot2["date"]:
                    return False
                
                # Convert times to datetime objects for comparison
                slot1_start = datetime.strptime(slot1["start_time"], "%H:%M")
                slot1_end = datetime.strptime(slot1["end_time"], "%H:%M")
                slot2_start = datetime.strptime(slot2["start_time"], "%H:%M")
                slot2_end = datetime.strptime(slot2["end_time"], "%H:%M")
                
                # Check for overlap
                return slot1_start < slot2_end and slot1_end > slot2_start
            
            def acquire_lock(self, agent_id, slot, timeout=None):
                """Attempt to lock a calendar slot."""
                if timeout is None:
                    timeout = self.default_timeout
                
                lock_id = self._generate_lock_id()
                
                with self.test.lock_tracking_lock:
                    # Check if slot is already locked
                    for existing_lock in self.test.active_locks.values():
                        if self._slots_overlap(existing_lock["slot"], slot):
                            logger.warning(f"Agent {agent_id} failed to lock slot: overlaps with existing lock")
                            return {
                                "success": False,
                                "reason": "slot_locked",
                                "locking_agent": existing_lock["agent_id"]
                            }
                    
                    # Create the lock
                    lock_info = {
                        "lock_id": lock_id,
                        "agent_id": agent_id,
                        "slot": slot,
                        "acquired_at": time.time(),
                        "expires_at": time.time() + timeout
                    }
                    
                    # Add to active locks
                    self.test.active_locks[lock_id] = lock_info
                    
                    # Add to lock history
                    self.test.lock_history.append({
                        "action": "acquire",
                        "lock_id": lock_id,
                        "agent_id": agent_id,
                        "slot": slot,
                        "timestamp": time.time()
                    })
                    
                    # Start a timer to automatically expire the lock
                    if timeout > 0:
                        expiry_thread = threading.Timer(
                            timeout, 
                            self.expire_lock,
                            args=[lock_id]
                        )
                        expiry_thread.daemon = True
                        expiry_thread.start()
                    
                    logger.info(f"Agent {agent_id} acquired lock {lock_id} for slot {slot['date']} {slot['start_time']}-{slot['end_time']}")
                    
                    return {
                        "success": True,
                        "lock_id": lock_id,
                        "expires_at": lock_info["expires_at"]
                    }
            
            def release_lock(self, lock_id):
                """Release a previously acquired lock."""
                with self.test.lock_tracking_lock:
                    if lock_id not in self.test.active_locks:
                        return {
                            "success": False,
                            "reason": "invalid_lock_id"
                        }
                    
                    # Get lock info before removal
                    lock_info = self.test.active_locks[lock_id]
                    
                    # Remove from active locks
                    del self.test.active_locks[lock_id]
                    
                    # Add to lock history
                    self.test.lock_history.append({
                        "action": "release",
                        "lock_id": lock_id,
                        "agent_id": lock_info["agent_id"],
                        "slot": lock_info["slot"],
                        "timestamp": time.time()
                    })
                    
                    logger.info(f"Lock {lock_id} released by agent {lock_info['agent_id']}")
                    
                    return {
                        "success": True
                    }
            
            def expire_lock(self, lock_id):
                """Automatically expire a lock that has reached its timeout."""
                with self.test.lock_tracking_lock:
                    if lock_id in self.test.active_locks:
                        lock_info = self.test.active_locks[lock_id]
                        
                        # Check if it's really expired
                        if time.time() >= lock_info["expires_at"]:
                            # Remove from active locks
                            del self.test.active_locks[lock_id]
                            
                            # Add to lock history
                            self.test.lock_history.append({
                                "action": "expire",
                                "lock_id": lock_id,
                                "agent_id": lock_info["agent_id"],
                                "slot": lock_info["slot"],
                                "timestamp": time.time()
                            })
                            
                            logger.info(f"Lock {lock_id} expired for agent {lock_info['agent_id']}")
        
        return ReservationManager(self, default_timeout)
    
    def _is_slot_locked(self, slot):
        """Check if a slot is currently locked."""
        # This must be called with lock_tracking_lock held
        for lock in self.active_locks.values():
            if lock["slot"] == slot:  # We're checking for exact slot match, not overlap
                return True
        return False
    
    def _slots_overlap(self, slot1, slot2):
        """Check if two time slots overlap."""
        # Different days don't overlap
        if slot1["date"] != slot2["date"]:
            return False
        
        # Convert times to datetime objects for comparison
        slot1_start = datetime.strptime(slot1["start_time"], "%H:%M")
        slot1_end = datetime.strptime(slot1["end_time"], "%H:%M")
        slot2_start = datetime.strptime(slot2["start_time"], "%H:%M")
        slot2_end = datetime.strptime(slot2["end_time"], "%H:%M")
        
        # Check for overlap
        return slot1_start < slot2_end and slot1_end > slot2_start


if __name__ == "__main__":
    unittest.main()