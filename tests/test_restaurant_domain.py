"""Restobot publishes the landing and preserved private restaurant workspace."""

from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest

pytest_plugins = ["tests.test_restaurant_http"]
RETIRED_HOST = "meretuule.arleserver.cfd"


class DemoLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.destinations = []

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "a" and attributes.get("href"):
            self.destinations.append(attributes.get("href"))


def test_robot_reception_does_not_link_to_the_removed_demo_site(client):
    response = client.get("/dashboard", headers={"Host": "restobot.arleserver.cfd"})
    assert response.status_code == 200
    links = DemoLinks()
    links.feed(response.text)
    assert links.destinations
    assert all(
        urlsplit(destination).hostname != RETIRED_HOST
        for destination in links.destinations
    ), "Robot navigation still advertises the removed demo website"
    assert 'id="operator-token"' in response.text
    assert 'id="reservation-prepare"' in response.text
    assert 'id="demo-start"' in response.text
    assert 'id="demo-mic"' in response.text


@pytest.mark.parametrize("host", ["robot.arleserver.cfd", "ROBOT.ARLESERVER.CFD."])
@pytest.mark.parametrize(
    "path", ["/", "/index.html", "/dashboard", "/dashboard/", "/booking-calendar.html"]
)
def test_old_browser_pages_redirect_to_restobot_preserving_query(client, host, path):
    response = client.get(
        path + "?source=calendar&language=et",
        headers={"Host": host},
        follow_redirects=False,
    )
    assert response.status_code == 308
    assert (
        response.headers["Location"]
        == "https://restobot.arleserver.cfd" + path + "?source=calendar&language=et"
    )
    assert response.headers["Cache-Control"] == "no-store"


def test_canonical_landing_and_workspace_are_distinct(client):
    landing = client.get("/", headers={"Host": "restobot.arleserver.cfd"})
    workspace = client.get("/dashboard", headers={"Host": "restobot.arleserver.cfd"})
    assert landing.status_code == workspace.status_code == 200
    links = DemoLinks()
    links.feed(landing.text)
    assert "/dashboard#demo-section" in links.destinations
    assert "/booking-calendar.html" in links.destinations
    assert 'id="operator-token"' not in landing.text
    assert 'id="operator-token"' in workspace.text


def test_old_host_api_is_not_redirected_or_authorized_by_the_migration(client):
    headers = {"Host": "robot.arleserver.cfd"}
    assert (
        client.get("/health", headers=headers, follow_redirects=False).status_code
        == 200
    )
    response = client.post(
        "/api/restaurant/reservation/prepare",
        content=b"not-json",
        headers=headers,
        follow_redirects=False,
    )
    assert response.status_code == 403
    assert "Location" not in response.headers
    assert response.headers["Cache-Control"] == "no-store"


def test_canonical_workspace_supports_head_without_exposing_a_body(client):
    response = client.head("/dashboard", headers={"Host": "restobot.arleserver.cfd"})
    assert response.status_code == 200
    assert response.content == b""
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize("host", [RETIRED_HOST, "MERETUULE.ARLESERVER.CFD."])
@pytest.mark.parametrize(
    "path",
    ["/", "/restaurant.js", "/api/public/restaurant", "/api/bookings", "/health"],
)
def test_retired_hostname_cannot_serve_any_part_of_the_app(client, host, path):
    response = client.get(path, headers={"Host": host}, follow_redirects=False)
    assert response.status_code == 410, f"Retired hostname still serves {path}"
    assert response.content == b""
    assert "Location" not in response.headers
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize("path", ["/hotel", "/hotel/"])
def test_retired_hotel_paths_do_not_redirect_to_the_removed_domain(client, path):
    response = client.get(
        path + "?source=legacy",
        headers={"Host": "robot.arleserver.cfd"},
        follow_redirects=False,
    )
    assert response.status_code == 410
    assert "Location" not in response.headers


def test_robot_health_and_restaurant_data_remain_available(client):
    headers = {"Host": "robot.arleserver.cfd"}
    assert client.get("/health", headers=headers).json()["ok"] is True
    assert client.get("/api/public/restaurant", headers=headers).status_code == 200
    response = client.get("/api/bookings", headers=headers)
    assert response.status_code == 403
    assert response.headers["Cache-Control"] == "no-store"
