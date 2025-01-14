FROM alpine:latest

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
FROM alpine:latest
EXPOSE 8080
WORKDIR /app
RUN wget https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip && unzip v2ray-linux-64.zip && rm v2ray-linux-64.zip && rm config.json
COPY config.json /app
ENTRYPOINT ["./v2ray","run"]
# Start script
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT ["/start.sh"]
