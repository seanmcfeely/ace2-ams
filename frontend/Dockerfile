ARG cypress_base=public.ecr.aws/cypress-io/cypress/included:10.3.1

FROM $cypress_base

ARG http_proxy
ARG https_proxy
ARG npm_strict_ssl=true

RUN http_proxy="$http_proxy" https_proxy="$https_proxy" apt-get install -y curl

WORKDIR /app

COPY package*.json ./

RUN npm config set strict-ssl ${npm_strict_ssl} && http_proxy="$http_proxy" https_proxy="$https_proxy" npm install 

COPY --chown=root:root . .

# Override the entrypoint of the cypress/included image
ENTRYPOINT ["bash", "-c", "while !</dev/tcp/gui-api/80; do sleep 1; done; npm run dev"]
