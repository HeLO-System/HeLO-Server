#!/bin/sh
gunicorn helo-server:app -b 0.0.0.0:5000