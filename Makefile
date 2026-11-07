build:
	uv run build.py

serve: build
	uv run python -m http.server -d site

clean:
	rm -rf site
