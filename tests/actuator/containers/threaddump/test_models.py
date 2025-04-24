import pytest
from src.actuator.containers.threaddump import (
    ThreadDump, Thread, StackTraceElement, Monitor, LockInfo, Synchronizer
)


def test_threaddump_model_parsing():
    # Test JSON data (simplified version of the actual data)
    json_data = {
        "threads": [
            {
                "threadName": "Reference Handler",
                "threadId": 9,
                "blockedTime": -1,
                "blockedCount": 0,
                "waitedTime": -1,
                "waitedCount": 0,
                "lockOwnerId": -1,
                "daemon": True,
                "inNative": False,
                "suspended": False,
                "threadState": "RUNNABLE",
                "priority": 10,
                "stackTrace": [
                    {
                        "moduleName": "java.base",
                        "moduleVersion": "21.0.6",
                        "methodName": "waitForReferencePendingList",
                        "fileName": "Reference.java",
                        "lineNumber": -2,
                        "className": "java.lang.ref.Reference",
                        "nativeMethod": True
                    },
                    {
                        "moduleName": "java.base",
                        "moduleVersion": "21.0.6",
                        "methodName": "processPendingReferences",
                        "fileName": "Reference.java",
                        "lineNumber": 246,
                        "className": "java.lang.ref.Reference",
                        "nativeMethod": False
                    }
                ],
                "lockedMonitors": [],
                "lockedSynchronizers": []
            },
            {
                "threadName": "Finalizer",
                "threadId": 10,
                "blockedTime": -1,
                "blockedCount": 0,
                "waitedTime": -1,
                "waitedCount": 1,
                "lockName": "java.lang.ref.NativeReferenceQueue$Lock@e1af3a1",
                "lockOwnerId": -1,
                "daemon": True,
                "inNative": False,
                "suspended": False,
                "threadState": "WAITING",
                "priority": 8,
                "stackTrace": [
                    {
                        "moduleName": "java.base",
                        "moduleVersion": "21.0.6",
                        "methodName": "wait0",
                        "fileName": "Object.java",
                        "lineNumber": -2,
                        "className": "java.lang.Object",
                        "nativeMethod": True
                    }
                ],
                "lockedMonitors": [
                    {
                        "className": "sun.nio.ch.Util$2",
                        "identityHashCode": 637840485,
                        "lockedStackDepth": 2,
                        "lockedStackFrame": {
                            "moduleName": "java.base",
                            "moduleVersion": "21.0.6",
                            "methodName": "lockAndDoSelect",
                            "fileName": "SelectorImpl.java",
                            "lineNumber": 130,
                            "className": "sun.nio.ch.SelectorImpl",
                            "nativeMethod": False
                        }
                    }
                ],
                "lockedSynchronizers": [
                    {
                        "className": "java.util.concurrent.locks.ReentrantLock$NonfairSync",
                        "identityHashCode": 18627876
                    }
                ],
                "lockInfo": {
                    "className": "java.lang.ref.NativeReferenceQueue$Lock",
                    "identityHashCode": 236647329
                }
            }
        ]
    }

    # Parse the JSON
    thread_dump = ThreadDump.model_validate(json_data)

    # Test thread count
    assert len(thread_dump.threads) == 2
    
    # Test first thread
    thread1 = thread_dump.threads[0]
    assert isinstance(thread1, Thread)
    assert thread1.thread_name == "Reference Handler"
    assert thread1.thread_id == 9
    assert thread1.blocked_time == -1
    assert thread1.blocked_count == 0
    assert thread1.waited_time == -1
    assert thread1.waited_count == 0
    assert thread1.lock_owner_id == -1
    assert thread1.daemon is True
    assert thread1.in_native is False
    assert thread1.suspended is False
    assert thread1.thread_state == "RUNNABLE"
    assert thread1.priority == 10
    assert thread1.lock_name is None
    assert thread1.lock_info is None
    
    # Test stack trace
    assert len(thread1.stack_trace) == 2
    stack_element = thread1.stack_trace[0]
    assert isinstance(stack_element, StackTraceElement)
    assert stack_element.module_name == "java.base"
    assert stack_element.module_version == "21.0.6"
    assert stack_element.method_name == "waitForReferencePendingList"
    assert stack_element.file_name == "Reference.java"
    assert stack_element.line_number == -2
    assert stack_element.class_name == "java.lang.ref.Reference"
    assert stack_element.native_method is True
    
    # Test stack trace string format
    stack_trace_str = thread1.get_stack_trace_as_string()
    assert "at java.lang.ref.Reference.waitForReferencePendingList(Reference.java:-2) (native)" in stack_trace_str
    assert "at java.lang.ref.Reference.processPendingReferences(Reference.java:246)" in stack_trace_str
    
    # Test locked monitors and synchronizers
    assert len(thread1.locked_monitors) == 0
    assert len(thread1.locked_synchronizers) == 0
    
    # Test second thread
    thread2 = thread_dump.threads[1]
    assert thread2.thread_name == "Finalizer"
    assert thread2.thread_id == 10
    assert thread2.thread_state == "WAITING"
    assert thread2.lock_name == "java.lang.ref.NativeReferenceQueue$Lock@e1af3a1"
    
    # Test locked monitor
    assert len(thread2.locked_monitors) == 1
    monitor = thread2.locked_monitors[0]
    assert isinstance(monitor, Monitor)
    assert monitor.class_name == "sun.nio.ch.Util$2"
    assert monitor.identity_hash_code == 637840485
    assert monitor.locked_stack_depth == 2
    assert isinstance(monitor.locked_stack_frame, StackTraceElement)
    assert monitor.locked_stack_frame.class_name == "sun.nio.ch.SelectorImpl"
    
    # Test locked synchronizer
    assert len(thread2.locked_synchronizers) == 1
    synchronizer = thread2.locked_synchronizers[0]
    assert isinstance(synchronizer, Synchronizer)
    assert synchronizer.class_name == "java.util.concurrent.locks.ReentrantLock$NonfairSync"
    assert synchronizer.identity_hash_code == 18627876
    
    # Test lock info
    assert thread2.lock_info is not None
    assert isinstance(thread2.lock_info, LockInfo)
    assert thread2.lock_info.class_name == "java.lang.ref.NativeReferenceQueue$Lock"
    assert thread2.lock_info.identity_hash_code == 236647329
    
    # Test helper methods
    assert thread1.is_runnable() is True
    assert thread1.is_blocked() is False
    assert thread1.is_waiting() is False
    
    assert thread2.is_runnable() is False
    assert thread2.is_blocked() is False
    assert thread2.is_waiting() is True
    
    # Test thread lookup methods
    assert thread_dump.get_thread_by_id(9) == thread1
    assert thread_dump.get_thread_by_id(10) == thread2
    assert thread_dump.get_thread_by_id(999) is None
    
    assert thread_dump.get_thread_by_name("Reference Handler") == thread1
    assert thread_dump.get_thread_by_name("Finalizer") == thread2
    assert thread_dump.get_thread_by_name("NonExistent") is None
    
    # Test thread state filters
    runnable_threads = thread_dump.get_threads_by_state("RUNNABLE")
    assert len(runnable_threads) == 1
    assert runnable_threads[0] == thread1
    
    waiting_threads = thread_dump.get_threads_by_state("WAITING")
    assert len(waiting_threads) == 1
    assert waiting_threads[0] == thread2
    
    # Test daemon thread filters
    daemon_threads = thread_dump.get_daemon_threads()
    assert len(daemon_threads) == 2  # Both test threads are daemon
    
    non_daemon_threads = thread_dump.get_non_daemon_threads()
    assert len(non_daemon_threads) == 0
    
    # Test thread state summary
    state_summary = thread_dump.get_thread_states_summary()
    assert len(state_summary) == 2
    assert state_summary["RUNNABLE"] == 1
    assert state_summary["WAITING"] == 1


def test_empty_threaddump():
    # Test empty JSON data
    json_data = {"threads": []}
    
    # Parse the JSON
    thread_dump = ThreadDump.model_validate(json_data)
    
    # Verify empty thread dump
    assert len(thread_dump.threads) == 0
    assert len(thread_dump.get_daemon_threads()) == 0
    assert len(thread_dump.get_non_daemon_threads()) == 0
    assert len(thread_dump.get_threads_by_state("RUNNABLE")) == 0
    assert thread_dump.get_thread_states_summary() == {}