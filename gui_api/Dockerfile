ARG fastapi_base=tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

FROM $fastapi_base

WORKDIR /app

ARG http_proxy
ARG https_proxy
ARG pip_install_options

COPY gui_api/requirements.txt .
RUN http_proxy="$http_proxy" https_proxy="$https_proxy" pip install -r requirements.txt ${pip_install_options}

COPY gui_api/app/ /app
COPY api_models/ /app/api_models