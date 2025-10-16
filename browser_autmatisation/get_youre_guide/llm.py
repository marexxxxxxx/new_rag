from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from state import state, isevent, ActivityListing, ActivityListing_advanced, Advanced
from messages import is_event_prompt, json_format_prompt, deep_analyst_prompt, deep_struter_prompt
from scraper import get_youre_data
is_event_model = ChatOllama(model="qwen3:4b")
json_format_model   = ChatOllama(model="hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:Q8_0", temperature=0)

def splitting(eingang):
    text = ""
    sammlung = []
    is_enter = 0
    for i in eingang:
        if i == "\n" and is_enter == 1:
            sammlung.append(text)
            is_enter = 0
            text =""
        if i == "\n":
            is_enter = 1
        if i != "\n":
            is_enter = 0
        text +=i
    for i in sammlung:
        print(i)
        print("\n \n \n")

with open("test.txt", "r") as t: 
    splitting(t.read())


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

def link_formater(erg: ActivityListing):
    links = erg.url
    if links[0][:-3] == ".jpeg":
        return erg
    elif links[1][:-3] == ".jpeg":
        better_links = [links[1], links[0]]
        erg.url = better_links
    else:
        Exception("Probelme bei dem Jpeg format.")
        return erg

def json_format(state:state):
    obj = state["current_obj"]
    struc = json_format_model.with_structured_output(ActivityListing)
    response = struc.invoke(json_format_prompt.invoke({"text": [obj]}))
    if state["ergebnisse"] == None:
        return {"ergebnisse": [response], "current_obj":""}
    else:
        ergb = state["ergebnisse"]

        ergb.insert(0,response)
        return {"ergebnisse": ergb, "current_obj":""}

def deeper_searcher(state:state):

    None
    
    

def create_obj(state:state): #Das soll die Objecte also die den Markdown text zu den einzelnen activen erstellen
    new_version = state["ergebnisse"]
    obj = state["ergebnisse"][0]
    new_version.pop(0)
    link = obj.url[0]
    if link[:-3] == ".jpeg":
        raise Exception("jpeg format nicht vorhanden")
    markdown = get_youre_data(link)
    result = splitting(markdown)
    is_event_mode = is_event_model.with_structured_output(isevent)
    erg = []
    for i in result:
        test = is_event_model.invoke(deep_analyst_prompt.invoke({"text": i}))
        if test == True:
            erg.append(i)
    structer = json_format_model.with_structured_output(Advanced)
    ergb = structer.invoke(deep_struter_prompt.invoke({"text": str(erg)}))
    ende = ActivityListing_advanced{**obj.model_dump(),**ergb.model_dump()}
    return {"ergebnisse": new_version, "structured_obj": ende}