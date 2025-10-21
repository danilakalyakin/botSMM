#!/bin/bash
export PORT=$PORT
gunicorn bot:app --bind 0.0.0.0:$PORT
