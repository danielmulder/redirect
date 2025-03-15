#!/bin/bash

echo "Starting Gunicorn server..."
exec gunicorn -b 0.0.0.0:8080 app:create_app
