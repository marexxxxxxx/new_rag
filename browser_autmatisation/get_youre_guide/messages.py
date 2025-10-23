from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts.chat import ChatPromptTemplate

is_event_prompt = ChatPromptTemplate.from_messages([ #muss noch angepasst werden, sodass es wirklich nur richtige elemente übernimmt.
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


deep_analyst_prompt = ChatPromptTemplate.from_messages([
    ("system","""

You are a high-precision validation engine. Your task is to analyze the input text and decide if it contains **at least one piece of genuine, relevant information** that meaningfully fits the defined schema definitions.

Your output must be **ONLY** `true` or `false`.

**SCHEMA DEFINITIONS (What to look for):**
* `highlights`: Genuine selling points (e.g., "See dolphins", "Volcano view").
* `full_description`: A detailed narrative description of the activity.
* `includes`: Specific services included in the price (e.g., "Lunch", "Snorkeling gear").
* `not_suitable_for`: Specific groups of people or health restrictions (e.g., "Pregnant women", "Children under 5").
* `pickup_details`: Specific pickup locations or meeting points.
* `important_information`: Critical "What to bring" info (e.g., "Bring passport").
* `coordinates`: Valid numerical latitudes/longitudes.

**STRICT REJECTION RULES (Junk Filter):**
You MUST output `false` if the text **EXCLUSIVELY** contains one or more of the following:
1.  **Generic Footer/Meta-Text:** "Privacy Policy", "Legal Notice", "Sitemap", "Contact", App Store Links, "General Terms and Conditions".
2.  **Generic Booking or Marketing Phrases:** "Free cancellation", "Reserve now & pay later", "Likely to sell out".
3.  **Irrelevant or Miscategorized Content:** SEO links, titles of OTHER tours, generic filler text (e.g., "Sunset at the sea" on a cheese tour), review quotes ("Laura was on time").
4.  **Invalid Data:** Coordinates like `inf`, `270.0`, or non-numeric values.
5.  **Page Structure Elements:** "Filters", "Search results", "How GetYourGuide ranks activities".

**Your Task:**
Read the text. Does it contain **at least one** piece of information that matches the **SCHEMA DEFINITIONS** and is *NOT* just content from the **REJECTION RULES**?

Say `true` if yes.
Say `false` if no (i.e., the text is exclusively junk/meta-text/irrelevant).

     
"""
    ),
    ("human", "{text}")
])

deep_struter_prompt = ChatPromptTemplate.from_messages([
    (
    "system",
    """

You are a high-precision information extraction model.
Extract the relevant data from the text below and return it strictly as JSON that follows the exact schema and semantic rules.

**SCHEMA AND SEMANTIC RULES:**

{{
  "highlights": array[string],
  // DEFINITION: Extract only genuine selling points or unique features that describe this specific activity (e.g., "Volcano view", "Swim with dolphins").

  "full_description": array[string],
  // DEFINITION: Extract only detailed, narrative descriptions of what happens during the activity.

  "includes": array[string],
  // DEFINITION: Extract only specific services or items included in the price (e.g., "Lunch", "Snorkeling gear", "Entrance fees").

  "not_suitable_for": array[string],
  // DEFINITION: Extract only specific groups of people or health restrictions for whom the activity is unsuitable (e.g., "Pregnant women", "Children under 7", "People with back problems").

  "pickup_details": array[string],
  // DEFINITION: Extract only specific information about pickup locations, meeting points, or pickup logic.

  "important_information": array[string],
  // DEFINITION: Extract only critical information the customer must know before booking (e.g., "What to bring: Passport", "Don't forget sunscreen", "Valid driver's license required").

  "coordinates": array[float]
  // DEFINITION: Extract only valid numerical latitudes (in the range -90 to 90) and longitudes (in the range -180 to 180).
}}

**OUTPUT RULES:**
1.  **JSON Only:** Return ONLY valid JSON.
2.  **No Explanations:** Do not include explanations, markdown, or extra fields.
3.  **Schema Adherence:** The keys and order must exactly match the schema above.
4.  **Strict Definition:** Extract ONLY information that exactly matches the field DEFINITION above.
    """
    ),
    ("human", "{text}")
])


deep_extracter = ChatPromptTemplate.from_messages([
    ("system", """
You should extract the {Titel}
The Schemah provided:
     {Schemah}
"""),
("human","{text}")
])

deep_highlight_extractor = ChatPromptTemplate.from_messages([
    ("system","""
You are a Precision Analyst. Your task is to extract the most important highlights from the following text. Highlights are the central facts, most important results, or core statements. Ignore introductions, filler words, and trivialities. Concentrate only on the core information.
     """),
     ("human", "{Text}")
])

deep_meeting_point_extractor = ChatPromptTemplate.from_messages([
    ("system","""
You are a Precision Coordinator. Your task is the extraction of exclusively exact, physical meeting points from the text.

Extract only:

    Complete addresses (e.g., Sample Street 10, 12345 City)

    Specific locations (e.g., Platform 7, Main Entrance City Hall, Café Central)
"""),("human", "{Text}")
])

deep_full_descriptin_extractor = ChatPromptTemplate.from_messages([
    ("system", """ You are a Data Transcriptor. Your task is to extract the complete, contiguous description from the following text.

Important Instruction: You must not omit, summarize, or change anything. Extract the entire block of text that constitutes the description. Only ignore irrelevant metadata or titles, if present. """), 
("human", "{Text}") 
])


deep_includes_extractor = ChatPromptTemplate.from_messages([
    ("system", """
You are a **Tour Preparation Specialist**. Your sole task is to analyze the provided text and strictly categorize all essential information into the three required lists: **What to Bring**, **Not Allowed**, and **Need to Know**.

**INSTRUCTIONS:**
1.  **what_to_bring:** Extract items that must be carried or worn.
2.  **not_good:** Extract all prohibitions, restrictions, or highly unsuited items/actions.
3.  **know_bevor_go:** Extract all remaining crucial details regarding logistics, timing, physical requirements, or organizational specifics.

Focus on precision. Do not summarize or invent information.
"""),
    ("human", "{Text}")
])