FROM node:16.10-slim

WORKDIR /app

# Copy app code
COPY . .

# Install dependencies and build
RUN yarn install 
RUN yarn add --dev typescript
RUN yarn build

# Expose the port
EXPOSE 8080

# Start the app
ENTRYPOINT npx react-inject-env set && npx http-server build
