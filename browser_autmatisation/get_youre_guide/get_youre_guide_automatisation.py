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
GET_YOURE_DATA_2 = "get_youre_data_2"
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
graph.add_node(GET_YOURE_DATA_2, get_youre_data)

graph.set_entry_point(GET_YOURE_DATA)
graph.add_edge(GET_YOURE_DATA, FIST_FORMATER)
graph.add_conditional_edges(FIST_FORMATER,get_data_check, {0: IS_EVENT, 1: GET_YOURE_DATA})
graph.add_conditional_edges(IS_EVENT, check, {0:JSON_FORMAT,1:IS_EVENT,2: GET_DEEP_LINK}) #go_deeper wird nicht mehr exestieren
graph.add_edge(JSON_FORMAT, IS_EVENT)
graph.add_edge(GET_DEEP_LINK, GET_YOURE_DATA_2)
graph.add_edge(GET_YOURE_DATA_2,DEEP_ANALYST)
graph.add_conditional_edges(DEEP_ANALYST, go_deeper_check, {0: GET_DEEP_LINK, 1: SCHREIBE})



app = graph.compile()

from IPython.display import Image, display
png = app.get_graph().draw_mermaid_png()
display(Image(png))
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

