# Example justfile for running Nomnema from a source checkout.
# Copy this file to `justfile`, configure BIB_DB and DESTINATION in `.env`,
# then run `just`, `just run-pdf file.pdf`, or `just run-clb`.
set dotenv-load := true

export PYTHONPATH := "src"
python := env_var_or_default("PYTHON", "/usr/bin/python3")


# List the available commands.
default:
    @just --list

fname := "file.pdf"


# Process a PDF, optionally assigning it to a group.
run-pdf fname group="":
    {{ python }} -m nomnema.main \
        bib_db="$BIB_DB" \
        destination="$DESTINATION" \
        origin="{{ fname }}"{{ if group == "" { "" } else { " group=\"" + group + "\"" } }}


# Process the PDF path currently stored in the X11 clipboard.
run-clb group="":
    #!/usr/bin/env bash
    set -eu
    clipboard="$(xclip -selection clipboard -o)"
    just run-pdf "$clipboard" "{{ group }}"
