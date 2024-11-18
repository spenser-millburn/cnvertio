from dataclasses import dataclass
import json
from typing import List
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import openai
import os
from pydantic import BaseModel
from datetime import datetime
from src.pipeline_engine import Stage
from src.plugin_interface import Artifact, PluginInterface, validate_action

class GoogleDrivePlugin(PluginInterface):
    input_data_type = "text"
    output_data_type = "text"
    name = "GoogleDrivePlugin"

    def __init__(self, service_account_file):
        self.service_account_file = service_account_file
        self.creds = None
        self.supported_actions = ["upload_file", "download_file", "list_files"]

    def authenticate(self):
        if not self.creds:
            self.creds = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )

    def upload_file(self, file_name):
        service = build('drive', 'v3', credentials=self.creds)
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_name, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def download_file(self, file_id, destination):
        service = build('drive', 'v3', credentials=self.creds)
        request = service.files().get_media(fileId=file_id)
        with open(destination, 'wb') as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        return f"File downloaded to: {destination}"

    @validate_action
    def execute(self, action, data=None, previous_result=None):
        service = build('drive', 'v3', credentials=self.creds)
        artifact = Artifact(
            plugin=GoogleDrivePlugin,
            data_type=self.output_data_type,
            status="success",
            timestamp=datetime.now(),
            metadata={"action": action}
        )

        if action == 'upload_file':
            file_name = data["file_path"]
            file_id = self.upload_file(file_name)
            artifact.metadata.update({"file_id": file_id, "file_name": file_name})
            return artifact

        elif action == 'download_file':
            result = self.download_file(file_id=data["file_id"], destination=data["file_path"])
            artifact.metadata.update({"result": result})
            return artifact

        elif action == 'list_files':
            results = service.files().list(pageSize=10, fields="files(id, name)").execute()
            items = results.get('files', [])
            artifact.metadata.update({"files": items})
            return artifact

class GPTTransformPlugin(PluginInterface):
    input_data_type = "text"
    output_data_type = "text"
    name = "GPTTransformPlugin" #TODO use __class__.__name__

    def __init__(self):
        self.authenticated = False
        self.client = None
        self.supported_actions = ["transform_text", "transform_file"]

    def authenticate(self):
        if not self.authenticated:
            self.client = openai.OpenAI()  # TODO add handling here
            self.authenticated = True

    def transform_text(self, source_text, transformation):
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": f"{source_text}, {transformation}"},
            ]
        )
        transformed_text = response.choices[0].message.content
        return transformed_text

    def transform_file(self, source_file_path, transformation):
        with open(source_file_path, "r+") as file:
            source_text = file.read()
            transformed_text = self.transform_text(source_text, transformation)
            file.write(transformed_text)
        return transformed_text + " successfully modified file"

    @validate_action
    def execute(self, action, data, previous_result=None):
        artifact = Artifact(
            plugin=GPTTransformPlugin,
            data_type=self.output_data_type,
            status="success",
            timestamp=datetime.now(),
            metadata={"action": action }
        )

        if action == 'transform_text':
            content = self.transform_text(data["source"], data["transformation"])
            artifact.metadata.update({"content": content})
            return artifact

        if action == 'transform_file':
            content = self.transform_text(data["source_path"], data["transformation"])
            artifact.metadata.update({"content": content})
            return artifact
