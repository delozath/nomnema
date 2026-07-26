from omegaconf import DictConfig

from nomnema.ports.core import BaseService

from nomnema.storage.local_storage_validation import (
    LocalFileStorageValidation,
    LocalFolderStorageValidation,
)

from nomnema.adapters.tasks.extract_doi import (
  ExtractDOIfromMarkdown,
  FetchBibEntryfromDOI2Bibtex
)

from nomnema.adapters.tasks.extract_abstract import (
    #FetchAbstractFromPubMedDOI,
    #FetchAbstractFromCrossrefDOI,
    FetchAbstractChain
)

from nomnema.adapters.tasks.sanitize_text import (
    EntryTextSanitizer,
    BibLaTeXEscaper,
    BibKeyNormalizer
)

from nomnema.domain.biblatex import BiblatexDriver

class RetrieveOrchestrator(BaseService):
    def __init__(self, cfg: DictConfig, *args, **kwargs):
        self.cfg = cfg

        destination = cfg.get("destination", None)
        if destination is None:
            raise ValueError(f"param `destination` is required")
        self.destination = (
            LocalFolderStorageValidation(destination)
                .perform(mode="check")
            )

        bib_db_path = cfg.get("bib_db", None)
        if bib_db_path is None:
            raise ValueError(f"param `bib_db` is required")
        self.bib_db_path = (
            LocalFileStorageValidation(bib_db_path)
                .perform(mode="check")
            )
        
        self.fetch_bib_entry = FetchBibEntryfromDOI2Bibtex()
        self.entry_text_sanitizer = EntryTextSanitizer()
        self.bib_driver = BiblatexDriver(bib_path=self.bib_db_path)
    
    def run(self, *args, **kwargs):
        # file_biblatex = LocalFolderStorageValidation(self.pfname).perform(mode="check")
        #origin = LocalFileStorageValidation(self.origin).perform(mode="check")
        
        origin = self.cfg.get("origin", None)
        if origin is None:
            raise ValueError(f"param `origin` is required")
        origin = (
            LocalFileStorageValidation(origin)
                .perform(mode="check")
            )
        doi_candidate = ExtractDOIfromMarkdown.perform(origin)
        entry_candidate = self.fetch_bib_entry.perform(doi_candidate, timeout_s=10.0)

        fetch_chain = FetchAbstractChain(doi_candidate, 'omar@mail.net')
        abstract_candidate, log_abstract_fetch = fetch_chain.run(clear=True)

        if abstract_candidate=="":
            raise ValueError(f"Failed to retrieve abstract for doi: {doi_candidate}")
        
        abstract = self.entry_text_sanitizer(abstract_candidate)

        entry = self.bib_driver.append_abstract(entry_candidate, abstract)

        if entry['doi'] in self.bib_driver.cache_unique_doi:
            raise ValueError(f"Duplicate DOI found: {entry['doi']}")

        bib_entry = self.bib_driver.dict_to_bibtex(entry)
        #self.bib_driver.add_entry(entry)
        bib_entry_edited, modified = process_text(bib_entry)







import signal
import threading
import tkinter as tk
from tkinter import ttk
from types import FrameType
from typing import Optional


class TextEditorWindow(tk.Toplevel):
    """Ventana modal para editar texto."""

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

        self.title(title)
        self.geometry("700x450")
        self.minsize(450, 300)

        # Se mantiene oculta mientras se construye.
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
            font=("TkDefaultFont", 11),
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

        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self._cancel,
        ).grid(
            row=0,
            column=0,
            padx=(0, 8),
        )

        ttk.Button(
            button_frame,
            text="Guardar",
            command=self._save,
        ).grid(
            row=0,
            column=1,
        )

        self.bind("<Escape>", self._on_cancel)
        self.bind("<Control-s>", self._on_save)
        self.bind("<Control-S>", self._on_save)

    def _load_text(self, text: str) -> None:
        self._text.insert("1.0", text)

    def show(self) -> None:
        """
        Muestra la ventana y activa el comportamiento modal.

        El orden es importante:
        1. Mostrar.
        2. Esperar a que sea visible.
        3. Tomar el grab.
        """
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

        self._close()

    def _cancel(self) -> None:
        self.result_text = self._original_text
        self.was_modified = False

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
    """Administra Tkinter y expone la operación de edición."""

    def edit(
        self,
        text: str,
        *,
        title: str = "Editor de texto",
    ) -> tuple[str, bool]:

        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError(
                "TextEditorDriver.edit() debe ejecutarse "
                "desde el hilo principal."
            )

        try:
            root = tk.Tk()
        except tk.TclError as error:
            raise RuntimeError(
                "No fue posible iniciar la interfaz gráfica. "
                "Verifica que exista un servidor gráfico disponible."
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
            # Se agenda el cierre dentro del ciclo de eventos de Tk.
            if window.winfo_exists():
                window.after_idle(window._cancel)

        def signal_poll() -> None:
            """
            Obliga a Tkinter a regresar periódicamente al intérprete de
            Python para que Ctrl+C pueda procesarse.
            """
            if root.winfo_exists():
                root.after(100, signal_poll)

        try:
            signal.signal(signal.SIGINT, handle_sigint)
            root.after(100, signal_poll)

            window.show()
            root.wait_window(window)

            return window.result_text, window.was_modified

        finally:
            signal.signal(signal.SIGINT, previous_sigint_handler)

            if root.winfo_exists():
                root.destroy()


def process_text(text: str) -> tuple[str, bool]:
    return TextEditorDriver().edit(
        text,
        title="Editar contenido",
    )