#!/usr/bin/env bash

# Save the path to the Python executable
PYTHON_EXE=$(which python)

# Save the path to the Python script you want to run
PYTHON_SCRIPT_PATH="/home/cats/Thesis_22_23/PE2LGP_Translator_2223/Modulo_construcao_regras/criacao_regras_automaticas.py"

# Save the path to the folder containing the HTML files
CORPUS_HTML_FOLDER_PATH="/home/cats/Thesis_22_23/PE2LGP_Translator_2223/Modulo_construcao_regras/Corpus/new_files"

# Iterate over the HTML files in the folder
for file in "$CORPUS_HTML_FOLDER_PATH"/*.html; do
    echo -e '\n'
    echo "Running the file: $(basename $file)"
    # Run the Python script with the current HTML file as an argument
    $PYTHON_EXE $PYTHON_SCRIPT_PATH "$CORPUS_HTML_FOLDER_PATH/$(basename $file)"
done