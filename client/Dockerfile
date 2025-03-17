FROM node:18-alpine

WORKDIR /client/

COPY package.json package-lock.json ./

RUN npm install

COPY . .

CMD ["npm", "run", "dev"]