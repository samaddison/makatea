import pytest
from src.actuator.containers.conditions import Conditions, Context, ConditionEvaluation


def test_conditions_model_parsing():
    # Test JSON data
    json_data = {
        "contexts": {
            "spring-boot-demo-app": {
                "positiveMatches": {
                    "SpringBootAdminClientAutoConfiguration": [
                        {
                            "condition": "OnWebApplicationCondition",
                            "message": "@ConditionalOnWebApplication (required) found 'session' scope"
                        },
                        {
                            "condition": "SpringBootAdminClientEnabledCondition",
                            "message": "matched"
                        }
                    ],
                    "AuditAutoConfiguration": [
                        {
                            "condition": "OnPropertyCondition",
                            "message": "@ConditionalOnProperty (management.auditevents.enabled) matched"
                        },
                        {
                            "condition": "OnBeanCondition",
                            "message": "@ConditionalOnBean (types: org.springframework.boot.actuate.audit.AuditEventRepository; SearchStrategy: all) found bean 'auditEventRepository'"
                        }
                    ]
                },
                "negativeMatches": {
                    "AopAutoConfiguration.JdkDynamicAutoProxyConfiguration": [
                        {
                            "condition": "OnPropertyCondition",
                            "message": "@ConditionalOnProperty (spring.aop.proxy-target-class=false) did not find property 'proxy-target-class'"
                        }
                    ]
                },
                "unconditionalClasses": [
                    "org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration"
                ]
            }
        }
    }

    # Parse the JSON
    conditions = Conditions.model_validate(json_data)

    # Test contexts
    context_names = conditions.get_context_names()
    assert len(context_names) == 1
    assert "spring-boot-demo-app" in context_names

    # Test context
    context = conditions.get_context("spring-boot-demo-app")
    assert isinstance(context, Context)
    
    # Test positive configurations
    positive_configs = context.get_positive_configurations()
    assert len(positive_configs) == 2
    assert "SpringBootAdminClientAutoConfiguration" in positive_configs
    assert "AuditAutoConfiguration" in positive_configs

    # Test negative configurations
    negative_configs = context.get_negative_configurations()
    assert len(negative_configs) == 1
    assert "AopAutoConfiguration.JdkDynamicAutoProxyConfiguration" in negative_configs

    # Test unconditional classes
    assert len(context.unconditional_classes) == 1
    assert context.unconditional_classes[0] == "org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration"

    # Test specific positive configuration evaluations
    admin_matches = context.get_positive_matches("SpringBootAdminClientAutoConfiguration")
    assert len(admin_matches) == 2
    assert isinstance(admin_matches[0], ConditionEvaluation)
    assert admin_matches[0].condition == "OnWebApplicationCondition"
    assert admin_matches[0].message == "@ConditionalOnWebApplication (required) found 'session' scope"
    
    # Test specific negative configuration evaluations
    aop_matches = context.get_negative_matches("AopAutoConfiguration.JdkDynamicAutoProxyConfiguration")
    assert len(aop_matches) == 1
    assert isinstance(aop_matches[0], ConditionEvaluation)
    assert aop_matches[0].condition == "OnPropertyCondition"
    assert aop_matches[0].message.startswith("@ConditionalOnProperty")
    
    # Test non-existent context and configuration
    assert conditions.get_context("non-existent-context") is None
    assert context.get_positive_matches("non-existent-config") is None
    assert context.get_negative_matches("non-existent-config") is None


def test_empty_conditions():
    # Test empty JSON data
    json_data = {"contexts": {}}
    
    # Parse the JSON
    conditions = Conditions.model_validate(json_data)
    
    # Verify empty contexts
    assert len(conditions.get_context_names()) == 0