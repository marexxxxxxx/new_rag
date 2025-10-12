from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts.chat import ChatPromptTemplate

is_event_prompt = ChatPromptTemplate.from_messages([
    ("system","""
Du bist ein Textanalyst. Analysiere, ob der gegebene Text eine Event-Info enthält und mindestens die folgenden Merkmale besitzt:

    Titel (Name des Events oder der Tour)

    Currency (z.B. Euro, angegeben durch „€“)

    rating_count (Bewertung, z.B. „4.8 (940)“)

Wenn der Text alle drei Merkmale aus den Beispielen enthält, gib „true“ zurück, sonst „false“.
Beispiele:

    Text: 4.7 out of 5 stars 4.7 Provider rating From €85 per person Corralejo: Lobos Island Catamaran Tour with Drinks & Snorkel﻿


→ true (enthält Titel, Currency und Bewertung)

Text: 4.8 out of 5 stars 4.8 (940) From €75 per person Corralejo: Buggy Safari Tour﻿


→ true (enthält Titel, Currency und Bewertung)

Text: Corralejo: Lobos Island Catamaran Tour - 4 hours - Pickup available﻿


    → false (enthält keine Currency und keine Bewertung)

Falls der Text also alle drei Merkmale wie in den Beispielen besitzt, return true, andernfalls return false.
"""),
("human", "{text}")
])


json_format_prompt=ChatPromptTemplate.from_messages([(
    "system",
    """
You are an information extraction model. 
Extract the relevant data from the text below and return it strictly as JSON that follows the exact schema.

SCHEMA:
{{
  "title": string,
  "rating_average": float,
  "rating_count": int,
  "price_value": float,
  "price_currency": string,
  "price_unit": string,
  "duration_min_hours": float | null,
  "booking_callout": string | null,
  "activity_url": string | null,
  "image_url": string | null
}}

RULES:
- Return ONLY valid JSON.
- Do not include explanations, markdown, or extra fields.
- Use "null" for missing optional values.
- Use proper numeric types for floats and integers.
- The keys and order must exactly match the schema above.
    """),
    ("human","{text}")
    

])
