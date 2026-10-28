import requests

BASE_URL = "https://restful-booker.herokuapp.com"

PAYLOAD = {
    "firstname": "Testy",
    "lastname": "McTest",
    "totalprice": 123,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-11-01", "checkout": "2026-11-05"},
    "additionalneeds": "Breakfast",
}


def test_create_then_get_booking():
    # json= serializes the dict; Accept picks JSON since the API can also answer in XML
    created = requests.post(
        f"{BASE_URL}/booking",
        json=PAYLOAD,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=10,
    )
    assert created.status_code == 200, created.text
    booking_id = created.json()["bookingid"]
    assert isinstance(booking_id, int)

    # Creates its own booking each run, so it never depends on existing data and needs no manual cleanup
    fetched = requests.get(
        f"{BASE_URL}/booking/{booking_id}",
        headers={"Accept": "application/json"},
        timeout=10,
    )
    assert fetched.status_code == 200, fetched.text
    assert fetched.json() == PAYLOAD
