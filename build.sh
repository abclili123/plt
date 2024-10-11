#!/bin/bash

# MacOS / Linux

# need to change this because the arguments
# will end up being the program that needs 
# to be parsed, so will have to do
# something like $args[1] to get the filename

if command -v python3 &>/dev/null; then
    echo "Running Lexer"
    python3 lexer.py
else
    echo "Python3 is not installed"
    echo "installing python..."
    # assuming that they have brew installed, but thats not a given
    if command brew install python3 &>/dev/null; then
        echo "Python3 installed"
        echo "Running Lexer"
        python3 lexer.py
    else
        if command sudo apt install python3 &>/dev/null; then
            echo "Python3 installed"
            echo "Running Lexer"
            python3 lexer.py
        else
            echo "Python3 could not be installed"
        fi
    fi
fi