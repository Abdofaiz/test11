#!/bin/sh
/usr/bin/v2ray run -config=/etc/v2ray/config.json &
python3 /app/bot.py