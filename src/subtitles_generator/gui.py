# gui.py
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from faster_whisper.tokenizer import _LANGUAGE_CODES
from main import call_event, call_select

COMMON_TYPES = ["txt", "md", "csv", "json", "xml", "yaml", "yml", "pdf", "docx", "xlsx"]
LANGUAGES = sorted(_LANGUAGE_CODES)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SubtitlesGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Subtitles Generator")
        self.geometry("620x520")
        self.resizable(False, False)

        # ── Tab View ──
        self.tabs = ctk.CTkTabview(self, width=580, height=460)
        self.tabs.pack(padx=20, pady=20)

        self._build_watch_tab()
        self._build_select_tab()

    # ────────────────────────────────────────────
    #  Watch Folder Tab
    # ────────────────────────────────────────────
    def _build_watch_tab(self):
        tab = self.tabs.add("Watch Folder")

        # Language
        ctk.CTkLabel(tab, text="Language").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        self.watch_language = ctk.CTkComboBox(tab, values=LANGUAGES, width=260)
        self.watch_language.set("en")
        self.watch_language.grid(row=0, column=1, padx=10, pady=(10, 0))

        # Directory
        ctk.CTkLabel(tab, text="Directory").grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))
        self.watch_dir_var = ctk.StringVar()
        dir_frame = ctk.CTkFrame(tab, fg_color="transparent")
        dir_frame.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="ew")
        ctk.CTkEntry(dir_frame, textvariable=self.watch_dir_var, width=200).pack(side="left")
        ctk.CTkButton(dir_frame, text="Browse", width=55, command=lambda: self._browse_dir(self.watch_dir_var)).pack(side="left", padx=(5, 0))

        # File trigger
        ctk.CTkLabel(tab, text="Trigger File Type").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
        self.watch_trigger = ctk.CTkComboBox(tab, values=COMMON_TYPES, width=260)
        self.watch_trigger.set("txt")
        self.watch_trigger.grid(row=2, column=1, padx=10, pady=(10, 0))

        # File type
        ctk.CTkLabel(tab, text="Audio File Type").grid(row=3, column=0, sticky="w", padx=10, pady=(10, 0))
        self.watch_file_type = ctk.CTkEntry(tab, width=260)
        self.watch_file_type.insert(0, "mp3")
        self.watch_file_type.grid(row=3, column=1, padx=10, pady=(10, 0))

        # Parallel
        self.watch_parallel = ctk.CTkCheckBox(tab, text="Parallel")
        self.watch_parallel.grid(row=4, column=0, padx=10, pady=(15, 0), sticky="w")

        # Recursive
        self.watch_recursive = ctk.CTkCheckBox(tab, text="Recursive")
        self.watch_recursive.grid(row=4, column=1, padx=10, pady=(15, 0), sticky="w")

        # Start button
        ctk.CTkButton(tab, text="Start Watching", command=self._on_watch_start).grid(
            row=5, column=0, columnspan=2, pady=(25, 0)
        )

    # ────────────────────────────────────────────
    #  Select Files Tab
    # ────────────────────────────────────────────
    def _build_select_tab(self):
        tab = self.tabs.add("Select Files")

        # Language
        ctk.CTkLabel(tab, text="Language").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        self.select_language = ctk.CTkComboBox(tab, values=LANGUAGES, width=260)
        self.select_language.set("en")
        self.select_language.grid(row=0, column=1, padx=10, pady=(10, 0))

        # Files
        ctk.CTkLabel(tab, text="Audio Files").grid(row=1, column=0, sticky="w", padx=10, pady=(10, 0))
        self.select_files_var = ctk.StringVar()
        files_frame = ctk.CTkFrame(tab, fg_color="transparent")
        files_frame.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="ew")
        ctk.CTkEntry(files_frame, textvariable=self.select_files_var, width=200).pack(side="left")
        ctk.CTkButton(files_frame, text="Browse", width=55, command=self._browse_files).pack(side="left", padx=(5, 0))

        # Output directory
        ctk.CTkLabel(tab, text="Output Directory").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
        self.select_out_dir_var = ctk.StringVar()
        out_frame = ctk.CTkFrame(tab, fg_color="transparent")
        out_frame.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="ew")
        ctk.CTkEntry(out_frame, textvariable=self.select_out_dir_var, width=200).pack(side="left")
        ctk.CTkButton(out_frame, text="Browse", width=55, command=lambda: self._browse_dir(self.select_out_dir_var)).pack(side="left", padx=(5, 0))

        # Parallel
        self.select_parallel = ctk.CTkCheckBox(tab, text="Parallel")
        self.select_parallel.grid(row=3, column=0, padx=10, pady=(15, 0), sticky="w")

        # Start button
        ctk.CTkButton(tab, text="Generate Subtitles", command=self._on_select_start).grid(
            row=4, column=0, columnspan=2, pady=(25, 0)
        )

    # ────────────────────────────────────────────
    #  Helpers
    # ────────────────────────────────────────────
    def _browse_dir(self, var: ctk.StringVar):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def _browse_files(self):
        paths = filedialog.askopenfilenames(
            title="Select audio files",
            filetypes=[
                ("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg *.wma *.aac *.mp4"),
                ("All files", "*.*"),
            ],
        )
        if paths:
            self.select_files_var.set(";".join(paths))

    def _on_watch_start(self):
        directory = self.watch_dir_var.get()
        if not directory:
            messagebox.showwarning("Missing field", "Please select a directory to watch.")
            return

        threading.Thread(
            target=call_event,
            kwargs=dict(
                language=self.watch_language.get(),
                directory=directory,
                file_trigger=self.watch_trigger.get(),
                file_type=self.watch_file_type.get(),
                parallel=bool(self.watch_parallel.get()),
                recursive=bool(self.watch_recursive.get()),
            ),
            daemon=True,
        ).start()
        messagebox.showinfo("Watching", f"Now watching:\n{directory}")

    def _on_select_start(self):
        files_str = self.select_files_var.get()
        if not files_str:
            messagebox.showwarning("Missing field", "Please select at least one audio file.")
            return

        files = [f for f in files_str.split(";") if f]
        output_directory = self.select_out_dir_var.get() or None

        threading.Thread(
            target=call_select,
            kwargs=dict(
                language=self.select_language.get(),
                files=files,
                output_directory=output_directory,
                parallel=bool(self.select_parallel.get()),
            ),
            daemon=True,
        ).start()
        messagebox.showinfo("Processing", f"Generating subtitles for {len(files)} file(s)...")


def main():
    app = SubtitlesGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
