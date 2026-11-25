import json
from pathlib import Path

from app.models import Service, Incident


DATA_DIR = Path("data")


def test_load_services():

    file_path = DATA_DIR / "services/services.json"

    with open(file_path) as f:
        data = json.load(f)

    services = [
        Service.model_validate(item)
        for item in data["services"]
    ]

    assert len(services) == 10


def test_load_incidents():

    file_path = DATA_DIR / "incidents/incidents.json"

    with open(file_path) as f:
        data = json.load(f)

    incidents = [
        Incident.model_validate(item)
        for item in data["incidents"]
    ]

    assert len(incidents) == 20