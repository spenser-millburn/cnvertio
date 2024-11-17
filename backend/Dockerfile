FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
RUN pip install fastapi google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pydantic uvicorn requests openai


# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 6500

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "6500"]
