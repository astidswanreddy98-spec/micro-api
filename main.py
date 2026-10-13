from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Micro API is running successfully!"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"greeting": f"Hello, {name}!"}