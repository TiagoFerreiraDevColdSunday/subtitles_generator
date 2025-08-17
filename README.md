# 🎙️ Fast Whisper AI Subtitle Generator

Generate subtitles from audio files using [Fast Whisper AI](https://github.com/SYSTRAN/faster-whisper).

ATTENTION: Just like any other speech-to-text LLM, it may produce transcription errors.

## How does it work?

The program watches a directory selected by the user. You specify:
- The **file type** you want to convert into subtitles (e.g., `.mp3`)
- A **trigger file type** (e.g., `.txt`)

Place all the `.mp3` files you want to convert into the watched directory. When you're ready, create the trigger `.txt` file in that directory. This signals the program to start converting all matching files into `.srt` and `.ass` subtitle files.

Then, you can apply those subtitles to your videos:

![Subtitles Example](prints/example_sub.png)

- `.srt` files are simpler and supported by most video players.
- `.ass` files are more polished and can include advanced styling (as shown above).

---
## Requirements

If you want to do it without using Makefile you would need the following to run the project:

- Python
- Poetry

Go to the project's root and run the following command:

```bash
poetry install
```

After this you should be able to execute:

```bash
poetry run python src/subtitles_generator/gui.py
```

---

## Makefile commands

### For Windows
```bash
make windows_full_installation
```

### For macOS
```bash
make mac_full_installation
```

To run without reinstalling:
```bash
make run
```

---

## GUI

The program uses **Gooey** for the graphical interface.  
You should see a layout similar to this:

![GUI](prints/layout.png)

### Parameter descriptions

| Parameter       | Description |
|-----------------|-------------|
| **language**    | The language you want Whisper to interpret |
| **directory**   | The directory the program will watch |
| **file_type**   | The file type you want to generate subtitles from (e.g., `mp3`) ffmpeg is almost capable of consuming any kind of audio file |
| **file_trigger**| When detected, the program starts searching for files with the `file_type` you specified |
| **parallel**    | If enabled, processes all detected files simultaneously (performance depends on your computer) |
| **recursive**    | If enabled, it will also watch for sub-directories traversed recursively |

---

## Process

1. Set the parameters and select the directory.

2. The program waits until it detects the trigger file you specified.  
   
   ![Waiting](prints/waiting.png)

3. Place your files in the directory, then create or move the trigger file there (e.g., `.txt`).

   ![txt](prints/txt.png)

4. Once the trigger file is detected, processing begins. The process may take some time all depends on how many files and their size.

   ![reading](prints/reading.png)

5. When finished, `.srt` and `.ass` files are generated.

   ![generated](prints/generated.png)
