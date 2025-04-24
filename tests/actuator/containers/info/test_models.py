import pytest
from datetime import datetime
from src.actuator.containers.info import (
    Info, Git, GitCommit, GitCommitId, GitCommitMessage, GitUser,
    Build, Java, JavaVendor, JavaRuntime, JavaJvm,
    OS, Process, Memory, MemorySection
)


def test_info_model_parsing():
    # Test JSON data
    json_data = {
        "git": {
            "branch": "master",
            "commit": {
                "time": "2025-04-23T03:02:32Z",
                "message": {
                    "full": "First commit\n",
                    "short": "First commit"
                },
                "id": {
                    "describe": "",
                    "abbrev": "4b21d9c",
                    "full": "4b21d9c937fb0db84f0a8cb3b220ae6a960918fa"
                },
                "user": {
                    "email": "samaddison@yahoo.com",
                    "name": "Juan Miguel Garcia"
                }
            },
            "build": {
                "user": {
                    "name": "Juan Miguel Garcia"
                }
            }
        },
        "build": {
            "artifact": "spring-boot-demo-app",
            "name": "spring-boot-demo-app",
            "time": "2025-04-23T10:23:42.348Z",
            "version": "0.0.1-SNAPSHOT",
            "group": "au.com.patrick"
        },
        "java": {
            "version": "21.0.6",
            "vendor": {
                "name": "Oracle Corporation",
                "version": "Oracle GraalVM 21.0.6+8.1"
            },
            "runtime": {
                "name": "Java(TM) SE Runtime Environment",
                "version": "21.0.6+8-LTS-jvmci-23.1-b55"
            },
            "jvm": {
                "name": "Java HotSpot(TM) 64-Bit Server VM",
                "vendor": "Oracle Corporation",
                "version": "21.0.6+8-LTS-jvmci-23.1-b55"
            }
        },
        "os": {
            "name": "Windows 11",
            "version": "10.0",
            "arch": "amd64"
        },
        "process": {
            "pid": 6636,
            "parentPid": 20676,
            "owner": "DESKTOP-H8F4AAH\\Juan Miguel Garcia",
            "cpus": 16,
            "memory": {
                "heap": {
                    "max": 5314183168,
                    "committed": 113246208,
                    "used": 49466472,
                    "init": 335544320
                },
                "nonHeap": {
                    "max": -1,
                    "committed": 76283904,
                    "used": 72691288,
                    "init": 2555904
                }
            }
        }
    }

    # Parse the JSON
    info = Info.model_validate(json_data)

    # Test Git information
    assert info.git is not None
    git = info.git
    assert isinstance(git, Git)
    assert git.branch == "master"
    assert git.build is not None
    assert git.build["user"]["name"] == "Juan Miguel Garcia"

    # Test Git commit
    commit = git.commit
    assert isinstance(commit, GitCommit)
    assert isinstance(commit.time, datetime)
    assert commit.time.isoformat() == "2025-04-23T03:02:32+00:00"
    
    # Test Git commit message
    message = commit.message
    assert isinstance(message, GitCommitMessage)
    assert message.short == "First commit"
    assert message.full == "First commit\n"
    
    # Test Git commit ID
    commit_id = commit.id
    assert isinstance(commit_id, GitCommitId)
    assert commit_id.abbrev == "4b21d9c"
    assert commit_id.full == "4b21d9c937fb0db84f0a8cb3b220ae6a960918fa"
    assert commit_id.describe == ""
    
    # Test Git user
    user = commit.user
    assert isinstance(user, GitUser)
    assert user.name == "Juan Miguel Garcia"
    assert user.email == "samaddison@yahoo.com"

    # Test Build information
    assert info.build is not None
    build = info.build
    assert isinstance(build, Build)
    assert build.artifact == "spring-boot-demo-app"
    assert build.name == "spring-boot-demo-app"
    assert isinstance(build.time, datetime)
    assert build.version == "0.0.1-SNAPSHOT"
    assert build.group == "au.com.patrick"

    # Test Java information
    assert info.java is not None
    java = info.java
    assert isinstance(java, Java)
    assert java.version == "21.0.6"
    
    # Test Java vendor
    vendor = java.vendor
    assert isinstance(vendor, JavaVendor)
    assert vendor.name == "Oracle Corporation"
    assert vendor.version == "Oracle GraalVM 21.0.6+8.1"
    
    # Test Java runtime
    runtime = java.runtime
    assert isinstance(runtime, JavaRuntime)
    assert runtime.name == "Java(TM) SE Runtime Environment"
    assert runtime.version == "21.0.6+8-LTS-jvmci-23.1-b55"
    
    # Test Java JVM
    jvm = java.jvm
    assert isinstance(jvm, JavaJvm)
    assert jvm.name == "Java HotSpot(TM) 64-Bit Server VM"
    assert jvm.vendor == "Oracle Corporation"
    assert jvm.version == "21.0.6+8-LTS-jvmci-23.1-b55"

    # Test OS information
    assert info.os is not None
    os = info.os
    assert isinstance(os, OS)
    assert os.name == "Windows 11"
    assert os.version == "10.0"
    assert os.arch == "amd64"

    # Test Process information
    assert info.process is not None
    process = info.process
    assert isinstance(process, Process)
    assert process.pid == 6636
    assert process.parent_pid == 20676
    assert process.owner == "DESKTOP-H8F4AAH\\Juan Miguel Garcia"
    assert process.cpus == 16
    
    # Test Memory information
    assert process.memory is not None
    memory = process.memory
    assert isinstance(memory, Memory)
    
    # Test Heap memory
    heap = memory.heap
    assert isinstance(heap, MemorySection)
    assert heap.max == 5314183168
    assert heap.committed == 113246208
    assert heap.used == 49466472
    assert heap.init == 335544320
    
    # Test Non-Heap memory
    non_heap = memory.non_heap
    assert isinstance(non_heap, MemorySection)
    assert non_heap.max == -1
    assert non_heap.committed == 76283904
    assert non_heap.used == 72691288
    assert non_heap.init == 2555904


def test_minimal_info():
    # Test minimal JSON data
    json_data = {}
    
    # Parse the JSON
    info = Info.model_validate(json_data)
    
    # Verify all sections are optional
    assert info.git is None
    assert info.build is None
    assert info.java is None
    assert info.os is None
    assert info.process is None