from pydantic import BaseModel
from typing import Union, Annotated, Optional, TypedDict
from langgraph.graph import StateGraph
from beispiel import test

class state(TypedDict):
    #PremierTeil
    current_obj: Annotated[str,"Object with the current event."]
    ergebnisse: Annotated[list, "Object with all of the events"] # D
    list_with_text: Annotated[list, "List with the text"]
    link: Annotated[list[str], "The list with the links to check"]
    #SecoundarTeil
    advanced_current_obj = Annotated[list[str], "The current Object to get a detailed extract from"]
    result_list: Annotated[list, "List with the final objects"]

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
    url: Annotated[list[str], "The Urls to the activity and image"]






class highlights(BaseModel):
    highlights: Annotated[list[str], "A list of the Highlights"]

class meeting_point(BaseModel):
    meeting_point: Annotated[list, "The meeting point where the people have to come"]

class full_description(BaseModel):
    full_description: Annotated[str, "The whole description"]

class includes(BaseModel):
    what_to_bring: Annotated[list, "Things you should bring with, or would be great"]
    not_good: Annotated[list, "Things that are not allowd or not suitiblie things"]
    know_bevor_go: Annotated[list, "Things that do not fit in the other categories"]
    

class Advanced(BaseModel):
    highlights: highlights
    full_description: full_description
    includes: includes
    meeting_point: meeting_point

class ActivityListing_advanced(ActivityListing):
    Advanced