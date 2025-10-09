from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
llm = ChatOllama(model="hf.co/LiquidAI/LFM2-1.2B-Extract-GGUF:Q8_0")

with open("test.txt", "r") as t:
    text = t.read()

message = [
    SystemMessage(content="""You are an experienced data analyst tasked with extracting structured information from a list of events and occurrences.

**Objective:** Convert the following events and occurrences into a **JSON array**.

**Instructions:**
1.  Each event/occurrence must be converted into a separate JSON object.
2.  Preserve the original field names and data structure as implied by the source material (the events and occurrences) (e.g., `date`, `description`, `location`).
3.  The entire output must **exclusively** contain the generated JSON array, with **no** additional explanations, introductory, or concluding sentences."""),
    HumanMessage(content=text)
]
response = llm.invoke(message)
with open("tester.txt", "w") as t:
    t.write(str(response))