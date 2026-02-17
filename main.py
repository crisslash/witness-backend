from fastapi import FastAPI
from typing import List

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Witness backend running"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/projects")
def list_projects():
    return {"projects": ["promet-donihue"]}

@app.get("/projects/{project_id}/dates")
def get_available_dates(project_id: str):
    return {
        "project": project_id,
        "available_dates": [
            "2026-02-14",
            "2026-02-15",
            "2026-02-16"
        ]
    }

@app.get("/projects/{project_id}/compare")
def compare(project_id: str, date1: str, date2: str):
    return {
        "project": project_id,
        "date1": date1,
        "date2": date2,
        "status": "comparison endpoint ready"
    }

