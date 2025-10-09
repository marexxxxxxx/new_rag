from pydantic import BaseModel
from typing import Union, Annotated, Field, Optional, TypedDict
from langgraph.graph import StateGraph

class state(TypedDict):
    counter: Annotated[int, "Number of how many iterations"]
    current_obj: Annotated[str,"Object with the current event"]
    ergebnisse: Annotated[list, "Object with all of the events"]
    list_with_text: Annotated[list, "List with Objects to check"]



class isevent(BaseModel):
    is_event: Annotated[bool,"Is the given text a event"]

class ActivityListing(BaseModel):
    """
    A concise Pydantic model for an activity listing.
    """
    title: str = Field(..., description="The name of the activity.")
    rating_average: float = Field(..., description="The average star rating (e.g., 4.3).")
    rating_count: int = Field(..., description="The total number of ratings (e.g., 1157).")
    price_value: float = Field(..., description="The base price (e.g., 140).")
    price_currency: str = Field(..., description="The price currency (e.g., 'EUR').")
    price_unit: str = Field(..., description="The unit for the price (e.g., 'group').")
    duration_min_hours: Optional[float] = Field(None, description="Minimum duration in hours (e.g., 3.5).")
    booking_callout: Optional[str] = Field(None, description="Special booking information (e.g., 'Booked 6 times yesterday').")
    activity_url: Optional[str] = Field(None, description="The direct URL to the activity listing.")
    image_url: Optional[str]: Field(None, description="The URL to the activity image")
