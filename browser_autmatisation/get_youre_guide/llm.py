from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from state import state, isevent, ActivityListing, ActivityListing_advanced, Advanced, has_more_info, highlights, meeting_point, full_description, includes
from messages import is_event_prompt, json_format_prompt, deep_analyst_prompt, deep_struter_prompt, deep_extracter, deep_full_descriptin_extractor, deep_highlight_extractor, deep_meeting_point_extractor, deep_includes_extractor
from scraper import get_youre_data
from scraper import splitting_events, splitt_and_cut
is_event_model = ChatOllama(model="hf.co/bartowski/ai21labs_AI21-Jamba-Reasoning-3B-GGUF:Q8_0", num_predict=1000)
json_format_model   = ChatOllama(model="hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:Q8_0", temperature=0, num_predict=1500)
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="marec.shopping@gmail.com")




def event_checker(state: state): #Findet herraus, was events sind, und was nicht.
    text_to_check=state["list_with_text"]
    current_obj = text_to_check[0]
    struc = is_event_model.with_structured_output(isevent)
    
    
    try:
        response = struc.invoke(is_event_prompt.invoke({"text": text_to_check[0]}))
    except:
        response = struc.invoke(is_event_prompt.invoke({"text": text_to_check[0]}))
    try:
        text_to_check.pop(0)
    except:
        print("es gab ein Problem")
    if response.is_event == False:
        return {"list_with_text":text_to_check}
    elif response.is_event == True:
        if text_to_check == []:
            return {"list_with_text":text_to_check}        
        return {"list_with_text":text_to_check, "current_obj": current_obj} #muss angepasst werden, current_obj wird fallen gelassen, hier wird listenartig

def link_formater(erg: ActivityListing): #verändert die postion des links sp, das der .jpeg link postion 0 ist
    try:
        links = erg.url
        if ".jpeg" not in links[0]:
            return erg
        elif ".jpeg" in links[0]:
            better_links = [links[1], links[0]]
            erg.url = better_links
            return erg
        else:
            raise Exception("Probelme bei dem Jpeg format.")
    except Exception as e:
        print(f"Folgender Fehler: {e}") 
        return ""
    
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

from time import sleep

def get_deep_link(state:state): #Das soll die Objecte also die den Markdown text zu den einzelnen activen erstellen
    """Zuständig für den Web Part, also für Link getting, richtig formatieren, dann webseite auf rufen"""
    sleep(1) 
    new_version = state["ergebnisse"]
    obj: ActivityListing = state["ergebnisse"][0]
    
    new_version.pop(0)
    if obj.name.lower() in ["rating rules", "company", "jobs", "work with us"]:
        return {"ergebnisse": new_version} 
    obj = link_formater(obj)
    
    link = obj.url[0]
    state["link"] = link

    if ".jpeg" in link:
        raise Exception("Falsches Format")
    
    return {"link": link, "advanced_current_obj": obj, "ergebnisse": new_version}


def formater(state:state):
    erg = state["list_with_text"]
    erg = splitting_events(erg)
    return {"list_with_text": erg}



obj_creater = {
    "## highlights": lambda inhalt: highlights(**inhalt),
    "## meeting point": lambda inhalt: meeting_point(**inhalt),
    "## full description": lambda inhalt: full_description(**inhalt),
    "## includes": lambda inhalt: inhalt
}

def extracter_for_deep_analyst(struc, titel, text, message):
    special_model = json_format_model.with_structured_output(struc)
    erg = special_model.invoke(message.invoke({"Text": text}))
    antwort = obj_creater[titel](inhalt=erg)
    return antwort

action_map = {

    "## highlights": lambda t, text : extracter_for_deep_analyst(struc=highlights.model_json_schema(), titel=t, text=text, message=deep_highlight_extractor),
    "## meeting point": lambda t, text: extracter_for_deep_analyst(struc=meeting_point.model_json_schema(), titel=t, text=text, message=deep_meeting_point_extractor),
    "## full description": lambda t, text: extracter_for_deep_analyst(struc=full_description.model_json_schema(), titel=t, text=text, message=deep_full_descriptin_extractor),
    "## includes": lambda t, text: extracter_for_deep_analyst(struc=includes.model_json_schema(), titel=t, text=text, message=deep_includes_extractor)
}

umwandler = {
    "## highlights": "highlights",
    "## meeting point": "meeting_point",
    "## full description": "full_description",
    "## includes": "includes"
}


def deep_analyst(state:state):#
    erg = splitt_and_cut(state["list_with_text"])
    keywords = ["## highlights","## full description","## includes", "## meeting point"]
    ergebnisse = {}
    
    for text in erg:
        for key in keywords:
            if key in text.lower():
                erg = action_map[key](t=key, text=text)
                ergebnisse[umwandler[key]] = erg
    
    if 'meeting_point' not in ergebnisse:
        ergebnisse['meeting_point'] = meeting_point(coordianten={0}, location="Keine ANgeaben im Text")

    if 'highlights' not in ergebnisse:
        ergebnisse['highlights'] = highlights(highlights=["War nicht in den Daten enthalten"])
    if 'full_description' not in ergebnisse:
        ergebnisse['full_description'] = full_description(full_description="War nicht in den Daten")
    if 'includes' not in ergebnisse:
        ergebnisse["includes"] = includes(what_to_bring=["War nicht in den Daten Enthalten"], not_good=["War nicht in den Daten Enthalten"], know_bevor_go=["War nicht in den Daten Enthalten"])
    


    location = geolocator.geocode(ergebnisse['meeting_point'].location)
    if location:
        ergebnisse["meeting_point"] = meeting_point(coordianten={location.latitude, location.longitude}, location=ergebnisse["meeting_point"].location) #vlt Coordinaten Fromat Falschherum

    obj = Advanced(
    highlights=ergebnisse['highlights'],
    full_description=ergebnisse['full_description'],
    includes=ergebnisse['includes'],
    meeting_point=ergebnisse['meeting_point']
)
    einf = state["advanced_current_obj"]
    ende = ActivityListing_advanced(ActivityListing=einf, Advanced=obj)
    letzte_liste = state["result_list"]
    letzte_liste.append(ende)
    return {"advanced_current_obj": None, "result_liste": letzte_liste}
    
        
