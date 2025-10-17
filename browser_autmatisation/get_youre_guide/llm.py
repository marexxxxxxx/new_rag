from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from state import state, isevent, ActivityListing, ActivityListing_advanced, Advanced
from messages import is_event_prompt, json_format_prompt, deep_analyst_prompt, deep_struter_prompt
from scraper import get_youre_data
from scraper import splitting
is_event_model = ChatOllama(model="hf.co/bartowski/ai21labs_AI21-Jamba-Reasoning-3B-GGUF:Q8_0", options={'num_predict': 0})
json_format_model   = ChatOllama(model="hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:Q8_0", temperature=0, options={'num_predict': 6000})




def event_checker(state: state): #Findet herraus, was events sind, und was nicht.
    text_to_check=state["list_with_text"]
    struc = is_event_model.with_structured_output(isevent)
    try:
        response = struc.invoke(is_event_prompt.invoke({"text": text_to_check[0]}))
    except:
        response = struc.invoke(is_event_prompt.invoke({"text": text_to_check[0]}))
    text_to_check.pop(0)
    if response.is_event == False:
        return {"list_with_text":text_to_check}
    elif response.is_event == True:
        if text_to_check == []:
            return {"list_with_text":text_to_check}        
        return {"list_with_text":text_to_check, "current_obj": text_to_check[0]}

def link_formater(erg: ActivityListing): #verändert die postion des links sp, das der .jpeg link postion 0 ist
    links = erg.url
    if links[0][-6:-1] == ".jpeg":
        return erg
    elif links[0][-6:-1] == ".jpeg":
        better_links = [links[1], links[0]]
        erg.url = better_links
        return erg
    else:
        raise Exception("Probelme bei dem Jpeg format.")


def json_format(state:state): #erstellt das json format
    obj = state["current_obj"]
    struc = json_format_model.with_structured_output(ActivityListing)
    try:
        response = struc.invoke(json_format_prompt.invoke({"text": [obj]}))
    except:
        response = struc.invoke(json_format_prompt.invoke({"text": [obj]}))
    if state["ergebnisse"] == None:
        return {"ergebnisse": [response], "current_obj":""}
    else:
        ergb = state["ergebnisse"]

        ergb.insert(0,response)
        return {"ergebnisse": ergb, "current_obj":""}

    

def create_obj(state:state): #Das soll die Objecte also die den Markdown text zu den einzelnen activen erstellen
    new_version = state["ergebnisse"]
    obj = state["ergebnisse"][0]
    new_version.pop(0)
    link = obj.url[0]
    state["link"] = link
    if link[0][-6:-1] == ".jpeg":
        raise Exception("Falsches Format")
    markdown = get_youre_data(state)
    result = splitting(markdown)
    is_event_mode = is_event_model.with_structured_output(isevent)
    erg = []
    for i in result: #warum ist result ohne details? das ist das problem
        test = is_event_model.invoke(deep_analyst_prompt.invoke({"text": i}))
        if test == True:
            erg.append(i)
    structer = json_format_model.with_structured_output(Advanced)
    ergb = structer.invoke(deep_struter_prompt.invoke({"text": str(erg)}))
    ende = ActivityListing_advanced(**obj.model_dump(),**ergb.model_dump())
    davor_und_jetzt = state["structured_obj"]
    davor_und_jetzt.append(ende)
    return {"ergebnisse": new_version, "structured_obj": davor_und_jetzt}