FROM v2fly/v2fly-core:latest

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    gcc \
    musl-dev

# Copy application files
COPY app/ /app
COPY config.json /etc/v2ray/config.json
WORKDIR /app

# Install Python dependencies
RUN pip3 install python-telegram-bot uuid fastapi uvicorn

# Start script
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT ["/start.sh"]