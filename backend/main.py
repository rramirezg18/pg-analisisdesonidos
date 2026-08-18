from fastapi import FastAPI

app = FastAPI(title="API Análisis de Sonidos de Motores")

@app.get("/")
def read_root():
    return {"mensaje": "¡Backend de Análisis de Sonidos funcionando!"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "db": "sqlite_ready"}