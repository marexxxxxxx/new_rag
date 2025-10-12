from pydantic import BaseModel
from typing import Annotated, Union
from langchain_core.agents import AgentAction, AgentFinish
class state_selenium(BaseModel):
    input: Annotated[str, "Anfangsfrage"]
    rueckgabe: Annotated[Union[None, AgentFinish, AgentAction], "Was ist der nächste Schritt des Agents."]