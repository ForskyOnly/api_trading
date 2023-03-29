from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def teste():
    liste = [i for i in range(100) if i%5==0]
    return{"liste des multiple de 5": liste}