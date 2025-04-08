const graphsContainer = document.getElementById('graphs-container');

// Fonction pour restaurer les graphiques à partir de localStorage
function restoreGraphs() {
    const savedGraphIds = JSON.parse(localStorage.getItem('openedGraphs')) || [];
    savedGraphIds.forEach(channelId => {
        const button = document.querySelector(`.widget-btn[data-channel-id='${channelId}']`);
        if (button) {
            fetch(`/channel-data/${channelId}/`)  // Charger les données depuis Django
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error("Erreur de récupération :", data.error);
                        return;
                    }

                    localStorage.setItem(`channel-${channelId}-data`, JSON.stringify({ labels: data.labels, values: data.values }));
                    createSeparationGraphe(channelId, button.getAttribute('data-channel-name'), data.labels, data.values);
                })
                .catch(error => console.error("Erreur chargement des données :", error));
        }
    });
}

// Connexion WebSocket
const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${wsScheme}://${window.location.host}/ws/sensor-data/`);

socket.onopen = function (event) {
    console.log("✅ WebSocket connecté avec succès !");
};

socket.onmessage = function(event) {
    let data = JSON.parse(event.data);

    let channelId = data.channel || data.channel_name;  // Prendre `channel_name` si `channel` est manquant
    let channelName = data.channel_name || data.channel;  // Prendre `channel` si `channel_name` est manquant
    let value = data.value;
    let timestamp = data.timestamp;

    let storedData = JSON.parse(localStorage.getItem(`channel-${channelId}-data`)) || { labels: [], values: [] };

    // Ajouter la nouvelle valeur
    storedData.labels.push(timestamp);
    storedData.values.push(value);

    // Garder seulement les 10 dernières valeurs pour éviter l’accumulation
    if (storedData.labels.length > 30) {
        storedData.labels.shift();
        storedData.values.shift();
    }

    // Mettre à jour le localStorage
    localStorage.setItem(`channel-${channelId}-data`, JSON.stringify(storedData));

    // Mettre à jour le graphique
    let chart = Chart.getChart(`chart-${channelId}`);
    if (chart) {
        chart.data.labels = storedData.labels;
        chart.data.datasets[0].data = storedData.values;
        chart.update();
    }
};

// Gérer les erreurs WebSocket
socket.onerror = function (error) {
    console.error("❌ Erreur WebSocket :", error);
};

// Gérer la fermeture de la connexion WebSocket
socket.onclose = function (event) {
    console.log("🔴 WebSocket déconnecté.");
};

// Enregistre les graphiques ouverts dans le localStorage
function saveOpenedGraphs() {
    const openedGraphs = [];
    document.querySelectorAll('.graph-container').forEach(graph => {
        openedGraphs.push(graph.getAttribute('data-channel-id'));
    });
    localStorage.setItem('openedGraphs', JSON.stringify(openedGraphs));
}

// Fonction pour convertir une date UTC en heure Madagascar (UTC+3)
function convertToMadagascarTime(dateString) {
    const date = new Date(dateString); // Convertir la chaîne de date en objet Date
    date.setHours(date.getHours() + 3); // Ajouter 3 heures pour UTC+3
    return date;
}

// Fonction pour formater une date en chaîne lisible
function formatDate(date) {
    return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Fonction pour créer un graphique individuel
function createSeparationGraphe(channelId, channelName, labels, values) {
    if (document.querySelector(`#graph-${channelId}`)) {
        alert('Le graphique pour ce canal est déjà affiché.');
        return;
    }

    const graphContainer = document.createElement('div');
    graphContainer.id = `graph-${channelId}`;
    graphContainer.classList.add('graph-container');
    graphContainer.setAttribute('data-channel-id', channelId);
    graphContainer.style.width = '450px';
    graphContainer.style.minWidth = '300px';
    graphContainer.style.minHeight = '250px';
    graphContainer.style.border = '1px solid #ccc';
    graphContainer.style.padding = '10px';
    graphContainer.style.position = 'relative';
    graphContainer.style.resize = 'both';
    graphContainer.style.overflow = 'auto';
    graphContainer.style.marginBottom = '20px';

    const title = document.createElement('h3');
    title.textContent = `${channelName}`;
    title.style.margin = '0';
    title.style.textAlign = 'center';
    graphContainer.appendChild(title);

    // Bouton de fermeture
    const closeButton = document.createElement('button');
    closeButton.innerHTML = 'x'; // Icône de fermeture
    closeButton.style.position = 'absolute';
    closeButton.style.top = '5px';
    closeButton.style.right = '5px';
    closeButton.style.border = 'none';
    closeButton.style.background = 'transparent';
    closeButton.style.cursor = 'pointer';
    closeButton.style.fontSize = '18px';
    closeButton.style.color = 'red';
    closeButton.addEventListener('click', () => {
        graphContainer.remove();
        saveOpenedGraphs();
    });
    graphContainer.appendChild(closeButton);

    // Bouton de téléchargement avec icône
    const downloadButton = document.createElement('button');
    downloadButton.innerHTML = '📥'; // Icône de téléchargement
    downloadButton.style.position = 'absolute';
    downloadButton.style.bottom = '5px';
    downloadButton.style.left = '5px';
    downloadButton.style.border = 'none';
    downloadButton.style.background = 'transparent';
    downloadButton.style.cursor = 'pointer';
    downloadButton.style.fontSize = '18px';
    downloadButton.addEventListener('click', () => {
        const canvas = document.getElementById(`chart-${channelId}`);
        const image = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = image;
        link.download = `graphique_${channelName}.png`;
        link.click();
    });
    graphContainer.appendChild(downloadButton);

    const canvas = document.createElement('canvas');
    canvas.id = `chart-${channelId}`;
    graphContainer.appendChild(canvas);

    graphsContainer.appendChild(graphContainer);

    const ctx = canvas.getContext('2d');

    // Convertir les labels UTC en heure Madagascar (UTC+3)
    const madagascarLabels = labels.map(label => {
        const madagascarTime = convertToMadagascarTime(label);
        return formatDate(madagascarTime); // Formater la date en chaîne lisible
    });

    // Définir une hauteur pour le canvas (optionnel)
    canvas.style.height = "350px"; 
    canvas.style.width = "100%";

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: madagascarLabels,
            datasets: [{
                label: `Données du channel : ${channelName}`,
                data: values,
                borderColor: 'rgba(75, 192, 192, 0.8)',
                backgroundColor: 'rgba(42, 190, 190, 0.2)', 
                fill: true,
                tension: 0.3, // Rend la ligne plus douce
            }]
        },
        options: {
            animation: {
                duration: 1500,  // Temps d'animation total
                easing: 'easeOutBounce', // Effet de rebond léger
                mode: 'default'
            },
            maintainAspectRatio: true,
            scales: {
                x: {
                    title: { display: true, text: 'Temps' },
                    animation: { duration: 1000, easing: 'easeInOutQuart' } // Transition douce pour l'axe X
                },
                y: {
                    title: { display: true, text: 'Valeurs' },
                    min: Math.min(...values) - (Math.max(...values) - Math.min(...values)) * 0.1,
                    max: Math.max(...values) + (Math.max(...values) - Math.min(...values)) * 0.1,
                    ticks: {
                        stepSize: 2, // Pas de 2 sur l'axe Y
                        autoSkip: true,  // Évite l'affichage excessif de labels
                        maxTicksLimit: 10 // Limite le nombre de valeurs affichées
                    }
                }
            }
        }
    });

    saveOpenedGraphs();
}

// Écouteur pour les boutons
document.querySelectorAll('.widget-btn').forEach(button => {
    button.addEventListener('click', () => {
        const channelId = button.getAttribute('data-channel-id');
        const channelName = button.getAttribute('data-channel-name');

        fetch(`/channel-data/${channelId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                localStorage.setItem(`channel-${channelId}-data`, JSON.stringify({ labels: data.labels, values: data.values }));
                createSeparationGraphe(channelId, channelName, data.labels, data.values);
            });
    });
});

// Restaurer les graphiques ouverts au chargement de la page
restoreGraphs();

// Fonction pour convertir une date UTC en heure Madagascar (UTC+3)
function convertToMadagascarTime(dateString) {
    const date = new Date(dateString); // Convertir la chaîne de date en objet Date
    date.setHours(date.getHours() + 3); // Ajouter 3 heures pour UTC+3
    return date;
}

// Fonction pour formater une date en chaîne lisible
function formatDate(date) {
    return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Fonction pour mettre à jour le graphique filtré
function updateCombinedChart(labels, values, channelName, startDate, endDate) {
    const filteredChartContainer = document.getElementById('filtered-chart-container');
    const filteredChartCanvas = document.getElementById('filtered-chart');
    const filteredChannelName = document.getElementById('filtered-channel-name');
    const filteredDateRangeValue = document.getElementById('filtered-date-range-value');

    // Mettre à jour le titre du graphique filtré
    filteredChannelName.textContent = channelName;
    filteredDateRangeValue.textContent = `${startDate} à ${endDate}`;

    // Afficher le conteneur du graphique filtré
    filteredChartContainer.style.display = 'block';

    const ctx = filteredChartCanvas.getContext('2d');

    // Convertir les labels UTC en heure Madagascar (UTC+3)
    const madagascarLabels = labels.map(label => {
        const madagascarTime = convertToMadagascarTime(label);
        return formatDate(madagascarTime); // Formater la date en chaîne lisible
    });

    if (window.filteredChart) {
        // Mettre à jour les données du graphique existant
        window.filteredChart.data.labels = madagascarLabels;
        window.filteredChart.data.datasets[0].data = values;
        window.filteredChart.update();
    } else {
        // Créer un nouveau graphique avec les options personnalisées
        window.filteredChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: madagascarLabels,
                datasets: [{
                    label: '', // Supprimer le label du dataset
                    data: values,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)', 
                    fill: true,
                    tension: 0.3 // Rend la ligne plus douce
                }]
            },
            options: {
                animation: {
                    duration: 1500,  // Temps d'animation total
                    easing: 'easeOutBounce', // Effet de rebond léger
                    mode: 'default'
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Temps' },
                        animation: { duration: 1000, easing: 'easeInOutQuart' } // Transition douce pour l'axe X
                    },
                    y: {
                        title: { display: true, text: 'Valeurs' },
                        min: Math.min(...values) - (Math.max(...values) - Math.min(...values)) * 0.1,
                        max: Math.max(...values) + (Math.max(...values) - Math.min(...values)) * 0.1
                    }
                },
                plugins: {
                    legend: {
                        display: false // Masquer complètement la légende
                    }
                }
            }
        });
    }
}

// Écouteur pour le formulaire de filtrage
document.getElementById('filter-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Empêche le rechargement de la page

    const channelId = document.getElementById('channel').value;
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;

    // Récupérer le nom du canal sélectionné
    const channelName = document.querySelector(`#channel option[value='${channelId}']`).textContent;

    // Envoyer une requête AJAX pour récupérer les données filtrées
    fetch(`/channel-data/${channelId}/?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            updateCombinedChart(data.labels, data.values, channelName, startDate, endDate);
        })
        .catch(error => console.error('Erreur :', error));
});

// Écouteur pour le bouton de fermeture du graphique filtré
document.getElementById('close-filtered-chart').addEventListener('click', function () {
    const filteredChartContainer = document.getElementById('filtered-chart-container');
    const filteredChartCanvas = document.getElementById('filtered-chart');

    // Masquer le conteneur du graphique filtré
    filteredChartContainer.style.display = 'none';

    // Réinitialiser le graphique filtré
    if (window.filteredChart) {
        window.filteredChart.destroy(); // Détruire l'instance du graphique
        window.filteredChart = null; // Réinitialiser la variable
    }

    // Effacer le canvas
    const ctx = filteredChartCanvas.getContext('2d');
    ctx.clearRect(0, 0, filteredChartCanvas.width, filteredChartCanvas.height);
});

// Écouteur pour le bouton de téléchargement du graphique filtré
document.getElementById('download-filtered-chart').addEventListener('click', function () {
    const filteredChartCanvas = document.getElementById('filtered-chart');
    const channelName = document.querySelector('#channel option:checked').textContent;

    // Exporter le graphique en image
    const image = filteredChartCanvas.toDataURL('image/png');
    const link = document.createElement('a');
    link.href = image;
    link.download = `graphique_${channelName}.png`;
    link.click();
});