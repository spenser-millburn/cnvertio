from typing import List
from pydantic import BaseModel
from src.plugin_interface import Artifact

class Stage(BaseModel):
    plugin: str
    action: str
    data: object

class Pipeline(BaseModel):
    steps: List[Stage]

class PipelineValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class InputValidator:
    def __init__(self, pipeline_engine):
        self.pipeline_engine = pipeline_engine

    def validate(self, stage: Stage, previous_result: Artifact):
        plugin = self.pipeline_engine.plugins.get(stage.plugin)

        if not plugin:
            raise PipelineValidationError(f"Plugin '{stage.plugin}' not found.")

        if previous_result and plugin.input_data_type != previous_result.data_type:
            raise PipelineValidationError(f"Input data type '{plugin.input_data_type}' is not compatible with previous output data type '{previous_result.data_type}'.")

class PipelineEngine:
    def __init__(self):
        self.plugins = {}
        self.input_validator = InputValidator(self)

    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin

    def execute_pipeline(self, pipeline):
        results = []
        for step in pipeline.steps:
            plugin_name = step.plugin
            action = step.action
            data = step.data

            plugin = self.plugins.get(plugin_name)

            if not plugin:
                raise ValueError(f"Plugin '{plugin_name}' not registered.")

            plugin.authenticate()

            if results:
                self.input_validator.validate(step, results[-1])

            result = plugin.execute(action=action, data=data, previous_result=results[-1] if results else None)
            results.append(result)

        return results
