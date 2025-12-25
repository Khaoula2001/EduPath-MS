FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --fetch-retry-mintimeout 20000 --fetch-retry-maxtimeout 120000 --fetch-retries 10
COPY . .
EXPOSE 4000
CMD ["npm", "start"]
