SHELL := /bin/bash

.PHONY: check quality-gates install clean build publish

check:
	@python3 scripts/validate_docs.py check
	@python3 scripts/validate_project.py check
	@python3 scripts/validate_contracts.py check
	@python3 scripts/validate_features.py check
	@python3 scripts/validate_bridge.py check
	@python3 scripts/validate_room_fsm.py check
	@python3 scripts/validate_dwell_reset.py check
	@python3 scripts/validate_white_lighting.py check

quality-gates: check
	@python3 scripts/validate_docs.py quality-gates
	@python3 scripts/validate_project.py quality-gates
	@python3 scripts/validate_contracts.py quality-gates
	@python3 scripts/validate_features.py quality-gates
	@python3 scripts/validate_bridge.py quality-gates
	@python3 scripts/validate_room_fsm.py quality-gates
	@python3 scripts/validate_dwell_reset.py quality-gates
	@python3 scripts/validate_white_lighting.py quality-gates

install:
	@python3 -m venv .venv

clean:
	@rm -rf .venv dist __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov

build:
	@mkdir -p dist
	@printf '%s\n' 'Phase 0 foundation bundle; no compiled artifact.' > dist/build.txt

publish: build
	@printf '%s\n' 'No publish target configured for this phase 0 foundation bundle.'
