FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends git make lnav \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir 'kontiki==2.0.0' 'kontiki-tui==2.0.0'
