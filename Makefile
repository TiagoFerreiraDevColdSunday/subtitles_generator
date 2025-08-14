windows_full_installation:
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

mac_os_full_installation:
	@if ! command -v brew >/dev/null 2>&1; then \
		echo "Homebrew not found. Installing..."; \
		/bin/bash -c "$$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; \
	fi
	brew install python
	brew install pipx
	pipx install poetry
	export PATH="$$HOME/.local/bin:$$PATH" 
	poetry config virtualenvs.in-project true
	poetry install
	poetry run python src/subtitles_generator/gui.py


run:
	poetry config virtualenvs.in-project true
	poetry install
	poetry run python src/subtitles_generator/gui.py