function copyToClipboard() {
    // Récupérer la valeur de l'API key
    const apiKeyElement = document.getElementById('apiKey');
    const apiKey = apiKeyElement.textContent;

    // Copier dans le presse-papiers
    navigator.clipboard.writeText(apiKey).then(() => {
        // Confirmation à l'utilisateur
        alert("Clé API copiée dans le presse-papiers !");
    }).catch(err => {
        console.error("Erreur lors de la copie : ", err);
        alert("Impossible de copier la clé API. Veuillez réessayer.");
    });
}