from fastapi import FastAPI

app = FastAPI(title="API Análisis de Sonidos de Motores", root_path="/api")

@app.get("/")
def read_root():
    return {"mensaje": "¡Backend estructurado profesionalmente!"}