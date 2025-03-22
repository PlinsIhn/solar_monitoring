document.addEventListener("DOMContentLoaded", function () {
    let notificationBtn = document.getElementById("notification-btn");
    let notificationDropdown = document.getElementById("notification-dropdown");
    let notificationList = document.getElementById("notification-list");
    let notificationCount = document.getElementById("notification-count");
    let enableAlertTime = document.getElementById("enable-alert-time"); // Checkbox

    let socket = new WebSocket("ws://localhost:8000/ws/sensor-data/");

    socket.onopen = function () {
        console.log("✅ WebSocket connecté !");
        restoreNotifications(); // Restaurer les notifications sauvegardées
    };

    socket.onerror = function (error) {
        console.error("❌ Erreur WebSocket :", error);
    };

    socket.onclose = function () {
        console.log("⚠️ WebSocket déconnecté !");
    };

    let lastValues = {};
    let storedAlerts = JSON.parse(localStorage.getItem("alerts")) || {}; // Charger les alertes sauvegardées

    const thresholds = {
        temperature_ps: { limit: 40, type: ">", message: "⚠️ Température élevée : ", unit: "°C" },
        tension_ps: { limit: 10, type: "<", message: "⚠️ Tension basse : ", unit: "V" },
        courant_ps: { limit: 0.5, type: "<", message: "⚠️ Courant basse : ", unit: "A" },
        humidite_ps: { limit: 30, type: "<", message: "⚠️ Humidité faible : ", unit: "%" },
        rayon_solaire: { limit: 50, type: "<", message: "⚠️ Faible irradiation solaire : ", unit: "W/m²" },
        tension_batt: { limit: 11, type: "<", message: "⚠️ Batterie faible : ", unit: "V" }
    };

    const activeAlerts = ["temperature_ps", "tension_ps", "courant_ps", "humidite_ps", "rayon_solaire"];
    const alwaysActiveAlerts = ["tension_batt"];

    function isAlertActive(channel) {
        let now = new Date();
        let currentHour = now.getHours();
        let currentMinutes = now.getMinutes();

        if (!enableAlertTime.checked) {
            return true;
        }

        if (alwaysActiveAlerts.includes(channel)) {
            return true;
        }
        
        return (currentHour > 7 || (currentHour === 7 && currentMinutes >= 0)) && 
               (currentHour < 16 || (currentHour === 16 && currentMinutes <= 30));
    }

    function updateNotification() {
        notificationList.innerHTML = "";
        let notifications = {};

        for (let channel in lastValues) {
            if (thresholds[channel] && isAlertActive(channel)) {
                let { limit, type, message, unit } = thresholds[channel];
                let value = lastValues[channel];

                if ((type === ">" && value > limit) || (type === "<" && value < limit)) {
                    notifications[channel] = `${message}${value}${unit} !`;
                }
            }
        }

        localStorage.setItem("alerts", JSON.stringify(notifications)); // Sauvegarder les alertes
        renderNotifications(notifications);
    }

    function renderNotifications(notifications) {
        notificationList.innerHTML = "";
        let count = Object.keys(notifications).length;

        for (let msg of Object.values(notifications)) {
            let newNotification = document.createElement("li");
            newNotification.textContent = msg;
            notificationList.appendChild(newNotification);
        }

        notificationCount.textContent = count;
        notificationCount.style.display = count > 0 ? "inline" : "none";
    }

    function restoreNotifications() {
        let alerts = JSON.parse(localStorage.getItem("alerts")) || {};
        renderNotifications(alerts);
    }

    socket.onmessage = function (event) {
        let data = JSON.parse(event.data);

        if (thresholds.hasOwnProperty(data.channel)) {
            lastValues[data.channel] = data.value;
            updateNotification();
        }
    };

    notificationBtn.addEventListener("click", function () {
        notificationDropdown.style.display = notificationDropdown.style.display === "block" ? "none" : "block";
    });

    enableAlertTime.addEventListener("change", updateNotification);
});
