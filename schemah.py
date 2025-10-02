from pydantic import BaseModel
from typing import Annotated, Union

class info_schemah(BaseModel):
    name: Annotated[str, "Name of the Aktivity"]
    activity: Annotated[Union[str,None],"Type of activity: Sight, Activity, or None (if not visible)."]
    price: Annotated[float,"The price"]
    location: Annotated[str, "The Location of the Event"]
    description: Annotated[str,"Description of the event"]
    link: Annotated[Union[str,None],"Add a link when provided, otherwise set it to None"]
    duration: Annotated[Union[list,None],"The Duration. If nothing is avaible: None"]
