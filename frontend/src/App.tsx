import React from 'react'; import './App.css'; import { API_HOST } from './constants'; import RequestButton from './components/RequestButton'; import Stack from '@mui/material/Stack'; import Card from '@mui/material/Card'; import CardContent from '@mui/material/CardContent'; import JsonView from '@uiw/react-json-view'; 

export default function App() { 
  const pipelineSteps = [ 
    { plugin: "google_drive", action: "upload_file", data: { file_path: ".temp/hello.txt" } }, 
    { plugin: "google_drive", action: "download_file", data: { "file_id": "15EuDWZaa2H8R24JinXkZENU8bsuNE8zN", "file_path": "test_download.txt" } }, 
    { plugin: "gpt_transform", action: "transform_file", data: { source_path: ".temp/test_download.txt", transformation: " what is this respond in one sentance what it depicts dont mention ascii art and be detailed" } }, 
    { plugin: "google_drive", action: "upload_file", data: { "file_path": ".temp/test_download.txt" } } 
  ]; 

  return ( 
    <div className="App" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}> 
      <Stack direction="row" spacing={10}> 
        <Card style={{ width: 400, height: 800, overflowY: 'auto', whiteSpace: 'pre-wrap' }}> 
          <CardContent> 
            <RequestButton 
              buttonText='Upload Data' 
              url="http://localhost:6500/execute_pipeline" 
              requestType="POST" 
              requestData={{ steps: [pipelineSteps[0]] }} 
            /> 
          </CardContent> 
        </Card> 
        <Card style={{ width: 400, height: 800, overflowY: 'auto', whiteSpace: 'pre-wrap' }}> 
          <CardContent> 
            <RequestButton 
              buttonText='Download Data' 
              url="http://localhost:6500/execute_pipeline" 
              requestType="POST" 
              requestData={{ steps: [pipelineSteps[1]] }} 
            /> 
          </CardContent> 
        </Card> 
        <Card style={{ width: 400, height: 800, overflowY: 'auto', whiteSpace: 'pre-wrap' }}> 
          <CardContent> 
            <RequestButton 
              buttonText='Transform Data' 
              url="http://localhost:6500/execute_pipeline" 
              requestType="POST" 
              requestData={{ steps: [pipelineSteps[2]] }} 
            /> 
          </CardContent> 
        </Card> 
        <Card style={{ width: 400, height: 800, overflowY: 'auto', whiteSpace: 'pre-wrap' }}> 
          <CardContent> 
            <RequestButton 
              buttonText='Upload Transformed Data' 
              url="http://localhost:6500/execute_pipeline" 
              requestType="POST" 
              requestData={{ steps: [pipelineSteps[3]] }} 
            /> 
          </CardContent> 
        </Card> 
        <Card style={{ width: 400, height: 800, overflowY: 'auto', whiteSpace: 'pre-wrap' }}> 
          <CardContent> 
            <RequestButton 
              buttonText='Execute All Stages' 
              url="http://localhost:6500/execute_pipeline" 
              requestType="POST" 
              requestData={{ steps: pipelineSteps }} 
            /> 
          </CardContent> 
        </Card> 
      </Stack> 
    </div> 
  ); 
}
