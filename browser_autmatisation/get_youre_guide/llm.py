from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from state import state, isevent, ActivityListing
from messages import is_event_prompt, json_format_prompt

is_event_model = ChatOllama(model="qwen3:4b")
json_format_model   = ChatOllama(model="hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:Q8_0", temperature=0)


def event_checker(state: state):
    text_to_check=state["list_with_text"]
    struc = is_event_model.with_structured_output(isevent)
    response = struc.invoke(is_event_prompt.invoke({"text": text_to_check[0]}))
    text_to_check.pop(0)
    if response.is_event == False:
        return {"list_with_text":text_to_check}
    elif response.is_event == True:
        if text_to_check == []:
            return {"list_with_text":text_to_check}        
        return {"list_with_text":text_to_check, "current_obj": text_to_check[0]}

def json_format(state:state):
    obj = state["current_obj"]
    struc = json_format_model.with_structured_output(ActivityListing)
    response = struc.invoke(json_format_prompt.invoke({"text": [obj]}))
    if state["ergebnisse"] == None:
        return {"ergebnisse": [response], "current_obj":""}
    else:
        ergb = state["ergebnisse"]
        ergb.insert(0,response.model_dump())
        return {"ergebnisse": ergb, "current_obj":""}


