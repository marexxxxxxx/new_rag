from browser_use import Agent, ChatBrowseUse


task = """
1. Go got https://www.getyourguide.de/
2. Use find_text to finde the searchbar
3. Click the button
3. Use send_keys to tipp Fuerteventura
4. Use find_text to find the button with Anytime
5. Click the button
6. Use find_text to find the 28 October.
7. CLick the 28. October
8. Use find_text to find the 30 October.
9. Click the 29. October
10. Use find_text to find Search
11. Click Search
12. Extract the link and return it.
"""

from langchain_ollama import ChatOllama

llm = ChatOllama(model="Ausfüllen")

Agent(
    task=task,
    llm=llm
)
