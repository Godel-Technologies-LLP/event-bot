from pydantic import BaseModel
from typing import List, Any, Union, Text
from rasa.nlu.utils import write_json_to_file
import json
import os
from pathlib import Path
from rasa.shared.exceptions import (
    FileIOException,
    FileNotFoundException,
)

DB_FILE = "db/bookings.json"
from actions.utils import EventDetails


class Booking(BaseModel):
    email: str
    event_details: EventDetails


def get_bookings() -> List[Booking]:
    return [Booking(**item) for item in read_db(DB_FILE)]


def read_db(db_file: str) -> Any:
    return read_json_file(db_file)


def save_booking(booking: Booking) -> None:
    bookings = get_bookings()
    bookings.append(booking)
    write_db(DB_FILE, [b.dict() for b in bookings])


def write_db(db_file: str, data: Any) -> None:
    write_json_to_file(db_file, data)


def read_json_file(filename: Union[Text, Path]) -> Any:
    """Read json from a file."""
    content = read_file(filename)
    if not content.strip():
        return {}
    try:
        return json.loads(content)
    except ValueError as e:
        raise FileIOException(
            f"Failed to read json from '{os.path.abspath(filename)}'. Error: {e}"
        )


def read_file(filename: Union[Text, Path]) -> str:
    # Assuming this function reads the content of a file
    with open(filename, "r") as file:
        return file.read()
