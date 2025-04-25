from src.actuator.containers.beans import Beans, Bean, Context


def test_beans_model_parsing():
    # Test JSON data
    json_data = {
        "contexts": {
            "spring-boot-demo-app": {
                "beans": {
                    "pagedResourcesAssembler": {
                        "aliases": [],
                        "scope": "singleton",
                        "type": "org.springframework.data.web.PagedResourcesAssembler",
                        "resource": "class path resource [org/springframework/data/rest/webmvc/config/RepositoryRestMvcConfiguration.class]",
                        "dependencies": [
                            "org.springframework.data.rest.webmvc.config.RepositoryRestMvcConfiguration"
                        ],
                    },
                    "applicationTaskExecutor": {
                        "aliases": ["taskExecutor"],
                        "scope": "singleton",
                        "type": "org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor",
                        "resource": "class path resource [org/springframework/boot/autoconfigure/task/TaskExecutorConfigurations$TaskExecutorConfiguration.class]",
                        "dependencies": [
                            "org.springframework.boot.autoconfigure.task.TaskExecutorConfigurations$TaskExecutorConfiguration",
                            "threadPoolTaskExecutorBuilder",
                        ],
                    },
                }
            }
        }
    }

    # Parse the JSON
    beans = Beans.model_validate(json_data)

    # Test contexts
    context_names = beans.get_context_names()
    assert len(context_names) == 1
    assert "spring-boot-demo-app" in context_names

    # Test context and beans
    context = beans.contexts["spring-boot-demo-app"]
    assert isinstance(context, Context)

    bean_names = beans.get_bean_names("spring-boot-demo-app")
    assert len(bean_names) == 2
    assert "pagedResourcesAssembler" in bean_names
    assert "applicationTaskExecutor" in bean_names

    # Test specific bean details
    bean1 = beans.get_bean("spring-boot-demo-app", "pagedResourcesAssembler")
    assert isinstance(bean1, Bean)
    assert bean1.scope == "singleton"
    assert bean1.type == "org.springframework.data.web.PagedResourcesAssembler"
    assert len(bean1.aliases) == 0
    assert len(bean1.dependencies) == 1
    assert (
        bean1.dependencies[0]
        == "org.springframework.data.rest.webmvc.config.RepositoryRestMvcConfiguration"
    )

    bean2 = beans.get_bean("spring-boot-demo-app", "applicationTaskExecutor")
    assert isinstance(bean2, Bean)
    assert bean2.scope == "singleton"
    assert (
        bean2.type == "org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor"
    )
    assert len(bean2.aliases) == 1
    assert bean2.aliases[0] == "taskExecutor"
    assert len(bean2.dependencies) == 2

    # Test non-existent context and bean
    assert beans.get_bean_names("non-existent-context") == []
    assert beans.get_bean("spring-boot-demo-app", "non-existent-bean") is None
    assert beans.get_bean("non-existent-context", "pagedResourcesAssembler") is None
