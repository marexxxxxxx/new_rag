from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from state import state, isevent, ActivityListing
from messages import is_event_prompt

is_event_model = ChatOllama(model="qwen3:4b")
json_format_model   = ChatOllama(model="hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:Q8_0", temperature=0)


def event_checker(state: state):
    text_to_check=state["list_with_text"]
    struc = is_event_model.with_structured_output(isevent)
    response = struc.invoke(is_event_prompt({"text": text_to_check[0]}))
    obj = text_to_check.pop(0)
    if response == False:
        return {"list_with_text":obj}
    elif response == True:
        return {"list_with_text":obj, "current_obj": text_to_check[0]}

def json_format(state:state):
    obj = state["current_obj"]
    struc = json_format_model.with_structured_output(ActivityListing)
    response = json_format_model.invoke({"text": obj})
    ergb = state["ergebnisse"].append(response)
    return {"ergebnisse": ergb, "current_obj":""}


    