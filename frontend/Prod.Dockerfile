# Create image based on node image
FROM node:latest as build

# Set working directory
WORKDIR /app
ADD . /app

# Add /app/node_modules/.bin to environment variables
ENV PATH /app/node_modules/.bin:$PATH

# Install all app dependencies
COPY package.json /app/package.json
COPY .npmrc /app/.npmrc
RUN npm install
RUN npm install -g @angular/cli@7.3.9

# Build the app
RUN npm run build-prod

# Create image based on nginx and deploy our built Angular app
FROM nginx:1.17-alpine

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html/*

# Copy from the stage 1
COPY --from=build /app/dist/frontend /usr/share/nginx/html

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
