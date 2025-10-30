from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv()


receiver_model = ChatOllama(model=os.environ["RECEIVER"]) #zuständig für die Plan genereierung
sender_model = ChatOllama(model=os.environ["SENDER"])# zuständig für die umsetztung


