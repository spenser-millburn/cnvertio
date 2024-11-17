import json
from typing import List
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import openai
import os

from pydantic import BaseModel

"""
=========================================================================================================
                                        Definitions
---------------------------------------------------------------------------------------------------------

- Pipeline: A container for workflow logic
- Stage: A discrete unit of work
- Plugin: 
=========================================================================================================
"""


class Stage(BaseModel):
    plugin: str
    action: str
    data: object

class Pipeline(BaseModel):
    steps: List[Stage]

class PluginInterface:
    def authenticate(self):
        raise NotImplementedError("Authenticate method not implemented.")

    def execute(self, action, data):
        raise NotImplementedError("Execute method not implemented.")
"""
=========================================================================================================
                                            Decorators
=========================================================================================================
"""


def validate_action(func):
    def wrapper(self, action, data=None):
        if not action:
            raise ValueError("Action not provided!")
        if action not in self.supported_actions:
            raise ValueError(f"Action '{action}' not supported.")
        return func(self, action, data)
    return wrapper

"""
=========================================================================================================
                                            Plugins:
---------------------------------------------------------------------------------------------------------
- Google Drive
- GPTTransform

=========================================================================================================
"""

class GoogleDrivePlugin(PluginInterface):
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
    def execute(self, action, data=None ):
        service = build('drive', 'v3', credentials=self.creds)

        if action == 'upload_file':
            file_name = data["file_path"]
            file_id = self.upload_file(file_name)
            return f"File uploaded with ID: {file_id}, Name: {file_name}"

        elif action == 'download_file':
            return self.download_file(file_id=data["file_id"], destination=data["file_path"])

        elif action == 'list_files':
            results = service.files().list(pageSize=10, fields="files(id, name)").execute()
            items = results.get('files', [])
            return items


class GPTTransformPlugin(PluginInterface):
    def __init__(self):
        self.authenticated = False
        self.client = None
        self.supported_actions = ["transform_text", "transform_file"]

    def authenticate(self):
        if not self.authenticated:
            self.client = openai.OpenAI() #TODO add handling here
            self.authenticated = True

    def transform_text(self,source_text, transformation):


        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content":""},
                {"role": "user", "content": f"{source_text}, {transformation}"},
            ]
        )
        transformed_text = response.choices[0].message.content
        return transformed_text

    def transform_file(self,source_file_path, transformation):
        with open(source_file_path, "r+") as file: 
            source_text  = file.read()
            transformed_text = self.transform_text(source_text, transformation)
            file.write(transformed_text)
        return transformed_text + "succesfully modified file"


    @validate_action
    def execute(self, action, data):
        if action == 'transform_text':
            return self.transform_text(data["source"],data["transformation"])
        if action == 'transform_file':
            return self.transform_file(data["source_path"],data["transformation"])

"""
=========================================================================================================
                                Engine: Pipeline Implementaiton
=========================================================================================================
"""

class PipelineEngine:
    def __init__(self):
        self.plugins = {}

    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin

    def execute_pipeline(self, pipeline):
        results = []
        for step in pipeline:
            plugin_name = step.plugin
            action = step.action
            data= step.data
            plugin = self.plugins.get(plugin_name)

            if not plugin:
                raise ValueError(f"Plugin '{plugin_name}' not registered.")

            plugin.authenticate()
            result = plugin.execute(action, data)
            results.append(result)

        return results

