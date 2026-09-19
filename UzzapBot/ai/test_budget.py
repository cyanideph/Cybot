from ai.budget import request_budget_available, response_budget_available


def test_request_budget_stops_at_daily_limit():
    assert request_budget_available({"requests_day": 99}, 100)
    assert not request_budget_available({"requests_day": 100}, 100)


def test_response_budget_enforces_hourly_and_daily_limits():
    assert response_budget_available(
        {"messages_hour": 2, "messages_day": 5}, 3, 20
    )
    assert not response_budget_available(
        {"messages_hour": 3, "messages_day": 5}, 3, 20
    )
    assert not response_budget_available(
        {"messages_hour": 2, "messages_day": 20}, 3, 20
    )
