document.getElementById('compile').addEventListener('click', function() {
    const code = document.getElementById('coding').value;
    
    // Send a POST request to the Flask backend
    fetch('/compile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: code })
    })
    .then(response => response.json())
    .then(data => {
        lexer = data.lexer;
        parser = data.parser;
        generated_code = data.generated_code;

        document.getElementById("lexer-output").innerHTML = lexer;
        document.getElementById("parser-output").innerHTML = parser;
        document.getElementById("code-gen-output").innerHTML = generated_code;
    })
    .catch(error => console.error('Error:', error));
});