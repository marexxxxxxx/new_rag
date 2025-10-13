from pydantic import BaseModel
from typing import Union, Annotated, Optional, TypedDict
from langgraph.graph import StateGraph
from beispiel import test

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

    title: Annotated[str, "The name of the activity."]
    rating_average: Annotated[float, "The average star rating (e.g., 4.3)."]
    rating_count: Annotated[int,"The total number of ratings (e.g., 1157."]
    price_value: Annotated[float, "The base price (e.g., 140)."]
    price_currency: Annotated[str, "The price currency (e.g., 'EUR')."]
    price_unit: Annotated[str,"The unit for the price (e.g., 'group')."]
    duration_min_hours: Annotated[Optional[float],"Minimum duration in hours (e.g., 3.5)."] = None
    booking_callout: Annotated[Optional[str],"Special booking information (e.g., 'Booked 6 times yesterday')."] = None
    url: Annotated[list[str], "The Urls to the activity and image"]