import signal
import threading
import tkinter as tk
from tkinter import ttk
from types import FrameType
from typing import Optional

class TextEditorWindow(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        title: str,
    ) -> None:
        super().__init__(parent)

        self._original_text = text

        self.result_text = text
        self.was_modified = False
        self.post_edit_biblatex_escape = False

        self.title(title)
        self.geometry("800x600")
        self.minsize(920, 800)

        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self._build_ui()
        self._load_text(text)

    def _build_ui(self) -> None:
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        editor_frame = ttk.Frame(self, padding=10)
        editor_frame.grid(row=0, column=0, sticky="nsew")

        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        self._text = tk.Text(
            editor_frame,
            wrap=tk.WORD,
            undo=True,
            font=("TkDefaultFont", 12),
        )
        self._text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            editor_frame,
            orient=tk.VERTICAL,
            command=self._text.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")

        self._text.configure(
            yscrollcommand=scrollbar.set,
        )

        button_frame = ttk.Frame(
            self,
            padding=(10, 0, 10, 10),
        )
        button_frame.grid(
            row=1,
            column=0,
            sticky="e",
        )

        self._post_edit_biblatex_escape = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            button_frame,
            text="Apply BibLaTeX escaping after editing",
            variable=self._post_edit_biblatex_escape,
        ).grid(
            row=0,
            column=0,
            padx=(0, 16),
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel,
        ).grid(
            row=0,
            column=1,
            padx=(0, 8),
        )

        ttk.Button(
            button_frame,
            text="Save",
            command=self._save,
        ).grid(
            row=0,
            column=2,
        )

        self.bind("<Escape>", self._on_cancel)
        self.bind("<Control-s>", self._on_save)
        self.bind("<Control-S>", self._on_save)

    def _load_text(self, text: str) -> None:
        self._text.insert("1.0", text)

    def show(self) -> None:
        self.update_idletasks()
        self._center_on_screen()

        self.deiconify()
        self.lift()

        self.wait_visibility()

        self.grab_set()
        self._text.focus_force()

    def _center_on_screen(self) -> None:
        self.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

    def _save(self) -> None:
        current_text = self._text.get("1.0", "end-1c")

        self.result_text = current_text
        self.was_modified = current_text != self._original_text
        self.post_edit_biblatex_escape = self._post_edit_biblatex_escape.get()

        self._close()

    def _cancel(self) -> None:
        self.result_text = self._original_text
        self.was_modified = False
        self.post_edit_biblatex_escape = False

        self._close()

    def _close(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass

        self.destroy()

    def _on_save(self, _: tk.Event) -> str:
        self._save()
        return "break"

    def _on_cancel(self, _: tk.Event) -> str:
        self._cancel()
        return "break"


class TextEditorDriver:
    def edit(
        self,
        text: str,
        *,
        title: str = "Entry preview",
    ) -> tuple[str, bool, bool]:

        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError(
                "TextEditorDriver.edit() must be executed "
                "from main thread"
            )

        try:
            root = tk.Tk()
        except tk.TclError as error:
            raise RuntimeError(
                "GUI was not instanciated "
            ) from error

        root.withdraw()

        window = TextEditorWindow(
            parent=root,
            text=text,
            title=title,
        )

        previous_sigint_handler = signal.getsignal(signal.SIGINT)

        def handle_sigint(
            signum: int,
            frame: Optional[FrameType],
        ) -> None:
            if window.winfo_exists():
                window.after_idle(window._cancel)

        def signal_poll() -> None:
            #NOTE for development purposes
            if root.winfo_exists():
                root.after(100, signal_poll)

        try:
            signal.signal(signal.SIGINT, handle_sigint)
            root.after(100, signal_poll)

            window.show()
            root.wait_window(window)

            return (
                window.result_text,
                window.was_modified,
                window.post_edit_biblatex_escape,
            )

        finally:
            signal.signal(signal.SIGINT, previous_sigint_handler)

            if root.winfo_exists():
                root.destroy()


def preview_entry_window(text: str) -> tuple[str, bool, bool]:
    return TextEditorDriver().edit(
        text,
        title="New Entry Preview and Edition",
    )
