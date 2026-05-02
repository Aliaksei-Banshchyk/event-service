"""
Tests for EventService – events.py
Covers: create_event, list_events, get_event, get_events_by_date, update_event
"""

EVENT_PAYLOAD = {
    "event_date": "2025-09-01T10:00:00",
    "place": "Main Hall",
    "description": "A great event",
}


def test_create_event(client):
    c, _ = client
    resp = c.post("/api/events", json=EVENT_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["place"] == "Main Hall"
    assert data["description"] == "A great event"
    assert "id" in data


def test_create_event_no_description(client):
    c, _ = client
    resp = c.post("/api/events", json={"event_date": "2025-10-01T10:00:00", "place": "Outdoor Stage"})
    assert resp.status_code == 201
    assert resp.json()["description"] is None


def test_list_events(client):
    c, _ = client
    c.post("/api/events", json=EVENT_PAYLOAD)
    resp = c.get("/api/events")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_event_found(client):
    c, _ = client
    created = c.post("/api/events", json=EVENT_PAYLOAD).json()
    resp = c.get(f"/api/event/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_event_not_found(client):
    c, _ = client
    resp = c.get("/api/event/99999")
    assert resp.status_code == 404


def test_get_events_by_date_range(client):
    c, _ = client
    c.post("/api/events", json={"event_date": "2025-06-01T10:00:00", "place": "Park"})
    c.post("/api/events", json={"event_date": "2025-12-01T10:00:00", "place": "Arena"})
    resp = c.get("/api/event/byDate?from_date=2025-05-01T00:00:00&to_date=2025-07-01T00:00:00")
    assert resp.status_code == 200
    results = resp.json()
    assert all("2025-06" in r["event_date"] for r in results)


def test_get_events_by_date_no_filter(client):
    c, _ = client
    resp = c.get("/api/event/byDate")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_update_event(client):
    c, _ = client
    created = c.post("/api/events", json=EVENT_PAYLOAD).json()
    resp = c.patch(f"/api/events/{created['id']}", json={"place": "New Venue"})
    assert resp.status_code == 200
    assert resp.json()["place"] == "New Venue"


def test_update_event_not_found(client):
    c, _ = client
    resp = c.patch("/api/events/99999", json={"place": "Nowhere"})
    assert resp.status_code == 404


def test_health(client):
    c, _ = client
    resp = c.get("/health")
    assert resp.status_code == 200
    assert resp.json()["service"] == "EventService"
