#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pp

import requests

BASE_URL = "http://localhost:6500"

def execute_pipeline(pipeline_steps):
    response = requests.post(f"{BASE_URL}/execute_pipeline", json={"steps": pipeline_steps})
    if response.status_code == 200:
        results = response.json()["results"]
        pp("Pipeline execution results:")
        for result in results:
            pp(result)
    else:
        pp(f"Error: {response.status_code} - {response.json()['detail']}")

if __name__ == "__main__":
    pipeline_steps = [
        {"plugin": "google_drive", "action": "upload_file", "data":None},
        {"plugin": "gpt_transform", "action": "transform_text", "data":{"source": "apples", "transformation": "list 10 things about this in 20 words"}},
        {"plugin": "google_drive", "action": "list_files", "data": None }
    ]
    execute_pipeline(pipeline_steps)

