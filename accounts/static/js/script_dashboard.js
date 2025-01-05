const graphsContainer = document.getElementById('graphs-container');

    // Fonction pour restaurer les graphiques à partir de localStorage
    function restoreGraphs() {
        const savedGraphIds = JSON.parse(localStorage.getItem('openedGraphs')) || [];
        savedGraphIds.forEach(channelId => {
            const button = document.querySelector(`.widget-btn[data-channel-id='${channelId}']`);
            if (button) {
                const savedData = JSON.parse(localStorage.getItem(`channel-${channelId}-data`));
                if (savedData) {
                    createSeparationGraphe(channelId, button.getAttribute('data-channel-name'), savedData.labels, savedData.values);
                } else {
                    button.click(); // Si aucune donnée sauvegardée, refetch
                }
            }
        });
    }

    // Enregistre les graphiques ouverts dans le localStorage
    function saveOpenedGraphs() {
        const openedGraphs = [];
        document.querySelectorAll('.graph-container').forEach(graph => {
            openedGraphs.push(graph.getAttribute('data-channel-id'));
        });
        localStorage.setItem('openedGraphs', JSON.stringify(openedGraphs));
    }

    // Fonction pour créer un graphique
    function createSeparationGraphe(channelId, channelName, labels, values) {
        if (document.querySelector(`#graph-${channelId}`)) {
            alert('Le graphique pour ce canal est déjà affiché.');
            return;
        }

        const graphContainer = document.createElement('div');
        graphContainer.id = `graph-${channelId}`;
        graphContainer.classList.add('graph-container');
        graphContainer.setAttribute('data-channel-id', channelId);
        graphContainer.style.width = '500px';
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

        const closeButton = document.createElement('button');
        closeButton.textContent = 'Fermer';
        closeButton.style.position = 'absolute';
        closeButton.style.top = '5px';
        closeButton.style.right = '5px';
        closeButton.addEventListener('click', () => {
            graphContainer.remove();
            saveOpenedGraphs();
        });
        graphContainer.appendChild(closeButton);

        const canvas = document.createElement('canvas');
        canvas.id = `chart-${channelId}`;
        graphContainer.appendChild(canvas);

        graphsContainer.appendChild(graphContainer);

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Données du channel : ${channelName}`,
                    data: values,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                }]
            },
            options: {
                scales: {
                    x: { title: { display: true, text: 'Temps' } },
                    y: {
                        title: { display: true, text: 'Valeurs' },
                        min: Math.min(...values) - (Math.max(...values) - Math.min(...values)) * 0.1,
                        max: Math.max(...values) + (Math.max(...values) - Math.min(...values)) * 0.1,
                    }
                }
            }
        });

        saveOpenedGraphs();
    }

    // graphe combiné

    

    // ecouteur graphe combine
    



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