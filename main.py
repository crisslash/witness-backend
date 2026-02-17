import os
import json
from fastapi import FastAPI
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = FastAPI()

DRIVE_FOLDER_ID = "1UMZh6SQs32ynwjcg0weTzGhaZUehMXve"
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

@app.get("/projects/{project_id}/photo-of-day")
def get_photo_of_day(project_id: str, date: str):

    service = get_drive_service()

    # buscar carpeta del proyecto
    project_query = f"'{DRIVE_FOLDER_ID}' in parents and name='{project_id}' and mimeType='application/vnd.google-apps.folder'"
    project_results = service.files().list(q=project_query, fields="files(id, name)").execute()
    project_folder_id = project_results.get("files", [])[0]["id"]

    # buscar carpeta de fecha
    date_query = f"'{project_folder_id}' in parents and name='{date}' and mimeType='application/vnd.google-apps.folder'"
    date_results = service.files().list(q=date_query, fields="files(id, name)").execute()

    if not date_results.get("files"):
        return {"error": "Date folder not found"}

    date_folder_id = date_results["files"][0]["id"]

    # listar imágenes dentro de la carpeta
    image_query = f"'{date_folder_id}' in parents and mimeType contains 'image/'"
    image_results = service.files().list(q=image_query, fields="files(id, name)").execute()

    images = image_results.get("files", [])

    if not images:
        return {"error": "No images found"}

    # buscar la más cercana a 12:00
    target_minutes = 12 * 60

    best_image = None
    smallest_diff = None

    for img in images:
        name = img["name"]

        try:
            time_part = name.split("_")[1].replace(".jpg", "")
            hour = int(time_part[:2])
            minute = int(time_part[2:])
            total_minutes = hour * 60 + minute

            diff = abs(total_minutes - target_minutes)

            if smallest_diff is None or diff < smallest_diff:
                smallest_diff = diff
                best_image = img

        except Exception:
            continue

    return {
        "project": project_id,
        "date": date,
        "selected_image": best_image
    }


@app.get("/projects/{project_id}/dates")
def get_available_dates(project_id: str):

    service = get_drive_service()

    # buscar carpeta hades dentro de Witnesscloud
    query = f"'{DRIVE_FOLDER_ID}' in parents and name='{project_id}' and mimeType='application/vnd.google-apps.folder'"

    results = service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()

    folders = results.get("files", [])

    if not folders:
        return {"error": "Project folder not found"}

    project_folder_id = folders[0]["id"]

    # listar subcarpetas (fechas)
    date_query = f"'{project_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'"

    date_results = service.files().list(
        q=date_query,
        fields="files(name)"
    ).execute()

    import re

all_folders = [f["name"] for f in date_results.get("files", [])]

date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

dates = sorted([name for name in all_folders if date_pattern.match(name)])


    return {
        "project": project_id,
        "available_dates": dates
    }

@app.get("/projects/{project_id}/compare")
def compare(project_id: str, date1: str, date2: str):
    return {
        "project": project_id,
        "date1": date1,
        "date2": date2,
        "status": "comparison endpoint ready"
    }

def get_drive_service():
    credentials_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    credentials_dict = json.loads(credentials_json)

    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )

    service = build("drive", "v3", credentials=credentials)
    return service

