import asyncio
from langchain_ollama import ChatOllama
from state import state, isevent, ActivityListing, ActivityListing_advanced, informations, bewertung
from messages import is_event_prompt, json_format_prompt,is_inforamtion_good_prompt
from scraper import splitting_events
from crawl4ai_better_version import try_using_fitt_website, try_using_wohle_website
import os
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")



is_event_model = ChatOllama(model="hf.co/bartowski/ai21labs_AI21-Jamba-Reasoning-3B-GGUF:Q8_0", num_predict=1000,base_url=ollama_url )
json_format_model = ChatOllama(model="hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:Q8_0", temperature=0, num_predict=1500, base_url=ollama_url)
look_if_good = ChatOllama(model="hf.co/unsloth/Qwen3-14B-GGUF:Q6_K", temperature=0.1, num_predict=1500,base_url=ollama_url)


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
        if ".jpeg" not in links[0] and ".jpg" not in links[0]:
            return erg
        elif ".jpeg" in links[0] or ".jpg" in links[0]:
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
    if state["ergebnisse"] == []:
        return {}
    new_version = state["ergebnisse"]
    obj: ActivityListing = state["ergebnisse"][0]
    obj = link_formater(obj)
    
    new_version.pop(0)
    try:
        if obj.name.lower() in ["rating rules", "company", "jobs", "work with us"]:
            return {"ergebnisse": new_version} 
    except Exception as e:
        print(f"DeadObj: {e}")
        return {"ergebnisse": new_version}
    
    link = obj.url[0]
    state["link"] = link
    print(link)
    if ".jpeg" in link or ".jpg" in link:
        raise Exception("Falsches Format")
    
    return {"link": link, "advanced_current_obj": obj, "ergebnisse": new_version}


def formater(state:state):
    erg = state["list_with_text"]
    erg = splitting_events(erg)
    return {"list_with_text": erg}



async def get_informations_fast(state: state):
    if state["ergebnisse"] == []:
        print("sleep")
        await asyncio.sleep(60)
        print("sleep2")
        return {}
    link = state["link"]
    try:
        test = await try_using_fitt_website(link=link, name=state["advanced_current_obj"].name)
        erg: informations = test
    except Exception as e:
        None
        print(f"HEy {e}")
# hier gibt es fhler mit dem .namen element
        return {"link_and_name":[link,state["advanced_current_obj"].name]} #hier muss eigentlich noch state[informations_to_check] = [] gesetzt werden

    obj = informations(
        highlights=erg.highlights,
        full_description=erg.full_description,
        includes=erg.includes,
        meeting_point=erg.meeting_point,
        non_suitable=erg.non_suitable
    )
    einf = state["advanced_current_obj"]
    ende = ActivityListing_advanced(ActivityListing=einf, informations=obj)
    
    return {"obj": ende,"informations_to_check":erg, "link_and_name":[link,state["advanced_current_obj"].name]} 
    

async def get_information_whole_page(state: state):
    if state["ergebnisse"] == []:
        print("sleep")
        await asyncio.sleep(60)
        print("sleep2")
        return {}
    link = state["link"]
    try:
        erg: informations  = await try_using_wohle_website(link=state["link_and_name"][0], name=state["link_and_name"][1])
    except Exception as e:
        print(e)
        return {} 

    obj = informations(
        highlights=erg.highlights,
        full_description=erg.full_description,
        includes=erg.includes,
        meeting_point=erg.meeting_point,
        non_suitable=erg.non_suitable
    )
    einf = state["advanced_current_obj"]
    ende = ActivityListing_advanced(ActivityListing=einf, informations=obj)
    letzte_liste = state["result_list"]
    letzte_liste.append(ende)
    return {"letzte_liste": letzte_liste} 


async def is_information_good(state:state):
    struc = look_if_good.with_structured_output(bewertung)
    erg = struc.invoke(is_inforamtion_good_prompt.invoke({"Text":state["informations_to_check"]}))
    if erg.points >= 6 and state["ergebnisse"] != []:
        letzte_liste = state["result_list"]
        letzte_liste.append(state["obj"])
        state["result_list"] = letzte_liste
        return 0
    elif erg.points >= 6 and state["ergebnisse"] == []:
        return 1
    elif erg.points <6 and state["ergebnisse"] != []:
        return 2
    elif erg.points <6 and state["ergebnisse"] == []:
        return 1

