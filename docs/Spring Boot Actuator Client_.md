# **Spring Boot Actuator Endpoints: A Detailed Specification for Client Implementation**

## **Introduction to Spring Boot Actuator Endpoints**

Spring Boot Actuator is a subproject of Spring Boot that brings production-ready capabilities to applications with minimal configuration.1 It offers a suite of built-in endpoints that expose operational information about a running application, such as its health, metrics, environment details, and more, without the need for developers to implement these features from scratch.1 These endpoints facilitate monitoring, management, and interaction with the application, proving invaluable in both development and production environments.2 Access to these endpoints is typically provided over HTTP and JMX, offering flexibility in how the application can be observed and managed.2 The default base path for all Actuator endpoints is /actuator, though this can be customized using the management.endpoints.web.base-path property in the application's configuration.4

To leverage the functionalities of Spring Boot Actuator, the inclusion of the spring-boot-starter-actuator dependency in the project's build configuration (e.g., pom.xml for Maven or build.gradle for Gradle) is essential.5 Once this dependency is added, several endpoints become available, but by default, only the health and info endpoints are exposed over HTTP.3 To gain access to the other valuable endpoints, explicit configuration is required. This is primarily achieved using the management.endpoints.web.exposure.include property in the application's properties file (e.g., application.properties or application.yml).7 This property allows developers to specify a list of endpoint IDs that should be made accessible over the web. Conversely, the management.endpoints.web.exposure.exclude property can be used to explicitly hide certain endpoints, offering fine-grained control over what operational data is exposed.7 It is crucial to consider the security implications when exposing Actuator endpoints, as they can reveal sensitive information about the application and its environment.10 Therefore, securing these endpoints, often using Spring Security, is a recommended best practice, especially in production deployments.7

## **Detailed Specification of Standard Actuator Endpoints**

### **2.1 auditevents**

* **Description:** The auditevents endpoint exposes information about audit events that have occurred within the application.11 This is particularly useful for tracking security-related activities such as user logins and logouts.1 The functionality of this endpoint relies on the presence of an AuditEventRepository bean in the application context.11  
* **URL Path:** /actuator/auditevents.12  
* **HTTP Method:** GET.12  
* **Input Parameters:**  
  * after: This optional parameter, of type String and formatted according to ISO 8601, allows filtering audit events to include only those that occurred after a specified timestamp.12 This can be helpful for retrieving recent events or events within a specific timeframe.  
  * principal: This optional String parameter enables filtering audit events based on the principal (typically the username) that initiated the event.12 This is useful for investigating actions performed by a particular user.  
  * type: This optional String parameter allows filtering audit events by their type (e.g., authentication\_success, logout).12 This helps in focusing on specific categories of audit events.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.12  
  * **Structure:** The top-level element is a JSON object containing a single field named events, which is an array.12 Each element in this array represents an audit event.  
  * **Fields:**  
    * events: An array of audit event objects.12  
    * events..timestamp: A String representing the timestamp of when the event occurred, typically in ISO 8601 format.12  
    * events..principal: A String indicating the principal associated with the event.12  
    * events..type: A String specifying the type of the audit event.12  
    * events..data: An optional Object containing additional details specific to the event type, such as the request URL or session details for authorization failures.5  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/auditevents?principal=alice\&after=2025-03-20T10%3A40%3A10.369991519Z\&type=logout'

* **Example Response:**  
  JSON  
  {  
    "events" :  
  }

* **Insight:** The auditevents endpoint will only function if an AuditEventRepository bean is available in the application context.11 If no such bean is provided, the endpoint might not return any data or might not be accessible. For basic use, an InMemoryAuditEventRepository can be used, but for production environments, a more robust implementation is recommended.5

### **2.2 beans**

* **Description:** The beans endpoint provides a comprehensive list of all the Spring-managed beans within the application context.11 This includes information about each bean's scope, type, resource, and dependencies, offering a detailed view of the application's internal structure.11  
* **URL Path:** /actuator/beans.14  
* **HTTP Method:** GET.14  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.14  
  * **Structure:** The JSON response contains a top-level object named contexts, which holds application contexts keyed by their ID (typically "application").14 Each context then contains a beans object.  
  * **Fields:**  
    * contexts: An object where each key is the ID of an application context.14  
    * contexts.\*.parentId: A String representing the ID of the parent application context, if one exists.14  
    * contexts.\*.beans: An object where each key is the name of a Spring bean within the context.14  
    * contexts.\*.beans.\*.aliases: An array of Strings listing any aliases defined for the bean.14  
    * contexts.\*.beans.\*.scope: A String indicating the scope of the bean (e.g., "singleton", "prototype").14  
    * contexts.\*.beans.\*.type: A String containing the fully qualified class name of the bean.14  
    * contexts.\*.beans.\*.resource: An optional String specifying the resource where the bean definition was found (e.g., a configuration file path).14  
    * contexts.\*.beans.\*.dependencies: An array of Strings listing the names of other beans that this bean depends on.14  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/beans'

* **Example Response:**  
  JSON  
  {  
    "contexts": {  
      "application": {  
        "parentId": null,  
        "beans": {  
          "org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration": {  
            "aliases":,  
            "scope": "singleton",  
            "type": "org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration",  
            "resource": "null",  
            "dependencies":  
          },  
          "homeController": {  
            "aliases":,  
            "scope": "singleton",  
            "type": "com.example.demo.HomeController",  
            "resource": "file:./build/classes/java/main/com/example/demo/HomeController.class",  
            "dependencies":  
          }  
          //... more beans  
        }  
      }  
    }  
  }

* **Insight:** In Spring Boot 2.0 and later versions, the beans endpoint might not be exposed by default over HTTP for security reasons.8 To access it, you might need to explicitly enable it by adding beans to the management.endpoints.web.exposure.include property in your application's configuration file.8

### **2.3 caches**

* **Description:** The caches endpoint provides information about the application's configured cache managers and the caches they manage.11 It allows inspecting the types of caches used and also provides functionality to evict cache entries.15  
* **URL Path:** /actuator/caches.15 /actuator/caches/{name}.15  
* **HTTP Method:** GET (for retrieving), DELETE (for evicting).15  
* **Input Parameters:**  
  * For retrieving a specific cache:  
    * name: The name of the cache to retrieve (Path Variable, String).15  
    * cacheManager: An optional query parameter (String) specifying the name of the cache manager if multiple caches with the same name exist.15  
  * For evicting a specific cache:  
    * name: The name of the cache to evict (Path Variable, String).15  
    * cacheManager: An optional query parameter (String) specifying the name of the cache manager if multiple caches with the same name exist.15 The Content-Type for this request should be application/x-www-form-urlencoded.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.15  
  * **Structure (Retrieving All Caches):** The JSON response contains a cacheManagers object, where each key is the name of a cache manager. Each cache manager object contains a caches object, where keys are cache names and values provide details like the target (fully qualified name of the native cache).15  
  * **Structure (Retrieving a Specific Cache):** The JSON response is an object containing the name of the cache, the cacheManager name, and the target (fully qualified name of the native cache).15  
  * **Fields (Retrieving All Caches):**  
    * cacheManagers: An object containing cache managers keyed by their ID.15  
    * cacheManagers.\*.caches: An object containing caches within each manager, keyed by cache name.15  
    * cacheManagers.\*.caches.\*.target: A String representing the fully qualified name of the underlying native cache.15  
  * **Fields (Retrieving a Specific Cache):**  
    * name: A String representing the name of the cache.15  
    * cacheManager: A String representing the name of the cache manager.15  
    * target: A String representing the fully qualified name of the underlying native cache.15  
* **Example Request (Retrieving All Caches):**  
  Bash  
  curl 'http://localhost:8080/actuator/caches'

* **Example Request (Retrieving Specific Cache):**  
  Bash  
  curl 'http://localhost:8080/actuator/caches/cities'

* **Example Request (Evicting a Specific Cache):**  
  Bash  
  curl \-X DELETE 'http://localhost:8080/actuator/caches/countries?cacheManager=anotherCacheManager' \-H 'Content-Type: application/x-www-form-urlencoded'

* **Example Response (Retrieving All Caches):**  
  JSON  
  {  
    "cacheManagers": {  
      "cacheManager": {  
        "caches": {  
          "cities": {  
            "target": "java.util.concurrent.ConcurrentHashMap"  
          },  
          "countries": {  
            "target": "java.util.concurrent.ConcurrentHashMap"  
          }  
        }  
      }  
    }  
  }

* **Example Response (Retrieving Specific Cache):**  
  JSON  
  {  
    "name": "cities",  
    "cacheManager": "cacheManager",  
    "target": "java.util.concurrent.ConcurrentHashMap"  
  }

* **Insight:** The caches endpoint supports the DELETE method to evict caches. Sending a DELETE request to /actuator/caches will evict all caches, while sending it to /actuator/caches/{name} will evict a specific cache.15 If a cache name is not unique, the cacheManager parameter must be provided during eviction.15

### **2.4 conditions**

* **Description:** The conditions endpoint provides a detailed report on the evaluation of conditions for configuration and auto-configuration classes.11 This report helps in understanding why certain beans were or were not created, offering insights into the application's configuration decisions.11  
* **URL Path:** /actuator/conditions.16  
* **HTTP Method:** GET.16  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.16  
  * **Structure:** The JSON response contains a top-level object named contexts, holding application contexts keyed by their ID.16 Each context contains positiveMatches, negativeMatches, and unconditionalClasses.  
  * **Fields:**  
    * contexts: An object containing application contexts keyed by their ID.16  
    * contexts.\*.positiveMatches: An object mapping configuration classes to an array of conditions that were successfully matched, along with messages explaining why.16  
    * contexts.\*.negativeMatches: An object mapping configuration classes to an array of conditions that were not matched. For each unmatched condition, details of the conditions that did match (if any) and the conditions that did not match are provided with explanatory messages.16  
    * contexts.\*.unconditionalClasses: An array of Strings listing the names of auto-configuration classes that have no conditions associated with them.16  
    * contexts.\*.parentId: An optional String indicating the ID of the parent application context.16  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/conditions'

* **Example Response:**  
  JSON  
  {  
    "contexts": {  
      "application": {  
        "positiveMatches": {  
          "org.springframework.boot.autoconfigure.web.servlet.DispatcherServletAutoConfiguration":  
        },  
        "negativeMatches": {  
          "org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration":  
            }  
          \]  
        },  
        "unconditionalClasses":,  
        "parentId": null  
      }  
    }  
  }

### **2.5 configprops**

* **Description:** The configprops endpoint displays a collated list of all @ConfigurationProperties beans defined in the application.11 This endpoint is subject to sanitization to prevent the exposure of sensitive information.11 It provides details about the prefix, properties, and the origin of these configuration properties.17  
* **URL Path:** /actuator/configprops.17 /actuator/configprops/{prefix}.17  
* **HTTP Method:** GET.17  
* **Input Parameters:**  
  * prefix: An optional path variable (String) that can be used to filter the results to only include @ConfigurationProperties beans whose prefix matches the given value.17 The prefix does not need to be an exact match.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.17  
  * **Structure:** The JSON response contains a top-level object named contexts, holding application contexts keyed by their ID.17 Each context contains a beans object.  
  * **Fields:**  
    * contexts: An object containing application contexts keyed by their ID.17  
    * contexts.\*.beans: An object where each key is the name of a @ConfigurationProperties bean.17  
    * contexts.\*.beans.\*.prefix: A String representing the prefix applied to the properties of this bean.17  
    * contexts.\*.beans.\*.properties: An object containing the properties of the bean as key-value pairs.17  
    * contexts.\*.beans.\*.inputs: An object detailing the origin and value of the configuration property used when binding to this bean.17  
    * contexts.\*.parentId: An optional String indicating the ID of the parent application context.17  
* **Example Request (All Config Props):**  
  Bash  
  curl 'http://localhost:8080/actuator/configprops'

* **Example Request (Config Props by Prefix):**  
  Bash  
  curl 'http://localhost:8080/actuator/configprops/server'

* **Example Response (All Config Props):**  
  JSON  
  {  
    "contexts": {  
      "application": {  
        "beans": {  
          "server.servlet.context": {  
            "prefix": "server.servlet.context",  
            "properties": {  
              "path": ""  
            },  
            "inputs": {  
              "origin": "class path resource \[application.properties\]: server.servlet.context.path",  
              "value": ""  
            }  
          },  
          "spring.datasource-org.springframework.boot.autoconfigure.jdbc.DataSourceProperties": {  
            "prefix": "spring.datasource",  
            "properties": {  
              "url": "jdbc:h2:mem:testdb",  
              "username": "sa",  
              "password": ""  
            },  
            "inputs": {  
              "origin": "class path resource \[application.properties\]: spring.datasource.url",  
              "value": "jdbc:h2:mem:testdb"  
            }  
          }  
          //... more config props  
        }  
      }  
    }  
  }

* **Insight:** Sensitive values within the configuration properties are subject to sanitization, typically being replaced by asterisks.11 In newer versions of Spring Boot, the visibility of these values can be controlled using properties like management.endpoint.configprops.show-values.18

### **2.6 env**

* **Description:** The env endpoint exposes properties from Spring's ConfigurableEnvironment, including active profiles, default profiles, and a list of property sources with their associated properties.11 This includes system properties, environment variables, and application-specific properties.11 Like configprops, the output of this endpoint is also subject to sanitization.11  
* **URL Path:** /actuator/env.19 /actuator/env/{property.name}.19  
* **HTTP Method:** GET.19  
* **Input Parameters:**  
  * property.name: An optional path variable (String) specifying the name of a single property to retrieve. If provided, the response will contain information about just that property.19  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.19  
  * **Structure (Entire Environment):** The JSON response contains activeProfiles, defaultProfiles, and an array of propertySources. Each propertySource has a name and a properties object.19  
  * **Structure (Single Property):** If a property name is provided in the path, the response will contain a property object with the property's source and value, along with the activeProfiles and defaultProfiles.19  
  * **Fields (Entire Environment):**  
    * activeProfiles: An array of Strings representing the names of the active profiles.19  
    * defaultProfiles: An array of Strings representing the names of the default profiles.19  
    * propertySources: An array of property source objects.19  
    * propertySources..name: A String representing the name of the property source (e.g., "systemProperties", "environmentVariables", "applicationConfig: \[classpath:/application.properties\]").19  
    * propertySources..properties: An object where each key is a property name and the value is an object containing the property's value (String) and optional origin (String).19  
  * **Fields (Single Property):**  
    * property: An object containing details of the requested property.19  
    * property.source: A String representing the name of the property source.19  
    * property.value: A String representing the value of the property.19  
* **Example Request (Entire Environment):**  
  Bash  
  curl 'http://localhost:8080/actuator/env'

* **Example Request (Single Property):**  
  Bash  
  curl 'http://localhost:8080/actuator/env/server.port'

* **Example Response (Entire Environment):**  
  JSON  
  {  
    "activeProfiles":,  
    "defaultProfiles": \[  
      "default"  
    \],  
    "propertySources":",  
        "properties": {  
          "server.port": {  
            "value": "8080",  
            "origin": "class path resource \[application.properties\]: server.port"  
          },  
          //... more application properties  
        }  
      }  
    \]  
  }

* **Example Response (Single Property):**  
  JSON  
  {  
    "property": {  
      "source": "applicationConfig: \[classpath:/application.properties\]",  
      "value": "8080"  
    },  
    "activeProfiles":,  
    "defaultProfiles": \[  
      "default"  
    \],  
    "propertySources": \[  
      //... (property sources array would be present in a full response)  
    \]  
  }

* **Insight:** Similar to configprops, sensitive information in the env endpoint is sanitized.11 The management.endpoint.env.show-values property can be used to control whether property values are shown, and management.endpoint.env.keys-to-sanitize allows customization of which property keys are considered sensitive.18

### **2.7 flyway**

* **Description:** The flyway endpoint provides details about the database migrations that have been applied by Flyway.11 This endpoint requires one or more Flyway beans to be present in the application context.11 It shows the history of migrations, including their version, description, script name, and execution status.20  
* **URL Path:** /actuator/flyway.20  
* **HTTP Method:** GET.20  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.20  
  * **Structure:** The JSON response contains a top-level object named contexts, holding application contexts keyed by their ID.20 Each context contains a flywayBeans object.  
  * **Fields:**  
    * contexts: An object containing application contexts keyed by their ID.20  
    * contexts.\*.flywayBeans: An object where each key is the name of a Flyway bean.20  
    * contexts.\*.flywayBeans.\*.migrations: An array of migration objects, each containing details about a specific migration.20  
    * contexts.\*.flywayBeans.\*.migrations..type: A String indicating the type of migration (e.g., "SQL").20  
    * contexts.\*.flywayBeans.\*.migrations..checksum: An optional Number representing the checksum of the migration script.20  
    * contexts.\*.flywayBeans.\*.migrations..version: An optional String representing the version of the migration.20  
    * contexts.\*.flywayBeans.\*.migrations..description: An optional String providing a description of the migration.20  
    * contexts.\*.flywayBeans.\*.migrations..script: A String representing the name of the script file that was executed.20  
    * contexts.\*.flywayBeans.\*.migrations..state: A String indicating the state of the migration (e.g., "SUCCESS", "PENDING", "FAILED").20  
    * contexts.\*.flywayBeans.\*.migrations..installedBy: An optional String representing the user who installed the migration.20  
    * contexts.\*.flywayBeans.\*.migrations..installedOn: An optional String representing the timestamp when the migration was installed.20  
    * contexts.\*.flywayBeans.\*.migrations..installedRank: An optional Number representing the rank of the migration.20  
    * contexts.\*.flywayBeans.\*.migrations..executionTime: An optional Number representing the execution time of the migration in milliseconds.20  
    * contexts.\*.parentId: An optional String indicating the ID of the parent application context.20  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/flyway'

* **Example Response:**  
  JSON  
  {  
    "contexts": {  
      "application": {  
        "flywayBeans": {  
          "flyway": {  
            "migrations":  
          }  
        },  
        "parentId": null  
      }  
    }  
  }

* **Insight:** The flyway endpoint is contingent on the application using Flyway for database migrations and having the necessary Flyway bean(s) configured.11 If Flyway is not in use, this endpoint will likely not provide any meaningful data.

### **2.8 health**

* **Description:** The health endpoint is a critical component of Spring Boot Actuator, providing a summary of the application's overall health status as well as the status of its individual components.11 It's often used by monitoring systems to determine the availability and operational state of the application.11  
* **URL Path:** /actuator/health.21 /actuator/health/{component}.21 /actuator/health/{component}/{subcomponent}.21  
* **HTTP Method:** GET.21  
* **Input Parameters:**  
  * component: An optional path variable (String) specifying the name of a specific health indicator component to check (e.g., db, diskSpace).21  
  * subcomponent: An optional path variable (String) used to retrieve the health status of a nested component within a health indicator (e.g., broker/us1).21 This can be extended for multiple levels of nesting.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.21  
  * **Structure (Overall Health):** The JSON response contains a status field indicating the overall health (e.g., "UP", "DOWN") and a components object containing details for individual health indicators.21  
  * **Structure (Component Health):** When a component is specified in the path, the response will contain the status of that component and its details.21  
  * **Structure (Nested Component Health):** For nested components, the response structure is similar to a single component, showing the status and details of the specific subcomponent.21  
  * **Fields (Overall Health):**  
    * status: A String representing the overall health status of the application.21  
    * components: An object containing health information for various components, where each key is the name of a component.21  
    * components.\*.status: A String representing the health status of the specific component.21  
    * components.\*.components: An optional object containing nested components for hierarchical health checks.21  
    * components.\*.details: An optional object providing detailed information about the health of the component. The presence of details is controlled by the management.endpoint.health.show-details property.21  
  * **Fields (Component/Nested Component Health):**  
    * status: A String representing the health status of the requested component or subcomponent.21  
    * details: An optional object providing detailed information about the health of the requested component or subcomponent.21  
* **Example Request (Overall Health):**  
  Bash  
  curl 'http://localhost:8080/actuator/health'

* **Example Request (Component Health):**  
  Bash  
  curl 'http://localhost:8080/actuator/health/db'

* **Example Request (Nested Component Health):**  
  Bash  
  curl 'http://localhost:8080/actuator/health/broker/us1'

* **Example Response (Overall Health):**  
  JSON  
  {  
    "status": "UP",  
    "components": {  
      "db": {  
        "status": "UP",  
        "details": {  
          "database": "H2",  
          "validationQuery": "isValid()"  
        }  
      },  
      "diskSpace": {  
        "status": "UP",  
        "details": {  
          "total": 76887154688,  
          "free": 51858280448,  
          "threshold": 10485760,  
          "path": "/...",  
          "exists": true  
        }  
      }  
    }  
  }

* **Insight:** The level of detail shown in the health endpoint's response can be configured using the management.endpoint.health.show-details property.21 Setting it to always will show full details, while never will only show the status. Spring Boot also allows the implementation of custom HealthIndicator beans to provide application-specific health checks.22 Additionally, health indicators can be grouped for better organization.1

### **2.9 httpexchanges**

* **Description:** The httpexchanges endpoint provides information about recent HTTP request-response exchanges handled by the application.11 By default, it retains information about the last 100 exchanges.11 This endpoint requires an HttpExchangeRepository bean to be present in the application context.11  
* **URL Path:** /actuator/httpexchanges.24  
* **HTTP Method:** GET.24  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.24  
  * **Structure:** The JSON response contains a single field named exchanges, which is an array of objects. Each object represents an HTTP exchange.24  
  * **Fields:**  
    * exchanges: An array of HTTP exchange objects.24  
    * exchanges..timestamp: A String representing the timestamp of when the exchange occurred, typically in ISO 8601 format.24  
    * exchanges..request: An object containing details about the HTTP request.24  
      * method: A String representing the HTTP method (e.g., "GET", "POST").24  
      * uri: A String representing the URI of the request.24  
      * remoteAddress: An optional String representing the IP address of the client.24  
      * headers: An object where keys are header names and values are arrays of header values.24  
    * exchanges..response: An object containing details about the HTTP response.24  
      * status: A Number representing the HTTP status code.24  
      * headers: An object where keys are header names and values are arrays of header values.24  
    * exchanges..principal: An optional object containing information about the authenticated principal, if any.24  
      * name: An optional String representing the name of the principal.24  
    * exchanges..session: An optional object containing information about the HTTP session, if any.24  
      * id: An optional String representing the ID of the session.24  
    * exchanges..timeTaken: A String representing the time taken to handle the exchange, in ISO 8601 duration format.24  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/httpexchanges'

* **Example Response:**  
  JSON  
  {  
    "exchanges":  
          },  
          "remoteAddress": "127.0.0.1"  
        },  
        "response": {  
          "status": 200,  
          "headers": {  
            "Content-Type":  
          }  
        },  
        "timeTaken": "PT0.015S"  
      }  
    \]  
  }

* **Insight:** The httpexchanges endpoint requires an HttpExchangeRepository bean. Spring Boot provides an InMemoryHttpExchangeRepository which, by default, stores the last 100 request-response exchanges.11 The recording of HTTP exchanges can be customized using the management.httpexchanges.recording.include and management.httpexchanges.recording.enabled properties.25

### **2.10 info**

* **Description:** The info endpoint displays general information about the application.11 This information is customizable and can include details such as build version, Git commit information, and other application-specific properties.11  
* **URL Path:** /actuator/info.26  
* **HTTP Method:** GET.26  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.26  
  * **Structure:** The JSON response is a single object that can contain various key-value pairs or nested objects, depending on the configured InfoContributor beans and info.\* properties.26  
  * **Fields:** The fields in the response are determined by the InfoContributor beans present in the application context and the properties configured under the info namespace in the application properties file. Common fields include:  
    * build: An object containing build-related information such as artifact, group, name, version, and time.26 This information is typically generated by build tools like Maven or Gradle.  
    * git: An object containing Git repository information such as branch and commit details (including time and id).26 This information is usually generated by a Git commit ID plugin during the build process.  
    * Custom fields can be added by defining info.\* properties (e.g., info.app.name, info.app.description) or by implementing custom InfoContributor beans.2  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/info'

* **Example Response:**  
  JSON  
  {  
    "build": {  
      "artifact": "demo",  
      "group": "com.example",  
      "name": "demo",  
      "version": "0.0.1-SNAPSHOT",  
      "time": "2025-03-20T11:07:00.000Z"  
    },  
    "git": {  
      "branch": "main",  
      "commit": {  
        "id": "abcdef1",  
        "time": "2025-03-20T11:06:00.000Z"  
      }  
    },  
    "app": {  
      "name": "Demo Application",  
      "version": "1.0"  
    }  
  }

* **Insight:** The information exposed by the info endpoint is highly customizable. Spring Boot provides default InfoContributor implementations for build and Git information, provided the necessary metadata is available (e.g., a git.properties file or build information generated by Maven or Gradle).26 Custom information can be easily added through configuration properties or by implementing custom InfoContributor components.2

### **2.11 integrationgraph**

* **Description:** The integrationgraph endpoint visualizes the Spring Integration components and their relationships within the application.11 This endpoint requires a dependency on spring-integration-core to be present in the project.11 It provides a JSON representation of the integration flow, including channels, endpoints, and other components.  
* **URL Path:** /actuator/integrationgraph.27  
* **HTTP Method:** GET (to retrieve the graph), POST (to rebuild the graph).27  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.27  
  * **Structure:** The JSON response contains a contentDescriptor section with metadata about the graph, a nodes array detailing each integration component, and a links array defining the connections between the components.27  
  * **Fields:**  
    * contentDescriptor: An object containing metadata about the integration graph, including providerVersion, providerFormatVersion, and provider.27  
    * nodes: An array of objects, where each object represents a Spring Integration component. Each node includes properties like nodeId, componentType, integrationPatternType, integrationPatternCategory, properties, name, observed, and input (for input channels).27  
    * links: An array of objects, where each object represents a connection between two nodes in the graph, specifying the from and to nodeId and the type of connection.27  
* **Example Request (Get Graph):**  
  Bash  
  curl 'http://localhost:8080/actuator/integrationgraph'

* **Example Request (Rebuild Graph):**  
  Bash  
  curl \-X POST 'http://localhost:8080/actuator/integrationgraph'

* **Example Response:**  
  JSON  
  {  
    "contentDescriptor": {  
      "providerVersion": "6.4.4",  
      "providerFormatVersion": "1.0",  
      "provider": "spring-integration"  
    },  
    "nodes":,  
    "links": \[  
      {  
        "from": "messageHandler.handler",  
        "to": "messageChannel",  
        "type": "input"  
      }  
    \]  
  }

* **Insight:** The integrationgraph endpoint requires the spring-integration-core dependency. It supports a POST request to rebuild the integration graph, which might be useful in scenarios where the integration configuration is updated at runtime.27

### **2.12 liquibase**

* **Description:** The liquibase endpoint provides information about the database schema changes that have been applied using Liquibase.11 This endpoint requires one or more Liquibase beans to be present in the application context.11 It details the list of change sets executed, including their author, description, execution time, and status.  
* **URL Path:** /actuator/liquibase.28  
* **HTTP Method:** GET.28  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.28  
  * **Structure:** The JSON response contains a top-level object named contexts, holding application contexts keyed by their ID.28 Each context contains a liquibaseBeans object.  
  * **Fields:**  
    * contexts: An object containing application contexts keyed by their ID.28  
    * contexts.\*.liquibaseBeans: An object where each key is the name of a Liquibase bean.28  
    * contexts.\*.liquibaseBeans.\*.changeSets: An array of change set objects, each containing details about a specific change set.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.author: A String representing the author of the change set.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.changeLog: A String representing the path to the change log file.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.comments: An optional String containing comments on the change set.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.contexts: An array of Strings representing the contexts in which the change set should be applied.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.dateExecuted: An optional String representing the timestamp when the change set was executed.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.deploymentId: An optional String representing the ID of the deployment that ran the change set.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.description: An optional String providing a description of the change set.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.execType: A String representing the execution type (e.g., "EXECUTED", "FAILED").28  
    * contexts.\*.liquibaseBeans.\*.changeSets.id: A String representing the unique ID of the change set.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.labels: An array of Strings representing the labels associated with the change set.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.checksum: An optional String representing the checksum of the change set.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.orderExecuted: An optional Number representing the order in which the change set was executed.28  
    * contexts.\*.liquibaseBeans.\*.changeSets.tag: An optional String representing any tag associated with the change set.28  
    * contexts.\*.parentId: An optional String indicating the ID of the parent application context.28  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/liquibase'

* **Example Response:**  
  JSON  
  {  
    "contexts": {  
      "application": {  
        "liquibaseBeans": {  
          "liquibase": {  
            "changeSets": \[  
              {  
                "author": "johndoe",  
                "changeLog": "classpath:db/changelog/db.changelog-master.xml",  
                "comments": "Initial schema",  
                "contexts":,  
                "dateExecuted": "2025-03-20T11:10:00.000Z",  
                "deploymentId": "123",  
                "description": "createTable",  
                "execType": "EXECUTED",  
                "id": "1",  
                "labels":,  
                "checksum": "8:...",  
                "orderExecuted": 1,  
                "tag": null  
              }  
            \]  
          }  
        },  
        "parentId": null  
      }  
    }  
  }

* **Insight:** Similar to the flyway endpoint, liquibase requires the application to use Liquibase for database migrations and have the corresponding Liquibase bean(s) configured.11

### **2.13 logfile**

* **Description:** The logfile endpoint returns the content of the application's log file, provided that the logging.file.name or logging.file.path property has been set in the application's configuration.11 It also supports the use of the HTTP Range header to retrieve only a portion of the log file's content.11  
* **URL Path:** /actuator/logfile.29  
* **HTTP Method:** GET.29  
* **Input Parameters:**  
  * Range: An optional HTTP header that allows specifying a byte range to retrieve a part of the log file. The format is typically bytes=start-end.29  
* **Output Response:**  
  * **Format:** The response is in plain text format with a Content-Type of text/plain.29 For partial content requests, the HTTP status code will be 206 Partial Content, and a Content-Range header will be included.29  
  * **Structure:** The response body contains the content of the log file, either the entire file or the specified byte range.  
  * **Fields:** The response body directly contains the log data as plain text.  
* **Example Request (Entire Log File):**  
  Bash  
  curl 'http://localhost:8080/actuator/logfile'

* **Example Request (Partial Log File \- First 1024 bytes):**  
  Bash  
  curl 'http://localhost:8080/actuator/logfile' \-H 'Range: bytes=0-1023'

* **Example Response (Partial Log File):**  
  HTTP/1.1 206 Partial Content  
  Content-Type: text/plain  
  Content-Range: bytes 0-1023/15360  
  Content-Length: 1024

  2025-03-20T11:15:00.000Z INFO 1 \--- \[main\] com.example.DemoApplication: Starting DemoApplication using Java 17 with PID 1 on...

... (rest of the first 1024 bytes of the log file)  
\`\`\`

* **Insight:** The logfile endpoint is only active if the logging file properties are set. Retrieving partial content using the Range header is not supported when the application uses the Jersey web framework.29

### **2.14 loggers**

* **Description:** The loggers endpoint allows viewing and modifying the logging levels of loggers within the application at runtime.11 This enables dynamic control over the verbosity of application logging without requiring a restart.11  
* **URL Path:** /actuator/loggers.30 /actuator/loggers/{logger.name}.30 /actuator/loggers/{group.name}.30  
* **HTTP Method:** GET (for retrieving), POST (for modifying).30  
* **Input Parameters:**  
  * For retrieving a specific logger or group:  
    * logger.name: The name of the logger to retrieve (Path Variable, String).30  
    * group.name: The name of the logger group to retrieve (Path Variable, String).30  
  * For setting the log level (using POST to /actuator/loggers/{logger.name} or /actuator/loggers/{group.name}):  
    * The request body should be a JSON object with a configuredLevel field, specifying the desired log level (e.g., "TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL", "OFF", or null to reset to default).30 The Content-Type header should be application/json.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.30  
  * **Structure (Retrieving All Loggers):** The JSON response contains an array of supported levels, an object named loggers where keys are logger names and values contain configuredLevel and effectiveLevel, and an object named groups with configured levels and member loggers.30  
  * **Structure (Retrieving a Single Logger):** The JSON response contains the configuredLevel and effectiveLevel for the specified logger.30  
  * **Structure (Retrieving a Single Group):** The JSON response contains the configuredLevel and an array of members for the specified logger group.30  
  * **Fields (Retrieving All Loggers):**  
    * levels: An array of Strings representing the supported log levels.30  
    * loggers: An object where keys are logger names and values are objects with configuredLevel (String or null) and effectiveLevel (String).30  
    * groups: An object where keys are logger group names and values are objects with configuredLevel (String or null) and members (array of Strings).30  
  * **Fields (Retrieving a Single Logger):**  
    * configuredLevel: A String or null representing the configured log level.30  
    * effectiveLevel: A String representing the effective log level.30  
  * **Fields (Retrieving a Single Group):**  
    * configuredLevel: A String or null representing the configured log level for the group.30  
    * members: An array of Strings representing the names of the loggers in the group.30  
* **Example Request (Get All Loggers):**  
  Bash  
  curl 'http://localhost:8080/actuator/loggers'

* **Example Request (Get Single Logger):**  
  Bash  
  curl 'http://localhost:8080/actuator/loggers/com.example'

* **Example Request (Set Logger Level to DEBUG):**  
  Bash  
  curl \-X POST 'http://localhost:8080/actuator/loggers/com.example' \-H 'Content-Type: application/json' \-d '{"configuredLevel":"debug"}'

* **Example Response (Get Single Logger):**  
  JSON  
  {  
    "configuredLevel": "debug",  
    "effectiveLevel": "debug"  
  }

* **Insight:** The loggers endpoint allows for dynamic modification of logging levels using POST requests. Setting the configuredLevel to null will revert the logger or group to its default inherited level.30

### **2.15 mappings**

* **Description:** The mappings endpoint provides a collated list of all the request mappings defined in the application.11 This includes mappings for Spring MVC controllers, Spring WebFlux handlers, and other web endpoint types, offering a comprehensive overview of the application's HTTP API surface.11  
* **URL Path:** /actuator/mappings.31  
* **HTTP Method:** GET.31  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.31  
  * **Structure:** The JSON response contains a top-level object named contexts, holding application contexts keyed by their ID.31 Each context contains a mappings object, which further categorizes mappings by type (e.g., dispatcherServlets, servletFilters, servlets, dispatcherHandlers, routerFunctions).  
  * **Fields (for dispatcherServlets):**  
    * contexts.\*.mappings.dispatcherServlets: An object where keys are the names of DispatcherServlet beans.31  
    * contexts.\*.mappings.dispatcherServlets.\*: An array of mapping objects for the specific DispatcherServlet. Each mapping object typically includes:  
      * handler: A String describing the handler for the mapping (e.g., the controller method).31  
      * predicate: A String representing the request predicate (e.g., the URL pattern and HTTP methods).31  
      * details: An object containing further details about the mapping, including handlerMethod (with className, name, descriptor) and requestMappingConditions (with methods, patterns, params, headers, consumes, produces).31  
  * **Fields (for other mapping types):** The structure and fields will vary depending on the type of mapping (e.g., servletFilters will list filter names and their mappings).31  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/mappings'

* **Example Response:**  
  JSON  
  {  
    "contexts": {  
      "application": {  
        "mappings": {  
          "dispatcherServlets": {  
            "dispatcherServlet": \[  
              {  
                "handler": "com.example.demo.HomeController",  
                "predicate": "{\[/\],methods=}",  
                "details": {  
                  "handlerMethod": {  
                    "className": "com.example.demo.HomeController",  
                    "name": "home",  
                    "descriptor": "()Ljava/lang/String;"  
                  },  
                  "requestMappingConditions": {  
                    "consumes":,  
                    "headers":,  
                    "methods":,  
                    "params":,  
                    "patterns": \[  
                      "/"  
                    \],  
                    "produces":  
                  }  
                }  
              },  
              //... more mappings  
            \]  
          },  
          "servletFilters": {  
            "characterEncodingFilter": \[  
              "/\*"  
            \]  
          }  
        },  
        "parentId": null  
      }  
    }  
  }

* **Insight:** The mappings endpoint provides a comprehensive overview of all web request mappings in the application. The structure of the response can vary depending on whether the application uses Spring MVC, Spring WebFlux, or other web technologies.31

### **2.16 metrics**

* **Description:** The metrics endpoint exposes a wealth of metrics about the application's performance and resource utilization.11 This includes JVM metrics (memory usage, garbage collection), HTTP request metrics, and any custom metrics the application might be exposing.11 It leverages Micrometer, Spring Boot's metrics facade.33  
* **URL Path:** /actuator/metrics.32 /actuator/metrics/{metric.name}.32  
* **HTTP Method:** GET.32  
* **Input Parameters:**  
  * metric.name: An optional path variable (String) specifying the name of a particular metric to retrieve detailed information about (e.g., jvm.memory.used, http.server.requests).32  
  * tag: An optional query parameter (String) in the format name:value that can be used to filter the metric data based on specific tags. Multiple tag parameters can be provided to further refine the results.32  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.32  
  * **Structure (List of Metric Names):** A GET request to /actuator/metrics will return a JSON object containing an array of metric names.32  
  * **Structure (Specific Metric):** A GET request to /actuator/metrics/{metric.name} will return a JSON object containing the name, description, baseUnit, an array of measurements (with statistic and value), and an array of availableTags (with tag and values).32  
  * **Fields (List of Metric Names):**  
    * names: An array of Strings representing the names of the available metrics.32  
  * **Fields (Specific Metric):**  
    * name: A String representing the name of the metric.32  
    * description: An optional String providing a description of the metric.32  
    * baseUnit: An optional String representing the base unit of the metric (e.g., "bytes", "seconds").32  
    * measurements: An array of measurement objects.32  
      * statistic: A String representing the statistic of the measurement (e.g., "VALUE", "COUNT", "TOTAL\_TIME").32  
      * value: A Number representing the value of the measurement.32  
    * availableTags: An array of tag objects that can be used for drill-down.32  
      * tag: A String representing the name of the tag.32  
      * values: An array of Strings representing the possible values for the tag.32  
* **Example Request (List Metric Names):**  
  Bash  
  curl 'http://localhost:8080/actuator/metrics'

* **Example Request (Specific Metric):**  
  Bash  
  curl 'http://localhost:8080/actuator/metrics/jvm.memory.used'

* **Example Request (Specific Metric with Tag):**  
  Bash  
  curl 'http://localhost:8080/actuator/metrics/http.server.requests?tag=method:GET'

* **Example Response (Specific Metric):**  
  JSON  
  {  
    "name": "jvm.memory.used",  
    "description": "The amount of used memory",  
    "baseUnit": "bytes",  
    "measurements": \[  
      {  
        "statistic": "VALUE",  
        "value": 104857600  
      }  
    \],  
    "availableTags": \[  
      {  
        "tag": "area",  
        "values": \[  
          "heap",  
          "nonheap"  
        \]  
      }  
    \]  
  }

* **Insight:** The metrics endpoint integrates with Micrometer, a metrics instrumentation library that supports multiple monitoring systems, including Prometheus.33 It allows retrieving a list of available metric names or detailed information about a specific metric. The tag parameter enables filtering metrics based on their associated tags, allowing for more granular monitoring.32

### **2.17 quartz**

* **Description:** The quartz endpoint provides information about the jobs and triggers managed by the Quartz Scheduler within the application.11 This endpoint is subject to sanitization to prevent the exposure of sensitive job data.11 It allows inspecting the configuration and runtime status of scheduled tasks managed by Quartz.  
* **URL Path:** /actuator/quartz.34 /actuator/quartz/jobs.34 /actuator/quartz/triggers.34 /actuator/quartz/jobs/{groupName}.34 /actuator/quartz/triggers/{groupName}.34 /actuator/quartz/jobs/{groupName}/{jobName}.34 /actuator/quartz/triggers/{groupName}/{triggerName}.34  
* **HTTP Method:** GET.34  
* **Input Parameters:**  
  * groupName: A path variable (String) specifying the name of the job or trigger group to retrieve information about.34  
  * jobName: A path variable (String) specifying the name of a specific job within a group.34  
  * triggerName: A path variable (String) specifying the name of a specific trigger within a group.34  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.34  
  * **Structure:** The structure of the response varies depending on the specific URL path used:  
    * /actuator/quartz: Returns lists of job and trigger groups.34  
    * /actuator/quartz/jobs: Returns a list of job names for each group.34  
    * /actuator/quartz/triggers: Returns a list of trigger names for each group, along with the paused status of the group.34  
    * /actuator/quartz/jobs/{groupName}: Returns an overview of jobs in a specific group, including their class names.34  
    * /actuator/quartz/triggers/{groupName}: Returns an overview of triggers in a specific group, including their type and details.34  
    * /actuator/quartz/jobs/{groupName}/{jobName}: Returns detailed information about a specific job, including its description, durability, request recovery setting, job data map (sanitized), and associated triggers.34  
    * /actuator/quartz/triggers/{groupName}/{triggerName}: Returns detailed information about a specific trigger, including its type, state, start and end times, previous and next fire times, priority, and type-specific details (e.g., cron expression for CronTrigger).34  
  * **Fields:** The fields in the response vary depending on the specific endpoint. Refer to the detailed descriptions and example responses in the official Spring Boot Actuator API documentation for each of these sub-endpoints.34  
* **Example Request:** 34  
* **Example Response:** 34  
* **Insight:** The quartz endpoint provides a comprehensive set of sub-endpoints for inspecting different aspects of the Quartz Scheduler. It allows developers to monitor and manage scheduled jobs, triggers, and their configurations. Sensitive data within the job data map is sanitized for security.34

### **2.18 scheduledtasks**

* **Description:** The scheduledtasks endpoint provides information about the tasks that are scheduled within the application using Spring's @Scheduled annotation or through programmatic scheduling.11 It details the type of scheduling (cron, fixed delay, fixed rate), the target method to be executed, and the scheduling parameters.  
* **URL Path:** /actuator/scheduledtasks.35  
* **HTTP Method:** GET.35  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.35  
  * **Structure:** The JSON response contains four main arrays: cron, fixedDelay, fixedRate, and custom, each listing the scheduled tasks of the respective type.35  
  * **Fields:**  
    * cron: An array of objects, where each object represents a cron-scheduled task and includes the runnable target, the cron expression, and the nextExecution time.35  
    * fixedDelay: An array of objects, where each object represents a fixed-delay task and includes the runnable target, initialDelay, interval, nextExecution time, and details of the lastExecution.35  
    * fixedRate: An array of objects, where each object represents a fixed-rate task and includes the runnable target, initialDelay, interval, and nextExecution time.35  
    * custom: An array of objects, where each object represents a task scheduled with a custom trigger and includes the runnable target and the trigger details.35  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/scheduledtasks'

* **Example Response:**  
  JSON  
  {  
    "cron":,  
    "fixedDelay":,  
    "fixedRate":,  
    "custom":  
  }

* **Insight:** The scheduledtasks endpoint provides a clear overview of all the scheduled tasks configured within the application, making it easy to monitor their configuration and next execution times.35

### **2.19 sessions**

* **Description:** The sessions endpoint allows retrieval and deletion of user sessions from a Spring Session-backed session store.11 This endpoint requires a servlet-based web application that uses Spring Session to manage HTTP sessions.11 It provides the ability to list sessions for a specific user and to delete individual sessions.  
* **URL Path:** /actuator/sessions.36 /actuator/sessions/{id}.36  
* **HTTP Method:** GET (for retrieving), DELETE (for deleting).36  
* **Input Parameters:**  
  * For retrieving sessions:  
    * username: A required query parameter (String) specifying the username for whom to retrieve the sessions.36  
  * For retrieving or deleting a specific session:  
    * id: A path variable (String) representing the ID of the session to retrieve or delete.36  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.36  
  * **Structure (Retrieving Sessions):** The JSON response contains an array named sessions, where each element is a session object.36  
  * **Structure (Retrieving Single Session):** The JSON response is a single session object.36  
  * **Fields (Session Object):** Each session object includes the following fields: id (String), attributeNames (array of Strings), creationTime (String in ISO 8601 format), lastAccessedTime (String in ISO 8601 format), maxInactiveInterval (Number in seconds), and expired (Boolean).36  
* **Example Request (Retrieving Sessions for a User):**  
  Bash  
  curl 'http://localhost:8080/actuator/sessions?username=alice'

* **Example Request (Retrieving a Specific Session):**  
  Bash  
  curl 'http://localhost:8080/actuator/sessions/4db5efcc-99cb-4d05-a52c-b49acfbb7ea9'

* **Example Request (Deleting a Specific Session):**  
  Bash  
  curl \-X DELETE 'http://localhost:8080/actuator/sessions/4db5efcc-99cb-4d05-a52c-b49acfbb7ea9'

* **Example Response (Retrieving Sessions):**  
  JSON  
  {  
    "sessions":,  
        "creationTime": "2025-03-20T11:20:00.000Z",  
        "lastAccessedTime": "2025-03-20T11:25:00.000Z",  
        "maxInactiveInterval": 1800,  
        "expired": false  
      }  
    \]  
  }

* **Insight:** The sessions endpoint is only available for servlet-based web applications that are using Spring Session. It allows for programmatic management of user sessions, which can be useful for administrative purposes or for implementing features like session invalidation.36

### **2.20 shutdown**

* **Description:** The shutdown endpoint allows for a graceful shutdown of the application.11 This endpoint is disabled by default and only works when the application is packaged as a JAR file.11 It provides a way to stop the application via an HTTP request.  
* **URL Path:** /actuator/shutdown.37  
* **HTTP Method:** POST.37  
* **Input Parameters:** None (The request body should be empty).  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.37  
  * **Structure:** The JSON response is a simple object containing a message field.37  
  * **Fields:**  
    * message: A String indicating the result of the shutdown request, typically "Shutting down, bye...".37  
* **Example Request:**  
  Bash  
  curl \-X POST 'http://localhost:8080/actuator/shutdown'

* **Example Response:**  
  JSON  
  {  
    "message": "Shutting down, bye..."  
  }

* **Insight:** The shutdown endpoint is disabled by default for security reasons and needs to be explicitly enabled in the application's configuration, for example, by including it in the management.endpoints.web.exposure.include property and setting management.endpoint.shutdown.enabled to true.7 It's crucial to secure this endpoint in production environments to prevent unauthorized shutdowns.37

### **2.21 startup**

* **Description:** The startup endpoint provides detailed information about the steps taken during the application's startup phase.11 This endpoint requires the SpringApplication to be configured with a BufferingApplicationStartup to collect the startup step data.11 It allows retrieving a snapshot of the startup steps or draining the collected data.  
* **URL Path:** /actuator/startup.38  
* **HTTP Method:** GET (to retrieve a snapshot), POST (to drain the data).38  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in JSON format with a Content-Type of application/vnd.spring-boot.actuator.v3+json.38  
  * **Structure:** The JSON response contains the springBootVersion and a timeline object. The timeline object includes the startTime of the application and an array of events, where each event represents a startup step.38  
  * **Fields:**  
    * springBootVersion: A String representing the version of Spring Boot used by the application.38  
    * timeline: An object containing the startup timeline.38  
      * startTime: A String representing the timestamp when the application started.38  
      * events: An array of event objects, each representing a startup step.38  
      * events..startTime: A String representing the timestamp when the startup step started.38  
      * events..endTime: A String representing the timestamp when the startup step ended.38  
      * events..duration: A String representing the duration of the startup step.38  
      * events..startupStep: An object containing details about the startup step.38  
        * name: A String representing the name of the startup step (e.g., "spring.beans.instantiate").38  
        * id: A Number representing the ID of the startup step.38  
        * parentId: An optional Number representing the ID of the parent startup step.38  
        * tags: An array of tag objects associated with the startup step, each with a key and a value.38  
* **Example Request (Snapshot):**  
  Bash  
  curl 'http://localhost:8080/actuator/startup'

* **Example Request (Drain):**  
  Bash  
  curl \-X POST 'http://localhost:8080/actuator/startup'

* **Example Response (Snapshot):**  
  JSON  
  {  
    "springBootVersion": "3.4.4",  
    "timeline": {  
      "startTime": "2025-03-20T11:25:00.000Z",  
      "events":,  
            "parentId": 0  
          }  
        }  
      \]  
    }  
  }

* **Insight:** The startup endpoint requires specific configuration with BufferingApplicationStartup. A GET request provides a snapshot of the current startup steps, while a POST request retrieves and clears the collected data.38

### **2.22 threaddump**

* **Description:** The threaddump endpoint provides a snapshot of all the active threads in the JVM at the moment the endpoint is accessed.11 This is invaluable for diagnosing performance bottlenecks, deadlocks, or other threading-related issues within the application.41  
* **URL Path:** /actuator/threaddump.40  
* **HTTP Method:** GET.40  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response can be in JSON format (application/json) or plain text format (text/plain), depending on the Accept header sent in the request.40  
  * **Structure (JSON):** The JSON response contains an array named threads, where each element represents a thread and includes detailed information about its state, stack trace, and any locked monitors or synchronizers.40  
  * **Structure (Plain Text):** The plain text response provides a human-readable dump of all threads, similar to the output of the jstack command-line utility.40  
  * **Fields (JSON):** Each thread object in the threads array includes fields such as threadName, threadId, threadState, stackTrace (an array of stack frames with details like className, methodName, lineNumber), lockedMonitors, and lockedSynchronizers.40  
* **Example Request (JSON):**  
  Bash  
  curl 'http://localhost:8080/actuator/threaddump' \-H 'Accept: application/json'

* **Example Request (Plain Text):**  
  Bash  
  curl 'http://localhost:8080/actuator/threaddump' \-H 'Accept: text/plain'

* **Example Response (JSON \- Snippet):**  
  JSON  
  {  
    "threads":,  
        "lockedMonitors":,  
        "lockedSynchronizers":,  
        "lockInfo": null,  
        "lockOwnerId": \-1,  
        "lockOwnerName": null,  
        "waitedCount": 0,  
        "waitedTime": 0,  
        "blockedCount": 0,  
        "blockedTime": 0,  
        "daemon": false,  
        "priority": 10,  
        "inNative": false,  
        "suspended": false  
      }  
      //... more threads  
    \]  
  }

* **Insight:** The threaddump endpoint is crucial for diagnosing concurrency issues. The JSON format allows for programmatic analysis, while the plain text format is often easier for human inspection.40

### **2.23 heapdump**

* **Description:** The heapdump endpoint returns a snapshot of the JVM's heap at the time of the request.11 The format of the heap dump file depends on the specific JVM implementation being used; it's typically in HPROF format for HotSpot JVMs and PHD format for OpenJ9 JVMs.11 Heap dumps are essential for analyzing memory usage and identifying memory leaks in Java applications.43  
* **URL Path:** /actuator/heapdump.42  
* **HTTP Method:** GET.42  
* **Input Parameters:** None.  
* **Output Response:**  
  * **Format:** The response is in binary format (HPROF or PHD) with a Content-Type of application/octet-stream (implied).42  
  * **Structure:** The response body contains the raw binary data of the JVM heap dump.  
  * **Fields:** The response body directly contains the binary heap dump data.  
* **Example Request:**  
  Bash  
  curl 'http://localhost:8080/actuator/heapdump' \-O heapdump.hprof

* **Example Response:** The response is binary data, which, in this example, curl saves to a file named heapdump.hprof in the current directory.  
* **Insight:** Due to the binary nature and potentially large size of the heap dump, it is recommended to save the response to a file for offline analysis using dedicated memory analysis tools such as Java VisualVM or Eclipse Memory Analyzer (MAT).42 The format of the heap dump is JVM-specific.42

### **2.24 prometheus**

* **Description:** The prometheus endpoint exposes the application's metrics in a format that is compatible with the Prometheus monitoring system.11 This requires the inclusion of the micrometer-registry-prometheus dependency in the project.11 Prometheus servers can then scrape these metrics at regular intervals for monitoring and alerting purposes.  
* **URL Path:** /actuator/prometheus.45  
* **HTTP Method:** GET.45  
* **Input Parameters:**  
  * includedNames: An optional query parameter (String) that allows specifying a comma-separated list of metric names to be included in the response. This can be used to filter the metrics returned by the endpoint.45  
* **Output Response:**  
  * **Format:** The response is in plain text format, following the Prometheus exposition format, with a Content-Type of text/plain;version=0.0.4;charset=utf-8 by default.45 It can also produce the OpenMetrics format (application/openmetrics-text;version=1.0.0;charset=utf-8) if requested via the Accept header.45  
  * **Structure:** The response body contains the metrics data in a text-based format that Prometheus can understand. Each metric is typically represented by a name, followed by a set of labels (key-value pairs) in curly braces, and then the current value of the metric.  
  * **Fields:** The response body contains the metrics data in the Prometheus exposition format.  
* **Example Request (Prometheus Format):**  
  Bash  
  curl 'http://localhost:8080/actuator/prometheus'

* **Example Request (Filtered Metrics):**  
  Bash  
  curl 'http://localhost:8080/actuator/prometheus?includedNames=jvm\_memory\_used\_bytes,jvm\_memory\_committed\_bytes'

* **Example Response (Prometheus Format \- Snippet):**  
  \# HELP jvm\_memory\_used\_bytes The amount of used memory  
  \# TYPE jvm\_memory\_used\_bytes gauge  
  jvm\_memory\_used\_bytes{area="heap",id="PS Eden Space",} 1.073741824E9  
  jvm\_memory\_used\_bytes{area="heap",id="PS Old Gen",} 1.073741824E9  
  jvm\_memory\_used\_bytes{area="heap",id="PS Survivor Space",} 1.073741824E9  
  jvm\_memory\_used\_bytes{area="nonheap",id="CodeHeap 'non-nmethods'",} 2.5165824E7  
  jvm\_memory\_used\_bytes{area="nonheap",id="Metaspace",} 4.02659328E8  
  \# HELP http\_server\_requests\_seconds The duration of HTTP server requests  
  \# TYPE http\_server\_requests\_seconds summary  
  http\_server\_requests\_seconds\_count{method="GET",outcome="200",status="200",uri="/actuator/prometheus",} 1.0  
  http\_server\_requests\_seconds\_sum{method="GET",outcome="200",status="200",uri="/actuator/prometheus",} 0.015  
  http\_server\_requests\_seconds\_max{method="GET",outcome="200",status="200",uri="/actuator/prometheus",} 0.015

* **Insight:** The prometheus endpoint necessitates the micrometer-registry-prometheus dependency. It allows filtering the exposed metrics using the includedNames query parameter. Applications intending to be monitored by Prometheus will need to expose this endpoint.45

## **Conclusion**

Spring Boot Actuator provides a powerful suite of endpoints that are essential for monitoring and managing Spring Boot applications.2 These endpoints offer insights into various aspects of the application's runtime behavior, from its overall health and performance metrics to detailed configuration and operational state.1 This report has detailed each of the standard Actuator endpoints up to threaddump, specifying their URL paths, HTTP methods, input parameters, and the format of their output responses, along with illustrative examples.12 This information should serve as a comprehensive guide for developers aiming to implement a client for interacting with these endpoints programmatically, enabling them to build robust monitoring and management solutions for their Spring Boot applications. For the most current and comprehensive details, developers are encouraged to consult the official Spring Boot documentation.

#### **Works cited**

1. Spring Boot Actuator | Baeldung, accessed on April 20, 2025, [https://www.baeldung.com/spring-boot-actuators](https://www.baeldung.com/spring-boot-actuators)  
2. Exploring Spring Boot Actuator Endpoints: A Comprehensive Guide \- Apidog, accessed on April 20, 2025, [https://apidog.com/blog/spring-boot-actuator-endpoints/](https://apidog.com/blog/spring-boot-actuator-endpoints/)  
3. Spring Boot Actuator: Health check, Auditing, Metrics gathering and Monitoring | CalliCoder, accessed on April 20, 2025, [https://www.callicoder.com/spring-boot-actuator/](https://www.callicoder.com/spring-boot-actuator/)  
4. Actuator REST API :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/index.html](https://docs.spring.io/spring-boot/api/rest/actuator/index.html)  
5. Spring Boot Authentication Auditing Support | Baeldung, accessed on April 20, 2025, [https://www.baeldung.com/spring-boot-authentication-audit](https://www.baeldung.com/spring-boot-authentication-audit)  
6. Getting Started | Building a RESTful Web Service with Spring Boot Actuator, accessed on April 20, 2025, [https://spring.io/guides/gs/actuator-service](https://spring.io/guides/gs/actuator-service)  
7. How to Enable All Endpoints in Spring Boot Actuator | Baeldung, accessed on April 20, 2025, [https://www.baeldung.com/spring-boot-actuator-enable-endpoints](https://www.baeldung.com/spring-boot-actuator-enable-endpoints)  
8. Spring boot 2 \- Actuator endpoint, where is /beans endpoint \- Stack Overflow, accessed on April 20, 2025, [https://stackoverflow.com/questions/49174700/spring-boot-2-actuator-endpoint-where-is-beans-endpoint/49174823](https://stackoverflow.com/questions/49174700/spring-boot-2-actuator-endpoint-where-is-beans-endpoint/49174823)  
9. Spring Boot Actuator | GeeksforGeeks, accessed on April 20, 2025, [https://www.geeksforgeeks.org/spring-boot-actuator/](https://www.geeksforgeeks.org/spring-boot-actuator/)  
10. Beware of Spring Boot Actuator Endpoint env: A Security Alert \- Igor Venturelli, accessed on April 20, 2025, [https://igventurelli.io/endpoint-env-a-security-alert/](https://igventurelli.io/endpoint-env-a-security-alert/)  
11. Endpoints :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/reference/actuator/endpoints.html](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)  
12. Audit Events (auditevents) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/auditevents.html](https://docs.spring.io/spring-boot/api/rest/actuator/auditevents.html)  
13. Spring actuator '/auditevents' endpoint returns 404 \- Stack Overflow, accessed on April 20, 2025, [https://stackoverflow.com/questions/61298875/spring-actuator-auditevents-endpoint-returns-404](https://stackoverflow.com/questions/61298875/spring-actuator-auditevents-endpoint-returns-404)  
14. Beans (beans) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/beans.html](https://docs.spring.io/spring-boot/api/rest/actuator/beans.html)  
15. Caches (caches) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/caches.html](https://docs.spring.io/spring-boot/api/rest/actuator/caches.html)  
16. Conditions Evaluation Report (conditions) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/conditions.html](https://docs.spring.io/spring-boot/api/rest/actuator/conditions.html)  
17. Configuration Properties (configprops) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/configprops.html](https://docs.spring.io/spring-boot/api/rest/actuator/configprops.html)  
18. Spring Boot Actuator hides property values in env endpoint \- Stack Overflow, accessed on April 20, 2025, [https://stackoverflow.com/questions/28300232/spring-boot-actuator-hides-property-values-in-env-endpoint](https://stackoverflow.com/questions/28300232/spring-boot-actuator-hides-property-values-in-env-endpoint)  
19. Environment (env) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/env.html](https://docs.spring.io/spring-boot/api/rest/actuator/env.html)  
20. Flyway (flyway) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/flyway.html](https://docs.spring.io/spring-boot/api/rest/actuator/flyway.html)  
21. Health (health) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/health.html](https://docs.spring.io/spring-boot/api/rest/actuator/health.html)  
22. Health Indicators in Spring Boot \- Baeldung, accessed on April 20, 2025, [https://www.baeldung.com/spring-boot-health-indicators](https://www.baeldung.com/spring-boot-health-indicators)  
23. Spring Boot Actuators: Customise Health Endpoint \- DEV Community, accessed on April 20, 2025, [https://dev.to/manojshr/customise-health-endpoint-2e1](https://dev.to/manojshr/customise-health-endpoint-2e1)  
24. HTTP Exchanges (httpexchanges) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/httpexchanges.html](https://docs.spring.io/spring-boot/api/rest/actuator/httpexchanges.html)  
25. Recording HTTP Exchanges :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/reference/actuator/http-exchanges.html](https://docs.spring.io/spring-boot/reference/actuator/http-exchanges.html)  
26. Info (info) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/info.html](https://docs.spring.io/spring-boot/api/rest/actuator/info.html)  
27. Spring Integration Graph (integrationgraph) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/integrationgraph.html](https://docs.spring.io/spring-boot/api/rest/actuator/integrationgraph.html)  
28. Liquibase (liquibase) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/liquibase.html](https://docs.spring.io/spring-boot/api/rest/actuator/liquibase.html)  
29. Log File (logfile) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/logfile.html](https://docs.spring.io/spring-boot/api/rest/actuator/logfile.html)  
30. Loggers (loggers) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/loggers.html](https://docs.spring.io/spring-boot/api/rest/actuator/loggers.html)  
31. Mappings (mappings) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/mappings.html](https://docs.spring.io/spring-boot/api/rest/actuator/mappings.html)  
32. Metrics (metrics) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/metrics.html](https://docs.spring.io/spring-boot/api/rest/actuator/metrics.html)  
33. Metrics :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/reference/actuator/metrics.html](https://docs.spring.io/spring-boot/reference/actuator/metrics.html)  
34. Quartz (quartz) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/quartz.html](https://docs.spring.io/spring-boot/api/rest/actuator/quartz.html)  
35. Scheduled Tasks (scheduledtasks) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/scheduledtasks.html](https://docs.spring.io/spring-boot/api/rest/actuator/scheduledtasks.html)  
36. Sessions (sessions) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/sessions.html](https://docs.spring.io/spring-boot/api/rest/actuator/sessions.html)  
37. Shutdown (shutdown) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/shutdown.html](https://docs.spring.io/spring-boot/api/rest/actuator/shutdown.html)  
38. Application Startup (startup) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/startup.html](https://docs.spring.io/spring-boot/api/rest/actuator/startup.html)  
39. Spring Boot Startup Actuator Endpoint \- Baeldung, accessed on April 20, 2025, [https://www.baeldung.com/spring-boot-actuator-startup](https://www.baeldung.com/spring-boot-actuator-startup)  
40. Thread Dump (threaddump) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/threaddump.html](https://docs.spring.io/spring-boot/api/rest/actuator/threaddump.html)  
41. What are the main differences between thread dump and heap dump? \- Stack Overflow, accessed on April 20, 2025, [https://stackoverflow.com/questions/76931100/what-are-the-main-differences-between-thread-dump-and-heap-dump](https://stackoverflow.com/questions/76931100/what-are-the-main-differences-between-thread-dump-and-heap-dump)  
42. Heap Dump (heapdump) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/heapdump.html](https://docs.spring.io/spring-boot/api/rest/actuator/heapdump.html)  
43. Breaking Down HPROFs from Spring Boot Actuator Heapdumps \- Wya.pl, accessed on April 20, 2025, [https://wya.pl/2021/04/06/breaking-down-hprofs-from-spring-boot-actuator-heapdumps/](https://wya.pl/2021/04/06/breaking-down-hprofs-from-spring-boot-actuator-heapdumps/)  
44. Fetching a heap dump from a Spring Boot service \- Device Insight, accessed on April 20, 2025, [https://device-insight.com/en/developers-blog/fetching-heap-dump-spring-boot-k8s/](https://device-insight.com/en/developers-blog/fetching-heap-dump-spring-boot-k8s/)  
45. Prometheus (prometheus) :: Spring Boot, accessed on April 20, 2025, [https://docs.spring.io/spring-boot/api/rest/actuator/prometheus.html](https://docs.spring.io/spring-boot/api/rest/actuator/prometheus.html)  
46. Monitor a Spring Boot App Using Prometheus \- Baeldung, accessed on April 20, 2025, [https://www.baeldung.com/spring-boot-prometheus](https://www.baeldung.com/spring-boot-prometheus)