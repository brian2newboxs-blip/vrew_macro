#!/bin/bash
cd "$(dirname "$0")"
echo "Vrew 매크로 (Original GUI) 실행 중..."
# Use the virtual environment python to avoid system conflicts
.venv/bin/python vrew_macro.py
