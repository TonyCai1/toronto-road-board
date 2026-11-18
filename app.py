import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "road_restrictions.json"


def format_date(value: str) -> str:
    parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    return f"{parsed.strftime('%b')} {parsed.day}, {parsed.year}"


def load_restrictions() -> list[dict]:
    with DATA_FILE.open(encoding="utf-8") as data_file:
        saved_response = json.load(data_file)

    restrictions = []
    for feature in saved_response["features"]:
        restriction = deepcopy(feature["attributes"])
        restriction["display_start"] = format_date(restriction["PLAN_START_LOCAL"])
        restriction["display_end"] = format_date(restriction["PLAN_END_LOCAL"])
        restriction["location"] = (
            f'{restriction["FROM_ROAD"]} to {restriction["TO_ROAD"]}'
        )
        restriction["badge"] = (
            "Road closed"
            if "full closure" in restriction["DESCRIPTION"].lower()
            else "Lane restriction"
        )
        restrictions.append(restriction)

    return restrictions


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html", restrictions=load_restrictions())

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
