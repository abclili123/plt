from flask import Flask, jsonify, request, render_template
import logging

from src import lexer
from src.parser import Parser

app = Flask(__name__)

# open index.html
@app.route("/") # this is what comes after the localhost url.. we jsut have one page
def index():
    return render_template("index.html")

# when compile is hit in browser
@app.route('/compile', methods=['POST'])
def compile():
    # get code from text editor
    data = request.get_json()
    code = data.get('code')

    # dump code into a file for lexer
    # we can just convert lexer to read the string later
    # create file path for code
    source_file = 'code.prog'
    with open(source_file, 'w') as file:
        file.write(code)

    # create file path for lexer output
    lexer_output_file = 'lexer_output.txt'

    # lex code
    # i know there is a better way to do this but for now we'll just read the file
    lexer_output = lexer.lexer('code.prog', lexer_output_file)
    with open(lexer_output_file, 'r') as file:
        lexer_output_data = file.read()

    # create file path for parser output
    parser_output_file = 'parser_output.txt'

    # parse lexer output
    # touch parser output file
    parser = Parser(lexer_output, parser_output_file)
    parser.parse_program()
    parser.print_ast_tree()
    with open(parser_output_file, 'r') as file:
        parser_output = file.read()

    # code generation 
    code_generation = 'code generation'

    # Send the explanation back as JSON
    return jsonify({
        'lexer': lexer_output_data,
        'parser': parser_output,
        'generated_code': code_generation
    })

# to run the app do python app.py then open the localhost url in chrome
if __name__ == "__main__":
    app.run(debug=True)
