from fastapi import FastAPI

app = FastAPI(title="SmartCampus")


@app.get("/health")
def health():
    return {"status": "ok"}
