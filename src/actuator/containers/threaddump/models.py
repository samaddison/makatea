from typing import List, Optional, Dict

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class StackTraceElement(ExtraBaseModel):
    """Represents a stack trace element in a thread dump."""
    module_name: Optional[str] = Field(None, alias="moduleName")
    module_version: Optional[str] = Field(None, alias="moduleVersion")
    method_name: str = Field(alias="methodName")
    file_name: Optional[str] = Field(None, alias="fileName")
    line_number: int = Field(alias="lineNumber")
    class_name: str = Field(alias="className")
    native_method: bool = Field(alias="nativeMethod")


class LockInfo(ExtraBaseModel):
    """Represents lock information in a thread dump."""
    class_name: str = Field(alias="className")
    identity_hash_code: int = Field(alias="identityHashCode")


class Monitor(ExtraBaseModel):
    """Represents a monitor in a thread dump."""
    class_name: str = Field(alias="className")
    identity_hash_code: int = Field(alias="identityHashCode")
    locked_stack_depth: int = Field(alias="lockedStackDepth")
    locked_stack_frame: StackTraceElement = Field(alias="lockedStackFrame")


class Synchronizer(ExtraBaseModel):
    """Represents a synchronizer in a thread dump."""
    class_name: str = Field(alias="className")
    identity_hash_code: int = Field(alias="identityHashCode")


class Thread(ExtraBaseModel):
    """Represents a thread in a thread dump."""
    thread_name: str = Field(alias="threadName")
    thread_id: int = Field(alias="threadId")
    blocked_time: int = Field(alias="blockedTime")
    blocked_count: int = Field(alias="blockedCount")
    waited_time: int = Field(alias="waitedTime")
    waited_count: int = Field(alias="waitedCount")
    lock_name: Optional[str] = Field(None, alias="lockName")
    lock_owner_id: int = Field(alias="lockOwnerId")
    daemon: bool
    in_native: bool = Field(alias="inNative")
    suspended: bool
    thread_state: str = Field(alias="threadState")
    priority: int
    stack_trace: List[StackTraceElement] = Field(alias="stackTrace")
    locked_monitors: List[Monitor] = Field(default_factory=list, alias="lockedMonitors")
    locked_synchronizers: List[Synchronizer] = Field(default_factory=list, alias="lockedSynchronizers")
    lock_info: Optional[LockInfo] = Field(None, alias="lockInfo")
    
    def get_stack_trace_as_string(self) -> str:
        """Get a formatted string representation of the stack trace.
        
        Returns:
            A formatted string of the stack trace.
        """
        lines = []
        for frame in self.stack_trace:
            native = " (native)" if frame.native_method else ""
            line = f"    at {frame.class_name}.{frame.method_name}({frame.file_name}:{frame.line_number}){native}"
            lines.append(line)
        return "\n".join(lines)
    
    def is_blocked(self) -> bool:
        """Check if the thread is blocked.
        
        Returns:
            True if the thread is blocked, False otherwise.
        """
        return self.thread_state == "BLOCKED"
    
    def is_waiting(self) -> bool:
        """Check if the thread is waiting.
        
        Returns:
            True if the thread is waiting, False otherwise.
        """
        return self.thread_state == "WAITING" or self.thread_state == "TIMED_WAITING"
    
    def is_runnable(self) -> bool:
        """Check if the thread is runnable.
        
        Returns:
            True if the thread is runnable, False otherwise.
        """
        return self.thread_state == "RUNNABLE"


class ThreadDump(ExtraBaseModel):
    """Container for thread dump information."""
    threads: List[Thread] = Field(default_factory=list)
    
    def get_thread_by_id(self, thread_id: int) -> Optional[Thread]:
        """Get a thread by its ID.
        
        Args:
            thread_id: The ID of the thread
            
        Returns:
            The Thread object, or None if not found.
        """
        for thread in self.threads:
            if thread.thread_id == thread_id:
                return thread
        return None
    
    def get_thread_by_name(self, thread_name: str) -> Optional[Thread]:
        """Get a thread by its name.
        
        Args:
            thread_name: The name of the thread
            
        Returns:
            The Thread object, or None if not found.
        """
        for thread in self.threads:
            if thread.thread_name == thread_name:
                return thread
        return None
    
    def get_threads_by_state(self, state: str) -> List[Thread]:
        """Get all threads in a specific state.
        
        Args:
            state: The thread state to filter by
            
        Returns:
            A list of Thread objects with the specified state.
        """
        return [thread for thread in self.threads if thread.thread_state == state]
    
    def get_daemon_threads(self) -> List[Thread]:
        """Get all daemon threads.
        
        Returns:
            A list of daemon threads.
        """
        return [thread for thread in self.threads if thread.daemon]
    
    def get_non_daemon_threads(self) -> List[Thread]:
        """Get all non-daemon threads.
        
        Returns:
            A list of non-daemon threads.
        """
        return [thread for thread in self.threads if not thread.daemon]
    
    def get_thread_states_summary(self) -> Dict[str, int]:
        """Get a summary of thread states.
        
        Returns:
            A dictionary mapping thread states to counts.
        """
        summary: Dict[str, int] = {}
        for thread in self.threads:
            state = thread.thread_state
            summary[state] = summary.get(state, 0) + 1
        return summary