from pydantic import BaseModel, Field


class Booking(BaseModel):
    """
    Booking request for a class.

    - `class_id`: The ID of the class to book.
    """

    class_id: str = Field(..., description="ID of the class to book")

    # @model_validator(mode="after")
    # def record_booking_date_and_time(self):
    #     self._booked_at = datetime.now(UTC).isoformat()
    #     return self
