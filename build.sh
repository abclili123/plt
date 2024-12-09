#!/bin/bash

# MacOS / Linux

check_python(){
    if ! command -v python3 &>/dev/null; then
        echo "Python3 was not found. Please install python3 to run the server"
        exit 1
    fi
}
check_flask(){
    if ! command -v flask &>/dev/null; then
        echo "Flask was not found. Please install flask to run the server"
        exit 1
    fi
}

# dont need this anymore?
# lexer() {
#     if [ -z "$1" ] || [ -z "$2" ] [ -z "$3" ]; then
#         echo "Usage: $0 <input_filename> <lexer_output_filename> <parser_output_filename>"
#         exit 1
#     fi

#     python3 lexer.py "$1" "$2" "$3"
# }

check_python
check_flask

python3.11 app.py

# lexer "$1" "$2" "$3"