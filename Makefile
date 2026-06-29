build:
	git submodule update --init --recursive

lint:
	python3 scripts/lint_wiki.py wiki/

.PHONY: build lint