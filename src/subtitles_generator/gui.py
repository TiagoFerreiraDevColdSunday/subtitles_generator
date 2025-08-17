# gui.py
from gooey import Gooey, GooeyParser
from main import call_event  # your Typer function; safe to call directly
from faster_whisper.tokenizer import _LANGUAGE_CODES

COMMON_TYPES = ["txt", "md", "csv", "json", "xml", "yaml", "yml", "pdf", "docx", "xlsx"]

@Gooey(program_name="Subtitles Generator")
def main():
    p = GooeyParser(description="Watch a folder and generate subtitles for each file in it.")
    
    # Args
    p.add_argument("language", choices=_LANGUAGE_CODES, default="en", help="Language for subtitles generation")
    p.add_argument("directory", widget="DirChooser", help="Directory to watch for new files")
    p.add_argument("file_trigger", choices=COMMON_TYPES, default="txt", help="File type to trigger the program when created.")
    p.add_argument("file_type", default="mp3", help="Type of file to process (e.g., mp3, wav, etc.)")
    p.add_argument("--parallel", action="store_true", help=" Process files in parallel")
    p.add_argument("--recursive", action="store_true", help=" Will watch for sub-directories traversed recursively")
    
    args = p.parse_args()

    call_event(
        language=args.language,
        directory=args.directory,
        file_trigger=args.file_trigger,
        file_type=args.file_type,
        parallel=args.parallel,
    )

if __name__ == "__main__":
    main()
