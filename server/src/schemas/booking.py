from pydantic import BaseModel, ConfigDict

from src.schemas.venue import VenueItem


class BookingItem(BaseModel):
    id: int
    venue_id: int
    user_id: str
    first_name: str
    last_name: str
    venue: VenueItem

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    venue_id: int
    user_id: int
    first_name: str
    last_name: str
