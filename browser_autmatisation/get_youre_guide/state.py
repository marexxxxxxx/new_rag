from pydantic import BaseModel
from typing import Union, Annotated, Optional, TypedDict
from langgraph.graph import StateGraph
from beispiel import test

class state(TypedDict):
    counter: Annotated[int, "Number of how many iterations"] 
    current_obj: Annotated[str,"Object with the current event."]

    ergebnisse: Annotated[list, "Object with all of the events"] 
    deep_ergebnisse: Annotated[list, "A more deeper version of the ergebnisse"]
    list_with_text: Annotated[list, "List with the text"]
    list_with_check: Annotated[list, "Accpeted text"]
    link: Annotated[list[str], "The list with the links to check"]

    list_obj: Annotated[list[str],"The Deeperversion of an element, just the plain text not organized."]
    structured_obj: Annotated[list, "The Deepversion of the events, with all informations, organized"]


class isevent(BaseModel):
    is_event: Annotated[bool,"Is the given text a event"]
class has_more_info(BaseModel):
    has_more: Annotated[bool,"Has more infos."]

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
    #booking_callout: Annotated[Optional[str],"Special booking information (e.g., 'Booked 6 times yesterday')."] = None Führt immer zu massiven fehlern und warte zeiten
    url: Annotated[list[str], "The Urls to the activity and image"]


class Advanced(BaseModel):
    highlights: Annotated[Union[None,list[str]], "The Highlights textblock"]
    full_description: Annotated[Union[None,list[str]], "The Full description textblock"]
    includes: Annotated[Union[None,list[str]], "The Includes textblock"]
    not_suitable_for: Annotated[Union[None,list[str]],"The not suitable textblock"]
    pickup_details: Annotated[Union[None,list[str]], "The pickup details"]
    important_information: Annotated[Union[None,list[str]], "The important infromation textblock"]
    coordinates: Annotated[Union[None,list[float]], "The coordiantes of the activity"]

class ActivityListing_advanced(ActivityListing):
    highlights: Annotated[list[str], "The Highlights textblock"]
    full_description: Annotated[list[str], "The Full description textblock"]
    includes: Annotated[list[str], "The Includes textblock"]
    not_suitable_for: Annotated[list[str],"The not suitable textblock"]
    pickup_details: Annotated[list[str], "The pickup details"]
    important_information: Annotated[list[str], "The important infromation textblock"]
    coordinates: Annotated[list[float], "The coordiantes of the activity"]
