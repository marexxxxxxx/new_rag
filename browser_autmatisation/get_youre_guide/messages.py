from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts.chat import ChatMessagePromptTemplate

is_event_prompt = ChatMessagePromptTemplate(
    "system","""
Du bist ein Text analyst. Analysiere, ob der Text eine Event Info hat, und mindestens solche
Merkmale besitzt wie:
1.Titel
2.Currency
3.rating_count

wenn es diese sachen erfüllt, so returnst du true, anderfalse false.
""",
MessagesPlaceholder(variable_name="text")
)


json_format_prompt=ChatMessagePromptTemplate(
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
    """,
    MessagesPlaceholder(variable_name="text")

)
