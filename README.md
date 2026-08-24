# Nomnema

Nomnema is a work-in-progress tool for turning downloaded academic PDFs into an organized, BibLaTeX-backed literature collection.

Given a PDF that contains a DOI, Nomnema:

1. extracts the DOI from the document;
2. retrieves a BibTeX record from `doi.org`;
3. looks for an abstract in PubMed and then Crossref;
4. normalizes the citation key and selected metadata;
5. opens an editable desktop preview of the generated BibTeX entry;
6. appends the approved entry to an existing `.bib` database;
7. moves the PDF into a dedicated destination folder; and
8. creates a Markdown companion file containing the title, authors, DOI, and abstract.

This is useful when papers accumulate in a downloads folder and you want one command to file the document, update your bibliography, and create a readable metadata note.

> [!WARNING]
> Nomnema is under active development. Its command-line interface, configuration, and output conventions may change. The current workflow depends heavily on `just` recipes; upcoming versions will provide several direct entry points and make the application easier to run without relying so much on justfiles.

## Current workflow

For an entry whose generated key is `Smith_2025`, running Nomnema produces a structure similar to this:

```text
/path/to/library/
└── Smith_2025/
    ├── Smith_2025.pdf
    └── Smith_2025.md
```

It also appends the entry to the configured BibLaTeX database and adds a `file` field pointing to the stored PDF. The key is currently derived from the first author token and the publication year.

Before any files or bibliography data are changed, a Tk desktop window displays the generated entry. You can:

- edit the BibTeX text;
- optionally apply BibLaTeX escaping after editing;
- save with **Save** or `Ctrl+S`; or
- abort with **Cancel** or `Esc`.

Cancelling leaves the source PDF and bibliography unchanged.

## Requirements

- Python 3.12 or newer. Although the current package metadata says Python 3.11, the source uses `typing.override`, which is available in Python 3.12.
- A graphical desktop session with Tk support.
- Internet access to retrieve records from DOI.org, PubMed, and Crossref.
- An existing BibLaTeX `.bib` file.
- An existing destination directory.
- [`just`](https://github.com/casey/just) for the recommended development workflow.
- `xclip` only if you want to process a PDF path from the X11 clipboard.

On Debian or Ubuntu, the required system packages can be installed with:

```bash
sudo apt install python3-tk just
```

For clipboard support, also install:

```bash
sudo apt install xclip
```

Package names may differ on other operating systems. The clipboard recipe currently targets X11 environments.

## Installation from source

Clone or download the repository and enter its directory. The `justfile` loads
`.env` automatically and runs Nomnema with the Python interpreter configured by
the `PYTHON` variable.

Install Nomnema in editable mode **no yet tested**:

```bash
python -m pip install -e .
```

The project metadata does not yet declare every runtime dependency. Until packaging is completed, install the remaining dependencies explicitly:

```bash
python -m pip install \
  requests \
  python-dotenv \
  pyperclip \
  "bibtexparser<2" \
  pandas \
  click \
```

## Configuration

Copy the example justfile and environment file:

```bash
cp example.just justfile
cp .env.example .env
```

At minimum, set these values in `.env`:

```dotenv
BIB_DB=/home/user/references/library.bib
DESTINATION=/home/user/references/papers
```

`BIB_DB` must point to an existing `.bib` file, even if it is empty, and `DESTINATION` must be an existing directory.

The sample `.env.example` also contains `ORIGIN` and `FNAME_SUFFIX`. The provided justfile currently receives the source path as a recipe argument, and a filename suffix can be supplied through a direct Hydra invocation as shown below.

To use a specific Python interpreter, define `PYTHON` when invoking `just` or add it to `.env`:

```dotenv
PYTHON=/home/user/path/to/nomnema/.venv/bin/python
```

If `PYTHON` is not set, the example justfile uses `/usr/bin/python3`. Setting it explicitly is therefore recommended when using a virtual environment.

## Usage

List the available recipes:

```bash
just
```

### Process a PDF

```bash
just run-pdf "/home/user/Downloads/paper.pdf"
```

The PDF must contain a recognizable DOI near the beginning of its extracted text.

### Assign a BibLaTeX group

Pass a second argument to add a `groups` field to the entry:

```bash
just run-pdf "/home/user/Downloads/paper.pdf" "Machine Learning"
```

### Process the path stored in the clipboard

Copy the full PDF path—not the PDF file itself—to the X11 clipboard, then run:

```bash
just run-clb
```

An optional group can also be supplied:

```bash
just run-clb "To Read"
```

### Run without `just`

The application can currently be invoked through its Python module and Hydra overrides:

```bash
PYTHONPATH=src python -m nomnema.main \
  bib_db="/home/user/references/library.bib" \
  destination="/home/user/references/papers" \
  origin="/home/user/Downloads/paper.pdf"
```

With an optional group and filename suffix:

```bash
PYTHONPATH=src python -m nomnema.main \
  bib_db="/home/user/references/library.bib" \
  destination="/home/user/references/papers" \
  origin="/home/user/Downloads/paper.pdf" \
  group="Machine Learning" \
  fname_suffix="_reviewed"
```

`fname_suffix` changes the PDF filename inside the generated entry directory. It is useful when that filename already exists.

## Important behavior

- Nomnema **moves** the source PDF; it does not copy it.
- A duplicate DOI already present in the BibLaTeX database is rejected.
- Existing output files are not overwritten.
- The destination subdirectory is created automatically, but its parent destination must already exist.
- If neither PubMed nor Crossref provides an abstract, the entry is stored with an empty abstract.
- Editing malformed BibTeX in the preview can cause parsing to fail, so keep the entry syntactically valid.
- The application currently needs a graphical display and cannot run headlessly.

## Development and tests

Install the test runner and execute the suite with:

```bash
python -m pip install pytest
python -m pytest
```

Some adapter tests perform live network requests and expect local `.env-test` values and sample PDFs that are not part of the public configuration. Run focused unit tests when those fixtures are unavailable, for example:

```bash
python -m pytest tests/domain tests/storage tests/services
```

## Project status

Nomnema is experimental software and is not yet packaged as a polished end-user application. Near-term development is expected to include multiple entry points for different workflows, simpler installation, complete dependency metadata, and execution paths that do not depend as heavily on `just` and project-specific justfiles.
