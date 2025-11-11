from pydantic import BaseModel
from typing import Union, Annotated, Optional, TypedDict
from langgraph.graph import StateGraph

class informations(BaseModel):
    highlights: Annotated[Union[str, None], "Highlights of the Trip. No Reviews"]
    full_description: Annotated[Union[str, None], "Full description of the Event"]
    includes: Annotated[Union[list[str], None],"What is included in the trip"]
    meeting_point: Annotated[Union[list[float,float], str, None],"THe Coordinates, the address, or None if nothing provided"]
    non_suitable: Annotated[Union[list[str],None],"Non suitable informations"]

class ActivityListing(BaseModel):
    """
    A concise Pydantic model for an activity listing.
    """

    name: Annotated[str, "The name of the activity."]
    rating_average: Annotated[float, "The average star rating (e.g., 4.3)."]
    rating_count: Annotated[int,"The total number of ratings (e.g., 1157."]
    price_value: Annotated[float, "The base price (e.g., 140)."]
    price_currency: Annotated[str, "The price currency (e.g., 'EUR')."]
    price_unit: Annotated[str,"The unit for the price (e.g., 'group')."]
    duration_min_hours: Annotated[Optional[float],"Minimum duration in hours (e.g., 3.5)."] = None
    url: Annotated[list[str], "The Urls to the activity and image"]


class ActivityListing_advanced(BaseModel):
    ActivityListing: ActivityListing
    informations: informations

    
class state(TypedDict):
    mem_result = Annotated[...,"Memgraph node"]
    #PremierTeil
    current_obj: Annotated[str,"Object with the current event."]
    ergebnisse: Annotated[list, "Object with all of the events"] # D
    list_with_text: Annotated[list, "List with the text"]
    link: Annotated[list[str], "The list with the links to check"]
    #SecoundarTeil
    advanced_current_obj: Annotated[ActivityListing, "The current Object to get a detailed extract from"]
    result_list: Annotated[list, "List with the final objects"]

    #Crawl4ai_infors
    obj: Annotated[ActivityListing_advanced,"The Object to add if true"]
    informations_to_check: Annotated[informations,"Should be a good ans suiting Model otherwise should it be renewed"]
    link_and_name: Annotated[list[str], "The Informations if its not good to make a new searchquery"]

class isevent(BaseModel):
    is_event: Annotated[bool,"Is the given text a event"]

class has_more_info(BaseModel):
    has_more: Annotated[bool,"Has more infos."]
    
class bewertung(BaseModel):
    points: Annotated[float, "The number of points the object become"]
    