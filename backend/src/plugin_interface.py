from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel


class PluginInterface:
    input_data_type: str
    output_data_type: str
    name:str

    def authenticate(self):
        raise NotImplementedError("Authenticate method not implemented.")

    def execute(self, action, data, previous_result):
        raise NotImplementedError("Execute method not implemented.")

    def __repr__(self):
        return f"PluginInterface(input_data_type={self.input_data_type}, output_data_type={self.output_data_type})"


@dataclass
class Artifact():
    data_type: str
    status: str
    timestamp: datetime
    metadata: dict
    plugin: PluginInterface

def validate_action(func):
    def wrapper(self, action, data=None, previous_result=None):
        if not action:
            raise ValueError("Action not provided!")
        if action not in self.supported_actions:
            raise ValueError(f"Action '{action}' not supported.")
        return func(self, action, data, previous_result)
    return wrapper
