import pysubs2
import os

def style_subtitles(file: str, subtitle_name: str, path: str) -> None:
    """
    Apply styles to the subtitles file.
    
    Args:
        file (str): Path to the subtitles file.
    """

    subs = pysubs2.load(file, encoding="utf-8")
    
    # Set global style
    style = pysubs2.SSAStyle()
    style.fontname = "Arial"
    style.fontsize = 25
    style.primarycolor = pysubs2.Color(255, 255, 255)  # white text
    style.outlinecolor = pysubs2.Color(0, 0, 0)        # black outline
    style.shadow = 2
    style.outline = 2

    subs.styles["Default"] = style

    output_path = os.path.join(path, subtitle_name + ".ass")
    subs.save(output_path)

