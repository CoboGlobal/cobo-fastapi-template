FROM python:3.10-bookworm

ARG GIT_TAG
# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive
# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /src

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

ENV GIT_TAG=${GIT_TAG}
COPY app /src