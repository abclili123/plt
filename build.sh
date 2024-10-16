#!/bin/bash

# MacOS / Linux

check_python(){
    if ! command -v python3 &>/dev/null; then
        echo "Install Python3 to run script"
        exit 1
    fi
}

lexer() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        echo "Usage: $0 <input_filename> <output_filename>"
        exit 1
    fi

    python3 lexer.py "$1" "$2"
}

check_python

lexer "$1" "$2"