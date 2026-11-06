build:
	uv run build.py

serve:
	uv run python -m http.server -d site

clean:
	rm -rf site
