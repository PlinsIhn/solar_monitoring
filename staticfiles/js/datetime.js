function updateDatetime() {
    const now = new Date();
    const formattedDate = now.toLocaleString('fr-FR', {
        weekday: 'long', // jour de la semaine (ex. lundi)
        year: 'numeric',
        month: 'long',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false, // pour l'heure en format 24h
    });
    document.getElementById('current-datetime').textContent = `${formattedDate}`;
}

// Mettre à jour toutes les secondes
setInterval(updateDatetime, 1000);
updateDatetime(); // Initialisation de la première date