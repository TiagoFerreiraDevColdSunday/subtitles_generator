# 🎙️ Whisper AI Subtitle Generator

Generate subtitles from speech using [Whisper AI](https://github.com/openai/whisper).

---

## 📦 Requirements

You need **[Poetry](https://python-poetry.org/)** and `pipx` to run this project.

---

## 🛠️ Setup Instructions

### Install `pipx`

#### Windows

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
```

Restart your terminal after running these commands.

---

#### Linux

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Restart your terminal.

---

#### macOS

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Restart your terminal.

---

### Install `poetry` (all platforms)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Make sure Poetry is in your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## ▶️ Run the Project

```bash
poetry run python3 main.py <language> <directory> <trigger_file>
```

### 🧵 How It Works

- A **thread** is created for the specified `<directory>`.
- Drop any `.mp3` files into that folder.
- When the specified `<trigger_file>` is written to or modified, the thread will trigger and start converting all `.mp3` files into subtitles using Whisper.



## 📝 Backlog / TODO

- Improve the visual design of the generated subtitles (will use pysubs2)

- Improve AI quality
