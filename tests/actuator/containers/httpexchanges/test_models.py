from datetime import datetime
from src.actuator.containers.httpexchanges import (
    HttpExchanges,
    HttpExchange,
    HttpRequest,
    HttpResponse,
)


def test_http_exchanges_model_parsing():
    # Test JSON data
    json_data = {
        "exchanges": [
            {
                "timestamp": "2025-04-23T11:00:15.553006200Z",
                "request": {
                    "uri": "http://localhost:9090/actuator/startup",
                    "method": "GET",
                    "headers": {
                        "host": ["localhost:9090"],
                        "connection": ["keep-alive"],
                        "user-agent": [
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/135.0.0.0"
                        ],
                    },
                },
                "response": {
                    "status": 200,
                    "headers": {
                        "Content-Type": [
                            "application/vnd.spring-boot.actuator.v3+json"
                        ],
                        "Transfer-Encoding": ["chunked"],
                    },
                },
                "timeTaken": "PT0.0150707S",
            }
        ]
    }

    # Parse the JSON
    http_exchanges = HttpExchanges.model_validate(json_data)

    # Test the number of exchanges
    assert len(http_exchanges.exchanges) == 1

    # Test exchange
    exchange = http_exchanges.exchanges[0]
    assert isinstance(exchange, HttpExchange)
    assert isinstance(exchange.timestamp, datetime)
    assert (
        exchange.timestamp.isoformat()[:19] == "2025-04-23T11:00:15"
    )  # Skip microseconds
    assert exchange.time_taken == "PT0.0150707S"

    # Test request
    request = exchange.request
    assert isinstance(request, HttpRequest)
    assert request.uri == "http://localhost:9090/actuator/startup"
    assert request.method == "GET"
    assert request.headers["host"] == ["localhost:9090"]
    assert request.headers["connection"] == ["keep-alive"]
    assert request.headers["user-agent"] == [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/135.0.0.0"
    ]

    # Test get_header helper method
    assert request.get_header("host") == "localhost:9090"
    assert request.get_header("HOST") == "localhost:9090"  # Case-insensitive
    assert request.get_header("missing") is None

    # Test response
    response = exchange.response
    assert isinstance(response, HttpResponse)
    assert response.status == 200
    assert response.headers["Content-Type"] == [
        "application/vnd.spring-boot.actuator.v3+json"
    ]
    assert response.headers["Transfer-Encoding"] == ["chunked"]

    # Test get_header helper method
    assert (
        response.get_header("Content-Type")
        == "application/vnd.spring-boot.actuator.v3+json"
    )
    assert (
        response.get_header("content-type")
        == "application/vnd.spring-boot.actuator.v3+json"
    )  # Case-insensitive
    assert response.get_header("missing") is None


def test_empty_http_exchanges():
    # Test empty JSON data
    json_data = {"exchanges": []}

    # Parse the JSON
    http_exchanges = HttpExchanges.model_validate(json_data)

    # Verify empty exchanges list
    assert len(http_exchanges.exchanges) == 0
