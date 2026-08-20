@echo off
setlocal
cd /d "%~dp0"
uv run uvicorn app.main:app --reload
