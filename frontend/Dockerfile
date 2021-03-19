FROM node:latest

# Expose ports
EXPOSE 3000
EXPOSE 35729

# Set working directory
WORKDIR /app

# Add /app/node_modules/.bin to environment variables
ENV PATH /app/node_modules/.bin:$PATH

# Copy package files and install app dependencies
COPY package.json /app/package.json
COPY .npmrc /app/.npmrc
RUN npm install
RUN npm install -g @angular/cli@7.3.9

# Add Angular app to working directory
ADD . /app

# Start the Angular app
CMD ["npm", "start"]
