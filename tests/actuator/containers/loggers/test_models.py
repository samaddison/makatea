from src.actuator.containers.loggers import Loggers, Logger, LoggerGroup


def test_loggers_model_parsing():
    # Test JSON data
    json_data = {
        "levels": ["OFF", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"],
        "loggers": {
            "ROOT": {"configuredLevel": "INFO", "effectiveLevel": "INFO"},
            "_org": {"effectiveLevel": "INFO"},
            "_org.springframework": {"effectiveLevel": "INFO"},
            "_org.springframework.web": {"effectiveLevel": "INFO"},
        },
        "groups": {
            "web": {
                "members": [
                    "org.springframework.core.codec",
                    "org.springframework.http",
                    "org.springframework.web",
                    "org.springframework.boot.actuate.endpoint.web",
                    "org.springframework.boot.web.servlet.ServletContextInitializerBeans",
                ]
            },
            "sql": {
                "members": [
                    "org.springframework.jdbc.core",
                    "org.hibernate.SQL",
                    "org.jooq.tools.LoggerListener",
                ]
            },
        },
    }

    # Parse the JSON
    loggers = Loggers.model_validate(json_data)

    # Test levels
    assert len(loggers.levels) == 6
    assert loggers.levels == ["OFF", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]

    # Test loggers
    logger_names = loggers.get_logger_names()
    assert len(logger_names) == 4
    assert "ROOT" in logger_names
    assert "_org" in logger_names
    assert "_org.springframework" in logger_names
    assert "_org.springframework.web" in logger_names

    # Test specific logger
    root_logger = loggers.get_logger("ROOT")
    assert isinstance(root_logger, Logger)
    assert root_logger.configured_level == "INFO"
    assert root_logger.effective_level == "INFO"

    org_logger = loggers.get_logger("_org")
    assert isinstance(org_logger, Logger)
    assert org_logger.configured_level is None
    assert org_logger.effective_level == "INFO"

    # Test groups
    group_names = loggers.get_group_names()
    assert len(group_names) == 2
    assert "web" in group_names
    assert "sql" in group_names

    # Test specific group
    web_group = loggers.get_group("web")
    assert isinstance(web_group, LoggerGroup)
    assert len(web_group.members) == 5
    assert "org.springframework.web" in web_group.members
    assert (
        "org.springframework.boot.web.servlet.ServletContextInitializerBeans"
        in web_group.members
    )

    # Test get_group_members
    sql_members = loggers.get_group_members("sql")
    assert len(sql_members) == 3
    assert "org.springframework.jdbc.core" in sql_members
    assert "org.hibernate.SQL" in sql_members
    assert "org.jooq.tools.LoggerListener" in sql_members

    # Test non-existent logger and group
    assert loggers.get_logger("non-existent-logger") is None
    assert loggers.get_group("non-existent-group") is None
    assert loggers.get_group_members("non-existent-group") == []


def test_empty_loggers():
    # Test minimal JSON data
    json_data = {"levels": [], "loggers": {}, "groups": {}}

    # Parse the JSON
    loggers = Loggers.model_validate(json_data)

    # Verify empty levels, loggers and groups
    assert len(loggers.levels) == 0
    assert len(loggers.get_logger_names()) == 0
    assert len(loggers.get_group_names()) == 0
