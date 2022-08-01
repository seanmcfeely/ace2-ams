ARG node_base=node:16-alpine
ARG nginx_base=nginx:1.22.0-alpine

# BUILD STAGE
FROM $node_base as builder

ARG http_proxy
ARG https_proxy
ARG npm_strict_ssl=true

WORKDIR /app

COPY package*.json .

RUN HTTP_PROXY="$http_proxy" HTTPS_PROXY="$https_proxy" apk --no-cache add --virtual native-deps \
  g++ gcc libgcc libstdc++ linux-headers make python 

RUN npm config set strict-ssl ${npm_strict_ssl} && \
  http_proxy="$http_proxy" https_proxy="$https_proxy" npm install node-gyp -g && \
  http_proxy="$http_proxy" https_proxy="$https_proxy" npm install && \
  apk del native-deps

COPY . .

RUN npm run build

# PRODUCTION STAGE
FROM $nginx_base as production

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]