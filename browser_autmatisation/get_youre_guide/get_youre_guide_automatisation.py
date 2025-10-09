from llm import json_format, isevent
from langgraph.graph import END, StateGraph
from state import state

def check(state):
    if len(state["current_obj"]) >= 0:
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

graph.add_node(IS_EVENT, isevent)
graph.add_node(JSON_FORMAT, json_format)

graph.set_entry_point(IS_EVENT)
graph.add_conditional_edges(IS_EVENT, check, {0:JSON_FORMAT,1:IS_EVENT,2: schreibe_alles})

graph.add_edge(JSON_FORMAT, IS_EVENT)

app = graph.compile()

from beispiel import test
test = app.invoke({"counter":0, "current_obj":"", "ergebnisse":[], "list_with_text":test})

