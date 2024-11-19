import base64
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
    """GoogleDrivePlugin is responsible for interacting with Google Drive to perform actions such as uploading, downloading, and listing files.

    Attributes:
        input_data_type (str): The type of input data the plugin accepts.
        output_data_type (str): The type of output data the plugin produces.
        name (str): The name of the plugin.
        service_account_file (str): Path to the service account JSON file.
        creds (Credentials): Google API credentials.
        supported_actions (List[str]): List of actions supported by the plugin.
    """
    input_data_type = "text"
    output_data_type = "text"
    name = "GoogleDrivePlugin"

    def __init__(self, service_account_file):
        """Initializes the GoogleDrivePlugin with a service account file.

        Args:
            service_account_file (str): Path to the service account JSON file.
        """
        self.service_account_file = service_account_file
        self.creds = None
        self.supported_actions = ["upload_file", "download_file", "list_files"]

    def authenticate(self):
        """Authenticates the plugin using the service account file."""
        if not self.creds:
            self.creds = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )

    def upload_file(self, file_name):
        """Uploads a file to Google Drive.

        Args:
            file_name (str): The name of the file to upload.

        Returns:
            str: The ID of the uploaded file.
        """
        service = build('drive', 'v3', credentials=self.creds)
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_name, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

    def download_file(self, file_id, destination):
        """Downloads a file from Google Drive.

        Args:
            file_id (str): The ID of the file to download.
            destination (str): The destination path to save the downloaded file.

        Returns:
            str: A message indicating the file download location.
        """
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
        """Executes a specified action with the provided data.

        Args:
            action (str): The action to perform.
            data (dict, optional): The data required for the action.
            previous_result (Any, optional): The result of a previous action.

        Returns:
            Artifact: The result of the action execution.
        """
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

class GoogleSheetsPlugin(PluginInterface):
    """GoogleSheetsPlugin is responsible for interacting with Google Sheets to perform actions such as creating, reading, and updating sheets.

    Attributes:
        input_data_type (str): The type of input data the plugin accepts.
        output_data_type (str): The type of output data the plugin produces.
        name (str): The name of the plugin.
        service_account_file (str): Path to the service account JSON file.
        creds (Credentials): Google API credentials.
        supported_actions (List[str]): List of actions supported by the plugin.
    """
    input_data_type = "text"
    output_data_type = "text"
    name = "GoogleSheetsPlugin"

    def __init__(self, service_account_file):
        """Initializes the GoogleSheetsPlugin with a service account file.

        Args:
            service_account_file (str): Path to the service account JSON file.
        """
        self.service_account_file = service_account_file
        self.creds = None
        self.supported_actions = ["create_sheet", "read_sheet", "update_sheet"]

    def authenticate(self):
        if not self.creds:
            self.creds = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )

    def create_sheet(self, title):
        """Creates a new Google Sheet.

        Args:
            title (str): The title of the new sheet.

        Returns:
            str: The ID of the created spreadsheet.
        """
        service = build('sheets', 'v4', credentials=self.creds)
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
        return spreadsheet.get('spreadsheetId')

    def read_sheet(self, spreadsheet_id, range_name):
        """Reads data from a Google Sheet.

        Args:
            spreadsheet_id (str): The ID of the spreadsheet.
            range_name (str): The range of cells to read.

        Returns:
            list: The values read from the sheet.
        """
        service = build('sheets', 'v4', credentials=self.creds)
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        return values

    def update_sheet(self, spreadsheet_id, range_name, values):
        """Updates a Google Sheet with new values.

        Args:
            spreadsheet_id (str): The ID of the spreadsheet.
            range_name (str): The range of cells to update.
            values (list): The values to update in the sheet.

        Returns:
            int: The number of cells updated.
        """
        service = build('sheets', 'v4', credentials=self.creds)
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption="RAW", body=body).execute()
        return result.get('updatedCells')

    @validate_action
    def execute(self, action, data, previous_result=None):
        """Executes a specified action with the provided data.

        Args:
            action (str): The action to perform.
            data (dict): The data required for the action.
            previous_result (Any, optional): The result of a previous action.

        Returns:
            Artifact: The result of the action execution.
        """
        artifact = Artifact(
            plugin=GoogleSheetsPlugin,
            data_type=self.output_data_type,
            status="success",
            timestamp=datetime.now(),
            metadata={"action": action}
        )

        if action == 'create_sheet':
            title = data["title"]
            spreadsheet_id = self.create_sheet(title)
            artifact.metadata.update({"spreadsheet_id": spreadsheet_id, "title": title})
            return artifact

        elif action == 'read_sheet':
            spreadsheet_id = data["spreadsheet_id"]
            range_name = data["range_name"]
            values = self.read_sheet(spreadsheet_id, range_name)
            artifact.metadata.update({"values": values})
            return artifact

        elif action == 'update_sheet':
            spreadsheet_id = data["spreadsheet_id"]
            range_name = data["range_name"]
            values = data["values"]
            updated_cells = self.update_sheet(spreadsheet_id, range_name, values)
            artifact.metadata.update({"updated_cells": updated_cells})
            return artifact

class GPTTransformPlugin(PluginInterface):
    """GPTTransformPlugin is responsible for transforming text using GPT models.

    Attributes:
        input_data_type (str): The type of input data the plugin accepts.
        output_data_type (str): The type of output data the plugin produces.
        name (str): The name of the plugin.
        authenticated (bool): Indicates if the plugin is authenticated.
        client (OpenAI): The OpenAI client for interacting with GPT models.
        supported_actions (List[str]): List of actions supported by the plugin.
    """
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
        """Transforms text using a specified transformation.

        Args:
            source_text (str): The text to transform.
            transformation (str): The transformation to apply.

        Returns:
            str: The transformed text.
        """
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
        """Transforms the content of a file using a specified transformation.

        Args:
            source_file_path (str): The path to the file to transform.
            transformation (str): The transformation to apply.

        Returns:
            str: A message indicating the file was successfully modified.
        """
        with open(source_file_path, "r+") as file:
            source_text = file.read()
            transformed_text = self.transform_text(source_text, transformation)
            file.write(transformed_text)
        return transformed_text + " successfully modified file"

    @validate_action
    def execute(self, action, data, previous_result=None):
        """Executes a specified action with the provided data.

        Args:
            action (str): The action to perform.
            data (dict): The data required for the action.
            previous_result (Any, optional): The result of a previous action.

        Returns:
            Artifact: The result of the action execution.
        """
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

class ImageAnalysisPlugin(PluginInterface):
    """ImageAnalysisPlugin is responsible for analyzing images and providing descriptions.

    Attributes:
        input_data_type (str): The type of input data the plugin accepts.
        output_data_type (str): The type of output data the plugin produces.
        name (str): The name of the plugin.
        authenticated (bool): Indicates if the plugin is authenticated.
        client (OpenAI): The OpenAI client for interacting with GPT models.
        supported_actions (List[str]): List of actions supported by the plugin.
    """
    input_data_type = "image"
    output_data_type = "text"
    name = "ImageAnalysisPlugin"

    def __init__(self):
        self.authenticated = False
        self.client = None
        self.supported_actions = ["analyze_image"]

    def encode_image(self, image_path):
        """Encodes an image to a base64 string.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: The base64 encoded string of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def authenticate(self):
        if not self.authenticated:
            self.client = openai.OpenAI()  # TODO add handling here
            self.authenticated = True

    def analyze_image(self, image_path):
        """Analyzes an image and returns a description.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: The description of the image content.
        """
        base64_image = self.encode_image(image_path)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ],
                }
            ],
        )
        return response.choices[0].message.content

    @validate_action
    def execute(self, action, data, previous_result=None):
        """Executes a specified action with the provided data.

        Args:
            action (str): The action to perform.
            data (dict): The data required for the action.
            previous_result (Any, optional): The result of a previous action.

        Returns:
            Artifact: The result of the action execution.
        """
        artifact = Artifact(
            plugin=ImageAnalysisPlugin,
            data_type=self.output_data_type,
            status="success",
            timestamp=datetime.now(),
            metadata={"action": action}
        )

        if action == 'analyze_image':
            content = self.analyze_image(data["image_path"])
            artifact.metadata.update({"content": content})
            return artifact

class RandomImageGeneratorPlugin(PluginInterface):
    """RandomImageGeneratorPlugin is responsible for downloading images from URLs.

    Attributes:
        input_data_type (str): The type of input data the plugin accepts.
        output_data_type (str): The type of output data the plugin produces.
        name (str): The name of the plugin.
        supported_actions (List[str]): List of actions supported by the plugin.
    """
    input_data_type = "text"
    output_data_type = "image"
    name = "ImageDownloadPlugin"

    def __init__(self):
        self.supported_actions = ["download_image"]

    def download_image(self, url, destination):
        """Downloads an image from a URL to a specified destination.

        Args:
            url (str): The URL of the image to download.
            destination (str): The destination path to save the downloaded image.

        Returns:
            str: A message indicating the image download location.
        """
        os.system(f"wget {url} -O {destination}")
        return f"Image downloaded to: {destination}"

    def authenticate(self):
        pass

    @validate_action
    def execute(self, action, data, previous_result=None):
        """Executes a specified action with the provided data.

        Args:
            action (str): The action to perform.
            data (dict): The data required for the action.
            previous_result (Any, optional): The result of a previous action.

        Returns:
            Artifact: The result of the action execution.
        """
        artifact = Artifact(
            plugin=RandomImageGeneratorPlugin,
            data_type=self.output_data_type,
            status="success",
            timestamp=datetime.now(),
            metadata={"action": action}
        )

        if action == 'download_image':
            url = data["url"]
            destination = data["destination"]
            result = self.download_image(url, destination)
            artifact.metadata.update({"result": result})
            return artifact
