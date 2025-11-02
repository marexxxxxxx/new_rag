from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello":"Hello"}

@app.put("/item/{id}")
def read(id):
    print(id)
    return {"item_id":id}