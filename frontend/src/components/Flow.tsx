import React, { useCallback } from "react";
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge } from "@xyflow/react";
import Node from "./Node"; // Import the custom node component
import "@xyflow/react/dist/style.css";

const initialNodes = [
  {
    id: "1",
    type: "custom",
    position: { x: 0, y: 0 },
    data: {
      buttonText: "Upload Data",
      url: "http://localhost:6500/execute_pipeline",
      requestType: "POST",
      requestData: {
        steps: [
          {
            plugin: "google_drive",
            action: "upload_file",
            data: { file_path: ".temp/hello.txt" },
          },
        ],
      },
    },
  },
  {
    id: "2",
    type: "custom",
    position: { x: 500, y: 200 },
    data: {
      buttonText: "Download Data",
      url: "http://localhost:6500/execute_pipeline",
      requestType: "POST",
      requestData: {
        steps: [
          {
            plugin: "google_drive",
            action: "download_file",
            data: {
              file_id: "15EuDWZaa2H8R24JinXkZENU8bsuNE8zN",
              file_path: "test_download.txt",
            },
          },
        ],
      },
    },
  },
  {
    id: "3",
    type: "custom",
    position: { x: 1000, y: 200 },
    data: {
      buttonText: "Transform Data",
      url: "http://localhost:6500/execute_pipeline",
      requestType: "POST",
      requestData: {
        steps: [
          {
            plugin: "gpt_transform",
            action: "transform_file",
            data: {
              source_path: ".temp/test_download.txt",
              transformation: " what is this respond in one sentance what it depicts dont mention ascii art and be detailed",
            },
          },
        ],
      },
    },
  },
  {
    id: "4",
    type: "custom",
    position: { x: 1500, y: 200 },
    data: {
      buttonText: "Upload Transformed Data",
      url: "http://localhost:6500/execute_pipeline",
      requestType: "POST",
      requestData: {
        steps: [
          {
            plugin: "google_drive",
            action: "upload_file",
            data: { file_path: ".temp/test_download.txt" },
          },
        ],
      },
    },
  },
  {
    id: "5",
    type: "custom",
    position: { x: 2000, y: 200 },
    data: {
      buttonText: "Execute All Stages",
      url: "http://localhost:6500/execute_pipeline",
      requestType: "POST",
      requestData: {
        steps: [
          { plugin: "google_drive", action: "upload_file", data: { file_path: ".temp/hello.txt" } },
          { plugin: "google_drive", action: "download_file", data: { file_id: "15EuDWZaa2H8R24JinXkZENU8bsuNE8zN", file_path: "test_download.txt" } },
          { plugin: "gpt_transform", action: "transform_file", data: { source_path: ".temp/test_download.txt", transformation: " what is this respond in one sentance what it depicts dont mention ascii art and be detailed" } },
          { plugin: "google_drive", action: "upload_file", data: { file_path: ".temp/test_download.txt" } }
        ],
      },
    },
  },
];

const initialEdges = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" },
  { id: "e3-4", source: "3", target: "4" },
 { id: "e4-5", source: "4", target: "5" },
];

export function FlowUI() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params:any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const nodeTypes = { custom: Node }; // Define the custom node type

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes} // Use the custom node type
      >
        <Controls />
        <MiniMap />
        <Background gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}

export default FlowUI;
