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
        // Output lexer, parser, and generated code in respective divs
        document.getElementById("lexer-output").innerHTML = data.lexer;
        document.getElementById("parser-output").innerHTML = data.parser;
        document.getElementById("code-gen-output").innerHTML = data.generated_code;

        // Check if an iframe with the ID 'generated-iframe' exists, and remove it if it does
        const existingIframe = document.getElementById('generated-iframe');
        if (existingIframe) {
            existingIframe.remove(); // Remove the old iframe
        }

        // Create a new iframe element
        const iframe = document.createElement('iframe');
        iframe.id = 'generated-iframe';  // Give it a unique ID
        iframe.style.display = 'none';

        // Append the new iframe to the body or any container
        document.body.appendChild(iframe);

        // Get the iframe's document object
        const iframeDoc = iframe.contentWindow.document;

        // Open the iframe document and inject the generated code
        iframeDoc.open();
        iframeDoc.write(`
            <html>
            <head>
                <title>Generated Code Execution</title>
            </head>
            <body>
                <script>
                    (function() {
                        // Wrap the generated code in an IIFE to prevent variable conflicts
                        ${data.generated_code}
                        // Ensure play() is called when the code inside the iframe is loaded
                        window.onload = function() {
                            if (typeof play === 'function') {
                                play(); // Call play() function inside the iframe
                            }
                        };
                    })();
                </script>
            </body>
            </html>
        `);
        iframeDoc.close();

        // Optionally: Add iframe load listener (if you need more control)
        iframe.onload = function() {
            console.log("Iframe loaded, play() function should have been called.");
        };
    })
    .catch(error => console.error('Error:', error));
});
