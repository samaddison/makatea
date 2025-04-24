import pytest
from datetime import datetime
from src.actuator.containers.sbom import (
    SBOM, Metadata, Tool, Component, Hash, License, ExternalReference, Property, Dependency
)


def test_sbom_model_parsing():
    # Test JSON data (simplified version of the actual SBOM)
    json_data = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:51b6941b-ba08-451f-bbef-50dcf66bb117",
        "version": 1,
        "metadata": {
            "timestamp": "2025-04-23T07:00:38Z",
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "bom-ref": "tool:cyclonedx-gradle-plugin",
                        "author": "CycloneDX",
                        "name": "cyclonedx-gradle-plugin",
                        "version": "2.2.0"
                    }
                ],
                "services": []
            },
            "component": {
                "type": "application",
                "bom-ref": "pkg:maven/au.com.patrick/spring-boot-demo-app@0.0.1-SNAPSHOT?project_path=%3A",
                "group": "au.com.patrick",
                "name": "spring-boot-demo-app",
                "version": "0.0.1-SNAPSHOT",
                "purl": "pkg:maven/au.com.patrick/spring-boot-demo-app@0.0.1-SNAPSHOT?project_path=%3A",
                "modified": False,
                "externalReferences": []
            },
            "licenses": []
        },
        "components": [
            {
                "type": "library",
                "bom-ref": "pkg:maven/com.fasterxml.jackson.core/jackson-annotations@2.18.3?type=jar",
                "group": "com.fasterxml.jackson.core",
                "name": "jackson-annotations",
                "version": "2.18.3",
                "description": "Core annotations used for value types, used by Jackson data binding package.",
                "hashes": [
                    {
                        "alg": "MD5",
                        "content": "cae46e2c56e1b40b67dcfcfc9b6e275a"
                    },
                    {
                        "alg": "SHA-1",
                        "content": "7fa21cf7da4598f8240e4ebd9779249622af1acd"
                    }
                ],
                "licenses": [
                    {
                        "license": {
                            "id": "Apache-2.0"
                        }
                    }
                ],
                "purl": "pkg:maven/com.fasterxml.jackson.core/jackson-annotations@2.18.3?type=jar",
                "modified": False,
                "externalReferences": [
                    {
                        "type": "vcs",
                        "url": "https://github.com/FasterXML/jackson-annotations"
                    }
                ],
                "properties": [
                    {
                        "name": "cdx:maven:package:test",
                        "value": "false"
                    }
                ]
            }
        ],
        "dependencies": [
            {
                "ref": "pkg:maven/au.com.patrick/spring-boot-demo-app@0.0.1-SNAPSHOT?project_path=%3A",
                "dependsOn": [
                    "pkg:maven/org.springframework.boot/spring-boot-starter-data-rest@3.4.4?type=jar",
                    "pkg:maven/org.springframework.boot/spring-boot-starter-web@3.4.4?type=jar"
                ]
            }
        ]
    }

    # Parse the JSON
    sbom = SBOM.model_validate(json_data)

    # Test SBOM attributes
    assert sbom.bom_format == "CycloneDX"
    assert sbom.spec_version == "1.6"
    assert sbom.serial_number == "urn:uuid:51b6941b-ba08-451f-bbef-50dcf66bb117"
    assert sbom.version == 1

    # Test metadata
    metadata = sbom.metadata
    assert isinstance(metadata, Metadata)
    assert isinstance(metadata.timestamp, datetime)
    assert metadata.timestamp.isoformat() == "2025-04-23T07:00:38+00:00"

    # Test tools
    tools = metadata.tools
    assert isinstance(tools, Tool)
    assert len(tools.components) == 1
    assert len(tools.services) == 0
    
    tool_component = tools.components[0]
    assert isinstance(tool_component, Component)
    assert tool_component.type == "application"
    assert tool_component.name == "cyclonedx-gradle-plugin"
    assert tool_component.version == "2.2.0"
    assert tool_component.author == "CycloneDX"

    # Test main component
    main_component = metadata.component
    assert isinstance(main_component, Component)
    assert main_component.type == "application"
    assert main_component.group == "au.com.patrick"
    assert main_component.name == "spring-boot-demo-app"
    assert main_component.version == "0.0.1-SNAPSHOT"
    assert main_component.bom_ref == "pkg:maven/au.com.patrick/spring-boot-demo-app@0.0.1-SNAPSHOT?project_path=%3A"
    assert main_component.purl == "pkg:maven/au.com.patrick/spring-boot-demo-app@0.0.1-SNAPSHOT?project_path=%3A"
    assert main_component.modified is False
    assert len(main_component.external_references) == 0

    # Test components
    assert len(sbom.components) == 1
    component = sbom.components[0]
    assert isinstance(component, Component)
    assert component.type == "library"
    assert component.group == "com.fasterxml.jackson.core"
    assert component.name == "jackson-annotations"
    assert component.version == "2.18.3"
    assert component.description == "Core annotations used for value types, used by Jackson data binding package."
    assert component.bom_ref == "pkg:maven/com.fasterxml.jackson.core/jackson-annotations@2.18.3?type=jar"

    # Test hashes
    assert len(component.hashes) == 2
    hash1 = component.hashes[0]
    assert isinstance(hash1, Hash)
    assert hash1.alg == "MD5"
    assert hash1.content == "cae46e2c56e1b40b67dcfcfc9b6e275a"

    # Test licenses
    assert len(component.licenses) == 1
    license1 = component.licenses[0]
    assert isinstance(license1, License)
    assert license1.license["id"] == "Apache-2.0"

    # Test external references
    assert len(component.external_references) == 1
    ref1 = component.external_references[0]
    assert isinstance(ref1, ExternalReference)
    assert ref1.type == "vcs"
    assert ref1.url == "https://github.com/FasterXML/jackson-annotations"

    # Test properties
    assert len(component.properties) == 1
    prop1 = component.properties[0]
    assert isinstance(prop1, Property)
    assert prop1.name == "cdx:maven:package:test"
    assert prop1.value == "false"

    # Test dependencies
    assert len(sbom.dependencies) == 1
    dependency = sbom.dependencies[0]
    assert isinstance(dependency, Dependency)
    assert dependency.ref == "pkg:maven/au.com.patrick/spring-boot-demo-app@0.0.1-SNAPSHOT?project_path=%3A"
    assert len(dependency.depends_on) == 2
    assert "pkg:maven/org.springframework.boot/spring-boot-starter-data-rest@3.4.4?type=jar" in dependency.depends_on
    assert "pkg:maven/org.springframework.boot/spring-boot-starter-web@3.4.4?type=jar" in dependency.depends_on

    # Test helper methods
    assert sbom.get_component_by_ref("pkg:maven/au.com.patrick/spring-boot-demo-app@0.0.1-SNAPSHOT?project_path=%3A") == main_component
    assert sbom.get_component_by_ref("pkg:maven/com.fasterxml.jackson.core/jackson-annotations@2.18.3?type=jar") == component
    assert sbom.get_component_by_ref("non-existent-ref") is None

    deps = sbom.get_dependencies_for("pkg:maven/au.com.patrick/spring-boot-demo-app@0.0.1-SNAPSHOT?project_path=%3A")
    assert len(deps) == 2
    assert sbom.get_dependencies_for("non-existent-ref") == []


def test_minimal_sbom():
    # Test minimal JSON data
    json_data = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": "urn:uuid:test",
        "version": 1,
        "metadata": {
            "timestamp": "2025-04-23T00:00:00Z",
            "tools": {
                "components": [],
                "services": []
            },
            "component": {
                "type": "application",
                "bom-ref": "test-ref",
                "name": "test-app",
                "version": "1.0"
            }
        }
    }
    
    # Parse the JSON
    sbom = SBOM.model_validate(json_data)
    
    # Verify minimal SBOM
    assert sbom.bom_format == "CycloneDX"
    assert sbom.metadata.component.name == "test-app"
    assert len(sbom.components) == 0
    assert len(sbom.dependencies) == 0