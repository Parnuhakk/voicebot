"""Only the robot website publishes the restaurant reception."""

from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest

from tests.test_restaurant_http import client  # noqa: F401


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
    response = client.get("/", headers={"Host": "robot.arleserver.cfd"})
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
