# backend/routes/api_global_context.py

from fastapi import APIRouter
import os
import json

router = APIRouter()

@router.get("/global_context")
def get_global_context():
    path = "backend/cache/global_context.json"
    if not os.path.exists(path):
        return {"error": "No context file found."}
    with open(path, "r") as f:
        return json.load(f)

