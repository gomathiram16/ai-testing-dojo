.PHONY: app check test

app:
	uvicorn app.main:app --reload --reload-dir app --port 8000

check:
	python -c "import fastapi, httpx, pytest; print('deps ok')"
	python -c "from app.main import app; print('app import ok')"

test:
	python -m pytest -q

ready:
	python verify_ready.py
