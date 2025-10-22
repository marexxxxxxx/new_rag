from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from state import state, isevent, ActivityListing, ActivityListing_advanced, Advanced, has_more_info, highlights, meeting_point, full_description, includes
from messages import is_event_prompt, json_format_prompt, deep_analyst_prompt, deep_struter_prompt, deep_extracter
from scraper import get_youre_data
from scraper import splitting_events, splitt_and_cut
is_event_model = ChatOllama(model="hf.co/bartowski/ai21labs_AI21-Jamba-Reasoning-3B-GGUF:Q8_0", num_predict=1000)
json_format_model   = ChatOllama(model="hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:Q8_0", temperature=0, num_predict=1500)






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
    links = erg.url
    if ".jpeg" not in links[0]:
        return erg
    elif ".jpeg" in links[0]:
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

from time import sleep

def get_deep_link(state:state): #Das soll die Objecte also die den Markdown text zu den einzelnen activen erstellen
    """Zuständig für den Web Part, also für Link getting, richtig formatieren, dann webseite auf rufen"""
    sleep(1) 
    new_version = state["ergebnisse"]
    obj: ActivityListing = state["ergebnisse"][0]
    
    new_version.pop(0)
    if obj.title.lower() in ["rating rules", "company", "jobs", "work with us"]:
        return {"ergebnisse": new_version} 
    obj = link_formater(obj)
    link = obj.url[0]
    state["link"] = link

    if ".jpeg" in link:
        raise Exception("Falsches Format")
    
    return {"link": link, "advanced_current_obj": obj, "ergebnisse": new_version}


    is_event_mode = is_event_model.with_structured_output(has_more_info)
    erg = []
    for i in markdown["list_with_text"]: 
        test: has_more_info = is_event_mode.invoke(deep_analyst_prompt.invoke({"text": i}))
        if test.has_more == True:
            erg.append(i)
    structer = is_event_model.with_structured_output(Advanced)
    for _ in range(2):
        try: 
            ergb = structer.invoke(deep_struter_prompt.invoke({"text": str(erg)}))
            break
        except:
            sleep(2)
            return {"ergebnisse": new_version}
    
    try:
        ende = ActivityListing_advanced(**obj.model_dump(),**ergb.model_dump())
    except:
        Exception("Unvollständig")
        print("Unvollständig")
        # 'a' (Append) öffnet die Datei und setzt den Cursor ans Ende.
        with open("verloren_gegange.txt", "a") as t:
            print("da ist was hopssssss")
            t.write(f"\n \n \n \n \n {obj}")
        return {"ergebnisse": new_version}
    davor_und_jetzt = state["structured_obj"]
    davor_und_jetzt.append(ende)
    return {"ergebnisse": new_version, "structured_obj": davor_und_jetzt}




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

def extracter_for_deep_analyst(struc, titel, text):
    special_model = json_format_model.with_structured_output(struc)
    erg = special_model.invoke(deep_extracter.invoke({"Titel": titel, "Schemah":struc, "text": text}))
    antwort = obj_creater[titel](inhalt=erg)
    return antwort

action_map = {

    "## highlights": lambda t, text: extracter_for_deep_analyst(struc=highlights.model_json_schema(), titel=t, text=text),
    "## meeting point": lambda t, text: extracter_for_deep_analyst(struc=meeting_point.model_json_schema(), titel=t, text=text),
    "## full description": lambda t, text: extracter_for_deep_analyst(struc=full_description.model_json_schema(), titel=t, text=text),
    "## includes": lambda t, text: extracter_for_deep_analyst(struc=includes.model_json_schema(), titel=t, text=text)
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
        ergebnisse['meeting_point'] = meeting_point(meeting_point={"nothing_here"})
    if 'highlights' not in ergebnisse:
        ergebnisse['highlights'] = highlights(highlights=["War nicht in den Daten enthalten"])
    if 'full_description' not in ergebnisse:
        ergebnisse['full_description'] = full_description(full_description="War nicht in den Daten")
    if 'includes' not in ergebnisse:
        ergebnisse["includes"] = includes(what_to_bring=["War nicht in den Daten Enthalten"], not_good=["War nicht in den Daten Enthalten"], know_bevor_go=["War nicht in den Daten Enthalten"])
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
    
        
