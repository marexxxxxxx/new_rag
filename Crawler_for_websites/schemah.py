from pydantic import BaseModel
from typing import Annotated, Union

class info_schemah(BaseModel):
    name: Annotated[str, "Name of the Aktivity"]
    activity: Annotated[Union[str,None],"Type of activity: Sight, Activity, or None (if not visible)."]
    price: Annotated[float,"The price"]
    location: Annotated[str, "The Location of the Event"]
    description: Annotated[str,"Description of the event"]
    link: Annotated[Union[str,None],"Extract the link that leads directly to the activity."]
    duration: Annotated[Union[list,None],"The Duration. If nothing is avaible: None"]
