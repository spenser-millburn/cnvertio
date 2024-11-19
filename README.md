# Project Overview

This project consists of a frontend and backend application designed to execute data processing pipelines using various plugins. The frontend is built with React, while the backend is developed using FastAPI.

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Environment Variables:**

   Ensure you have the `OPENAI_API_KEY` set in your environment.

3. **Service Account File:**

   Place your Google service account JSON file at `/home/smillburn/Documents/conductor-441120-b2b06a8ce1c6.json`.

4. **Build and Run the Application:**

   Use Docker Compose to build and run the services:

   ```bash
   docker-compose up --build
   ```

## Accessing the Application

- **Frontend:** Access the React application at `http://localhost:3200`.
- **Backend:** The FastAPI backend is available at `http://localhost:6500`.

## Key Components

- **Frontend:** React application with a flow-based UI for executing data pipelines.
- **Backend:** FastAPI application with plugins for Google Drive, Google Sheets, Gmail, GPT transformations, and image analysis.

## Usage

- Use the frontend to interact with the pipeline execution flow.
- The backend processes requests and executes the specified pipeline steps using registered plugins.

## License

This project is licensed under the MIT License.
