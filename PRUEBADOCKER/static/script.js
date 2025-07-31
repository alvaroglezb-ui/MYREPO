function enviarTexto() {
    const texto = document.getElementById('textoInput').value;

    fetch('/procesar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ texto: texto })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('respuesta').innerText = data.respuesta;
    })
    .catch(error => {
        document.getElementById('respuesta').innerText = 'Error: ' + error.message;
        console.error('Fetch error:', error);
    });
}
