from llm import json_format, event_checker
from langgraph.graph import END, StateGraph
from state import state
from langchain_core.runnables.config import RunnableConfig
config = RunnableConfig(recursion_limit=100)
def check(state):
    if len(state["current_obj"]) >0:
        return 0
    elif len(state["current_obj"]) == 0 and state["list_with_text"] != []:
        return 1
    elif state["list_with_text"] == []:
        return 2
def schreibe_alles(state):
    with open("ergebnisse.txt", "w") as t:
        t.write(str(state["ergebnisse"]))
graph = StateGraph(state)
IS_EVENT= "is_event"
JSON_FORMAT = "json_format"
SCHREIBE = "schreibe"

graph.add_node(IS_EVENT, event_checker)
graph.add_node(JSON_FORMAT, json_format)
graph.add_node(SCHREIBE,schreibe_alles)

graph.set_entry_point(IS_EVENT)
graph.add_conditional_edges(IS_EVENT, check, {0:JSON_FORMAT,1:IS_EVENT,2: SCHREIBE})

graph.add_edge(JSON_FORMAT, IS_EVENT)

app = graph.compile()

from beispiel import test

b = app.invoke({
    "counter": 0, 
    "current_obj": "", 
    "ergebnisse": [[]], 
    "list_with_text": test
},{"recursion_limit":100})

