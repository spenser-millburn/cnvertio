#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pprint
import requests
import json

BASE_URL = "http://localhost:6500"

def execute_pipeline(pipeline_steps):
    response = requests.post(f"{BASE_URL}/execute_pipeline", json=pipeline_steps)
    result = response.json()
    pprint(result)

def load_json_as_string(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        json_string = file.read()
    return json_string

if __name__ == "__main__":
    json_string = load_json_as_string('pipeline_steps.json')
    pipeline_steps = json.loads(json_string)
    execute_pipeline(pipeline_steps)
