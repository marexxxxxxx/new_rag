from langchain_core.messages import HumanMessage
import base64


image_path = "test.png"
with open(image_path, "rb") as b:
    image_base74= base64.b64encode(b.read()).decode("utf-8")
message = HumanMessage(content=[
    {"type": "text", "text": "Extrahiere mir alle erlebnisse von dieser Webseite als json."},
    {"type": "image",
    "source_type":"base64",
     "data": image_base74,
     "mime_type": "image/jpeg"}

])