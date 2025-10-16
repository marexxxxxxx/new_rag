from llm import json_format, event_checker
from langgraph.graph import END, StateGraph
from state import state
from langchain_core.runnables.config import RunnableConfig
from scraper import get_youre_data
from checks import schreibe_alles, check, get_data_check
config = RunnableConfig(recursion_limit=100)

graph = StateGraph(state)
IS_EVENT= "is_event"
JSON_FORMAT = "json_format"
SCHREIBE = "schreibe"
GET_YOURE_DATA = "get_youre_data"

graph.add_node(GET_YOURE_DATA, get_youre_data)
graph.add_node(IS_EVENT, event_checker)
graph.add_node(JSON_FORMAT, json_format)
graph.add_node(SCHREIBE,schreibe_alles)

graph.set_entry_point(GET_YOURE_DATA)
graph.add_conditional_edges(GET_YOURE_DATA,get_data_check, {0: IS_EVENT, 1: GET_YOURE_DATA})
graph.add_conditional_edges(IS_EVENT, check, {0:JSON_FORMAT,1:IS_EVENT,2: SCHREIBE})

graph.add_edge(JSON_FORMAT, IS_EVENT)

app = graph.compile()

from beispiel import test

b = app.invoke({
    "link": "",
    "counter": 0, 
    "current_obj": "", 
    "ergebnisse": [], 
    "list_with_text": test
},{"recursion_limit":10000000})

