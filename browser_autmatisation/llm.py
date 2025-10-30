from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os
from messages import message
load_dotenv()
llm = ChatOllama(model=os.environ["MODEL_BROWSER"])

response = llm.invoke([message])
print(response.content)