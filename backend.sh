#!/bin/sh

cd /app
alembic revision --autogenerate -m "init"
alembic upgrade head

python3 -m api