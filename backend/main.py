#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pp
import requests

BASE_URL = "http://localhost:6500"

def execute_pipeline(pipeline_steps):
    previous_result = None
    for step in pipeline_steps:
        step['previous_result'] = previous_result
        response = requests.post(f"{BASE_URL}/execute_pipeline", json={"step": step})
        if response.status_code == 200:
            previous_result = response.json()["result"]
            pp("Step execution result:")
            pp(previous_result)
        else:
            pp(f"Error: {response.status_code} - {response.json()['detail']}")
            break

if __name__ == "__main__":
    pipeline_steps = [
        {"plugin": "google_drive", "action": "upload_file", "data": None},
        {"plugin": "gpt_transform", "action": "transform_text", "data": {"source": "apples", "transformation": "list 10 things about this in 20 words"}},
        {"plugin": "google_drive", "action": "list_files", "data": None}
    ]
    execute_pipeline(pipeline_steps)
