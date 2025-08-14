windows_full_instalation:
	winget install Python.Python.3 --accept-source-agreements --accept-package-agreements
	python -m pip install --user pipx
	python -m pipx ensurepath
	$env:PATH = "$($env:USERPROFILE)\.local\bin;$env:PATH"
	pipx install --force poetry
	pipx upgrade poetry
	poetry config virtualenvs.in-project true
	poetry env use (Get-Command python).Source
	poetry install
	poetry run python src/subtitles_generator/gui.py

mac_os_full_instalation:
	brew install python
	brew install pipx
	pipx install poetry
	export PATH="$HOME/.local/bin:$PATH" 
	poetry config virtualenvs.in-project true
	poetry install
	poetry run python src/subtitles_generator/gui.py

SHELL := /bin/bash

linux_full_installation:
	set -e
	if command -v apt >/dev/null; then sudo apt update && sudo apt install -y python3 python3-pip pipx; \
	elif command -v dnf >/dev/null; then sudo dnf install -y python3 python3-pip pipx; \
	fi
	command -v pipx >/dev/null || { python3 -m pip install --user pipx; python3 -m pipx ensurepath; }
	export PATH="$(HOME)/.local/bin:$$PATH"; hash -r
	pipx install --force poetry
	pipx upgrade poetry || true
	poetry config virtualenvs.in-project true
	poetry env use $$(command -v python3)
	test -f pyproject.toml
	poetry install
	poetry run python src/subtitles_generator/gui.py


run:
	poetry config virtualenvs.in-project true
	poetry install
	poetry run python src/subtitles_generator/gui.py