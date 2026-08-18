from fastapi import FastAPI

app = FastAPI(title="API Análisis de Sonidos de Motores")

@app.get("/")
def read_root():
    return {"mensaje": "¡Backend estructurado profesionalmente!"}