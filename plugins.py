import json
from typing import List
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
import openai
import os

from pydantic import BaseModel

def validate_action(func):
    def wrapper(self, action, data=None):
        if not action:
            raise ValueError("Action not provided!")
        if action not in self.supported_actions:
            raise ValueError(f"Action '{action}' not supported.")
        return func(self, action, data)
    return wrapper

class PluginInterface:
    def authenticate(self):
        raise NotImplementedError("Authenticate method not implemented.")

    def execute(self, action, data):
        raise NotImplementedError("Execute method not implemented.")

class GoogleDrivePlugin(PluginInterface):
    def __init__(self, service_account_file):
        self.service_account_file = service_account_file
        self.creds = None
        self.supported_actions = ["upload_file", "list_files"]

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

    @validate_action
    def execute(self, action, data=None):
        service = build('drive', 'v3', credentials=self.creds)

        if action == 'upload_file':
            file_id = self.upload_file('hello.txt')
            return f"File uploaded with ID: {file_id}"

        elif action == 'list_files':
            results = service.files().list(pageSize=10, fields="files(id, name)").execute()
            items = results.get('files', [])
            return items


class GPTTransformPlugin(PluginInterface):
    def __init__(self):
        self.authenticated = False
        self.client = None
        self.supported_actions = ["transform_text"]

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

    @validate_action
    def execute(self, action, data):
        if action == 'transform_text':
            return self.transform_text(data["source"],data["transformation"])

class PipelineStep(BaseModel):
    plugin: str
    action: str
    data: object

class Pipeline(BaseModel):
    steps: List[PipelineStep]

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

