from datetime import datetime
from typing import Dict, Optional, Any

from pydantic import Field

from ..common.extra_base_model import ExtraBaseModel


class GitUser(ExtraBaseModel):
    """Represents a Git user."""
    name: str
    email: Optional[str] = None


class GitCommitMessage(ExtraBaseModel):
    """Represents a Git commit message."""
    full: str
    short: str


class GitCommitId(ExtraBaseModel):
    """Represents a Git commit ID."""
    describe: str = ""
    abbrev: str
    full: str


class GitCommit(ExtraBaseModel):
    """Represents a Git commit."""
    time: datetime
    message: GitCommitMessage
    id: GitCommitId
    user: GitUser


class Git(ExtraBaseModel):
    """Represents Git information."""
    branch: str
    commit: GitCommit
    build: Optional[Dict[str, Any]] = None


class Build(ExtraBaseModel):
    """Represents build information."""
    artifact: str
    name: str
    time: datetime
    version: str
    group: Optional[str] = None


class JavaVendor(ExtraBaseModel):
    """Represents Java vendor information."""
    name: str
    version: str


class JavaRuntime(ExtraBaseModel):
    """Represents Java runtime information."""
    name: str
    version: str


class JavaJvm(ExtraBaseModel):
    """Represents Java JVM information."""
    name: str
    vendor: str
    version: str


class Java(ExtraBaseModel):
    """Represents Java information."""
    version: str
    vendor: JavaVendor
    runtime: JavaRuntime
    jvm: JavaJvm


class OS(ExtraBaseModel):
    """Represents operating system information."""
    name: str
    version: str
    arch: str


class MemorySection(ExtraBaseModel):
    """Represents a memory section (heap or non-heap)."""
    max: int
    committed: int
    used: int
    init: int


class Memory(ExtraBaseModel):
    """Represents memory information."""
    heap: MemorySection
    non_heap: MemorySection = Field(alias="nonHeap")


class Process(ExtraBaseModel):
    """Represents process information."""
    pid: int
    parent_pid: Optional[int] = Field(None, alias="parentPid")
    owner: Optional[str] = None
    cpus: Optional[int] = None
    memory: Optional[Memory] = None


class Info(ExtraBaseModel):
    """Container for Spring Boot info."""
    git: Optional[Git] = None
    build: Optional[Build] = None
    java: Optional[Java] = None
    os: Optional[OS] = None
    process: Optional[Process] = None