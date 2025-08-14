# gui.py
from gooey import Gooey, GooeyParser
from main import call_event  # your Typer function; safe to call directly

@Gooey(program_name="Subtitles Generator")
def main():
    p = GooeyParser(description="Watch a folder and generate subtitles for each file in it.")
    
    # Args
    p.add_argument("language", default="en")
    p.add_argument("directory", widget="DirChooser")
    p.add_argument("file_trigger", default=".txt")
    p.add_argument("file_type", default="mp3")
    p.add_argument("--parallel", action="store_true", help="Process files in parallel")
    
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
