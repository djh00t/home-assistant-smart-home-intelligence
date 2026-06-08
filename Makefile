SHELL := /bin/bash

.PHONY: check quality-gates install clean build publish

check:
	@python3 scripts/validate_docs.py check

quality-gates: check
	@python3 scripts/validate_docs.py quality-gates

install:
	@python3 -m venv .venv

clean:
	@rm -rf .venv dist

build:
	@mkdir -p dist
	@printf '%s\n' 'Documentation bundle; no compiled artifact.' > dist/build.txt

publish: build
	@printf '%s\n' 'No publish target configured for this documentation bundle.'
