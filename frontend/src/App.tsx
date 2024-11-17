import React, { useState } from 'react';
import './App.css';
import { API_HOST } from './constants';
import RequestButton from './components/RequestButton';
import JsonView from '@uiw/react-json-view';
import Stack from '@mui/material/Stack';

export default function App() {
  const [responsea, setResponsea] = useState({ "data": "No Route Data yet" });
  const [responseb, setResponseb] = useState({ "data": "No Route Data yet" });
  const [responsec, setResponsec] = useState({ "data": "No Route Data yet" });
  const [responsed, setResponsed] = useState({ "data": "No Route Data yet" });

  const pipelineSteps = [
    { plugin: "google_drive", action: "upload_file", data: {file_path: "./hello.txt"}},
    { plugin: "google_drive", action: "download_file", data: {"file_id":"15EuDWZaa2H8R24JinXkZENU8bsuNE8zN",  "file_path" : "test_download.txt"}},
    // { plugin: "gpt_transform", action: "transform_text", data: { source: "apples", transformation: " what is this respond in one sentance what it depicts dont mention ascii art  and be detailed" } },
    { plugin: "gpt_transform", action: "transform_file", data: { source_path: "test_download.txt", transformation: " what is this respond in one sentance what it depicts dont mention ascii art  and be detailed" } },
    { plugin: "google_drive", action: "upload_file", data: {"file_path" : "test_download.txt"} }
  ];

  return (
    <div className="App">
      <Stack direction="row" spacing={2}>
        <RequestButton
          buttonText='Upload Data'
          url="http://localhost:6500/execute_pipeline"
          requestType="POST"
          requestData={{
            steps: [pipelineSteps[0]]
          }}
          responseHandler={setResponsea}
        />
        <RequestButton
          buttonText='Download Data'
          url="http://localhost:6500/execute_pipeline"
          requestType="POST"
          requestData={{
            steps: [pipelineSteps[1]]
          }}
          responseHandler={setResponseb}
        />
        <RequestButton
          buttonText='Transform Data'
          url="http://localhost:6500/execute_pipeline"
          requestType="POST"
          requestData={{
            steps: [pipelineSteps[2]]
          }}
          responseHandler={setResponsec}
        />
        <RequestButton
          buttonText='Transform Data'
          url="http://localhost:6500/execute_pipeline"
          requestType="POST"
          requestData={{
            steps: [pipelineSteps[3]]
          }}
          responseHandler={setResponsed}
        />
      </Stack>
      <div style={{ padding: "10px" }}>
        <h1>Src Upload</h1>
        <JsonView value={responsea} collapsed={false} />
        <h1>Src Download</h1>
        <JsonView value={responseb} collapsed={false} />
        <h1>Transformer Response</h1>
        <JsonView value={responsec} collapsed={false} />
        <h1>Dest Response</h1>
        <JsonView value={responsed} collapsed={false} />
      </div>
    </div>
  );
}
