from fastapi import FastApi
from browser_auto import get_link_asycn
from get_youre_guide_automatisation import create_data_base
app = FastApi()

@app.get("/location/{location}")
def get_informations(location):
    link = get_link_asycn(location)
    create_data_base(link)
    return {"answer":"fertig"}
