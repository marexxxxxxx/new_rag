from llm import json_format, event_checker, formater, get_deep_link, extracter_for_deep_analyst, deep_analyst
from langgraph.graph import END, StateGraph
from state import state
from langchain_core.runnables.config import RunnableConfig
from scraper import get_youre_data
from checks import schreibe_alles, check, get_data_check, go_deeper_check
config = RunnableConfig(recursion_limit=100)
from dotenv import load_dotenv


graph = StateGraph(state)
IS_EVENT= "is_event"
JSON_FORMAT = "json_format"
SCHREIBE = "schreibe"
GET_YOURE_DATA = "get_youre_data"
FIST_FORMATER = "first_formater_for_getyoureguide"

GET_DEEP_LINK = "get_deep_link"
EXCTRACTOR_FOR_DEEP_ANALYST = "extracter_for_deep_analyst"
DEEP_ANALYST = "deep_analyst"

#PremierTeil
graph.add_node(GET_YOURE_DATA, get_youre_data)
graph.add_node(FIST_FORMATER, formater)
graph.add_node(IS_EVENT, event_checker)
graph.add_node(JSON_FORMAT, json_format)
graph.add_node(SCHREIBE,schreibe_alles)
#SecoundarTeil
graph.add_node(GET_DEEP_LINK, get_deep_link)
graph.add_node(EXCTRACTOR_FOR_DEEP_ANALYST, extracter_for_deep_analyst)
graph.add_node(DEEP_ANALYST, deep_analyst)


graph.set_entry_point(GET_YOURE_DATA)
graph.add_edge(GET_YOURE_DATA, FIST_FORMATER)

graph.add_conditional_edges(FIST_FORMATER,get_data_check, {0: IS_EVENT, 1: GET_YOURE_DATA})
graph.add_conditional_edges(IS_EVENT, check, {0:JSON_FORMAT,1:IS_EVENT,2: GO_DEEPER}) #go_deeper wird nicht mehr exestieren

#muss neu überarbeitet werden.
graph.add_conditional_edges(GO_DEEPER, go_deeper_check, {0:GO_DEEPER, 1: SCHREIBE})
graph.add_edge(JSON_FORMAT, IS_EVENT)

app = graph.compile()
from beispiel import test

b = app.invoke({
    "link": "https://www.getyourguide.com/fuerteventura-l419/",
    "counter": 0, 
    "current_obj": "", 
    "ergebnisse": [], 
    "list_with_text": "",
    "test": "",
    "structured_obj": []
},{"recursion_limit":10000000})

