"""
test_events.py – EventService
Place at the ROOT of the event-service repo.
Run with: pytest test_events.py -v
"""
import pytest


EVENT_PAYLOAD = {
    "event_date": "2025-09-01T10:00:00",
    "place": "Vilnius Central Park",
    "description": "Tree planting day",
}


# ── /health ───────────────────────────────────────────────────────────────────

def test_health(client):
    c, _ = client
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── POST /api/events ──────────────────────────────────────────────────────────

def test_create_event_success(client):
    c, _ = client
    r = c.post("/api/events", json=EVENT_PAYLOAD)
    assert r.status_code == 201
    data = r.json()
    assert data["place"] == "Vilnius Central Park"
    assert data["description"] == "Tree planting day"
    assert "id" in data


def test_create_event_no_description(client):
    c, _ = client
    r = c.post("/api/events", json={
        "event_date": "2025-10-01T10:00:00",
        "place": "Kaunas Arena",
    })
    assert r.status_code == 201
    assert r.json()["description"] is None


def test_create_event_missing_place(client):
    c, _ = client
    r = c.post("/api/events", json={"event_date": "2025-10-01T10:00:00"})
    assert r.status_code == 422


# ── GET /api/events ───────────────────────────────────────────────────────────

def test_list_events_empty(client):
    c, _ = client
    r = c.get("/api/events")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_events_returns_created(client):
    c, _ = client
    c.post("/api/events", json=EVENT_PAYLOAD)
    c.post("/api/events", json={**EVENT_PAYLOAD, "place": "Kaunas"})
    r = c.get("/api/events")
    assert r.status_code == 200
    assert len(r.json()) >= 2


# ── GET /api/event/{id} ───────────────────────────────────────────────────────

def test_get_event_success(client):
    c, _ = client
    created = c.post("/api/events", json=EVENT_PAYLOAD)
    event_id = created.json()["id"]
    r = c.get(f"/api/event/{event_id}")
    assert r.status_code == 200
    assert r.json()["id"] == event_id


def test_get_event_not_found(client):
    c, _ = client
    r = c.get("/api/event/99999")
    assert r.status_code == 404


# ── GET /api/event/byDate ─────────────────────────────────────────────────────

def test_events_by_date_range(client):
    c, _ = client
    c.post("/api/events", json={**EVENT_PAYLOAD, "event_date": "2026-01-15T10:00:00"})
    c.post("/api/events", json={**EVENT_PAYLOAD, "event_date": "2026-03-20T10:00:00"})
    r = c.get("/api/event/byDate?from_date=2026-01-01T00:00:00&to_date=2026-02-01T00:00:00")
    assert r.status_code == 200
    results = r.json()
    assert all("2026-01" in e["event_date"] for e in results)


def test_events_by_date_no_params(client):
    c, _ = client
    r = c.get("/api/event/byDate")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── PATCH /api/events/{id} ────────────────────────────────────────────────────

def test_update_event_place(client):
    c, _ = client
    created = c.post("/api/events", json=EVENT_PAYLOAD)
    event_id = created.json()["id"]
    r = c.patch(f"/api/events/{event_id}", json={"place": "New Venue"})
    assert r.status_code == 200
    assert r.json()["place"] == "New Venue"


def test_update_event_description(client):
    c, _ = client
    created = c.post("/api/events", json=EVENT_PAYLOAD)
    event_id = created.json()["id"]
    r = c.patch(f"/api/events/{event_id}", json={"description": "Updated desc"})
    assert r.status_code == 200
    assert r.json()["description"] == "Updated desc"


def test_update_event_not_found(client):
    c, _ = client
    r = c.patch("/api/events/99999", json={"place": "Nowhere"})
    assert r.status_code == 404
