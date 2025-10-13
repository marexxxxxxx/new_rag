from langchain_core.prompts.chat import ChatPromptTemplate



receiver_prompt = ChatPromptTemplate([
    ("system", """
Du bist ein spezialist für Websuchen. Deine Aufgabe ist es eine gewisse Sache zu beantworten. Das Thema lautet: {Themea}.
Erstelle einen Plan basierend auf den Informaiotnen die du bereits hast, wie fortgefahren werden muss, damit du das Thema beantworten kannst.
"""),
(
    "human", """
Momentan befindest du dich hier, an diesem Punkt der Websuche: 
{Webseite}    
"""
)
])

sender_prompt = ChatPromptTemplate([
    (
        "system", """
Du bist ein spezialist für Websuchen. Du sollst den folgenden Plan umsetzten:
{Plan}
Du hast dafür den Selenium MCP Server zur Verfügung. Versuche Möglichst weit zu kommen. Wenn du nicht weiter kommst beende deinen Chat.        
"""
    )
])