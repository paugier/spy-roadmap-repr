build:
	uv run build.py

serve:
	python -m http.server -d site
