#!/usr/bin/env bash
set -e

echo "🔧 Setting up your Django environment..."

sudo apt-get update -y
sudo apt-get install -y pkg-config libcairo2-dev libjpeg-dev zlib1g-dev libfreetype6-dev

python -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install django
fi

if [ -f "manage.py" ]; then
    python manage.py migrate || true
fi

nohup python manage.py runserver 0.0.0.0:8000 &
echo "✅ Django server started at http://localhost:8000"
