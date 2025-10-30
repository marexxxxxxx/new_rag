from llm import receiver_model, sender_model
from langchain_core.agents import AgentAction
from dotenv import load_dotenv
import os
from state import state_selenium

load_dotenv()

def receiver(state_selenium):
    ergebi = receiver_model.invoke({"Themea":state_selenium["input"], "Webseite": state_selenium["rueckgabe_sender"]})
    if AgentAction in ergebi:
        print("AgentAction befindet sich in ergebi")
    else:
        print("Nein ist nicht vorhanden.")