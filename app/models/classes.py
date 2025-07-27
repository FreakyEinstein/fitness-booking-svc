from pydantic import BaseModel, Field
import uuid

from ..config import Settings

settings = Settings()


class Class(BaseModel):
    """
    Represents a fitness class session.

    - `datetime_of_class`: Input as IST ISO string (e.g. "2025-07-28T05:30:00").
      This will be stored as UTC ISO string internally.
    """

    id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="Unique class ID")
    name: str = Field(..., description="Name of the class")
    datetime_of_class: str = Field(
        ...,
        description="Date and time of the class in IST ISO format (e.g. '2025-07-28T05:30:00').",
    )
    # instructor: str = Field(..., description="Instructor name")
    total_slots: int = Field(10, description="Total slots available")
    duration_in_hours: int = Field(1, description="Duration of class in hours")
