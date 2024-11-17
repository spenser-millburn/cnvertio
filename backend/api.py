#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from plugins import PipelineEngine, Pipeline, Stage
from plugins import GoogleDrivePlugin, GPTTransformPlugin
from typing import List

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

pipeline_engine = PipelineEngine()
pipeline_engine.register_plugin('google_drive', GoogleDrivePlugin(service_account_file='/app/conductor-441120-b2b06a8ce1c6.json'))
pipeline_engine.register_plugin('gpt_transform', GPTTransformPlugin())

@app.post("/execute_pipeline")
def execute_pipeline(pipeline: Pipeline):
    try:
        results = pipeline_engine.execute_pipeline(pipeline.steps)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e.with_traceback()))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6500)