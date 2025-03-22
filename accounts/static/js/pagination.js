document.addEventListener("DOMContentLoaded", function () {
    let currentPage = 1;
    const rowsPerPage = 10; // Nombre de lignes par page
    const table = document.getElementById("historique-table");
    const tbody = document.getElementById("table-body");
    const rows = Array.from(tbody.getElementsByTagName("tr")); // Convertir en tableau
    const totalPages = Math.ceil(rows.length / rowsPerPage);
    
    function showPage(page) {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;

        // Masquer toutes les lignes
        rows.forEach((row, index) => {
            row.style.display = (index >= start && index < end) ? "" : "none";
        });

        // Mettre à jour l'affichage de la pagination
        document.getElementById("page-info").textContent = `Page ${page} / ${totalPages}`;

        // Désactiver les boutons si nécessaire
        document.getElementById("prev-btn").disabled = (page === 1);
        document.getElementById("next-btn").disabled = (page === totalPages);
    }

    window.prevPage = function () {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
        }
    };

    window.nextPage = function () {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
        }
    };

    // Afficher la première page au chargement
    if (rows.length > 0) {
        showPage(currentPage);
    } else {
        document.getElementById("pagination").style.display = "none"; // Masquer la pagination si aucune donnée
    }
});