# Use official Node.js image for build
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the app source code
COPY . .

# Add these lines to accept build arguments and set them as environment variables
ARG REACT_APP_API_BASE_URL
ARG REACT_APP_IMAGE_API_URL
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL
ENV REACT_APP_IMAGE_API_URL=$REACT_APP_IMAGE_API_URL

# Build the React app for production (these env vars will be injected)
RUN npm run build:prod

# Use a lightweight web server to serve the static files
FROM nginx:alpine

# Copy built assets from previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"] 