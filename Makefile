windows_full_instalation:
	@powershell -NoProfile -ExecutionPolicy Bypass -Command "\
		$$ErrorActionPreference='Stop'; \
		try { winget source update } catch {}; \
		try { if (-not (winget source list | Select-String -SimpleMatch 'msstore')) { winget source add -n msstore https://storeedgefd.dsx.mp.microsoft.com/v9.0/ } } catch {}; \
		$$ok=$$false; \
		try { winget install --id Python.Python.3.13 -e --accept-source-agreements --accept-package-agreements; $$ok=$$true } catch {}; \
		if (-not $$ok) { try { winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements; $$ok=$$true } catch {} }; \
		if (-not $$ok) { try { winget install --id Python.Python.3 -e --accept-source-agreements --accept-package-agreements; $$ok=$$true } catch {} }; \
		if (-not $$ok) { winget search Python.Python; throw 'Python not found in winget sources' }; \
		$$py=(Get-Command py -ErrorAction SilentlyContinue); \
		if ($$py) { $$PY='py' } else { $$PY='python' }; \
		& $$PY -m ensurepip --upgrade; \
		& $$PY -m pip install --user --upgrade pip; \
		& $$PY -m pip install --user pipx; \
		& $$PY -m pipx ensurepath; \
		$$env:PATH = \"$$env:USERPROFILE\\.local\\bin;$$env:PATH\"; \
		& $$PY -m pipx install --force poetry; \
		& $$PY -m pipx upgrade poetry; \
		poetry config virtualenvs.in-project true; \
		poetry env use $$((Get-Command python).Source); \
		if (-not (Test-Path 'pyproject.toml')) { throw 'pyproject.toml not found in current directory.' }; \
		poetry install; \
		poetry run python src/subtitles_generator/gui.py \
	"



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