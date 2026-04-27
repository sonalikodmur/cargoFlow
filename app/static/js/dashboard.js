let map;
let shipmentMarkers = [];
let alertMarkers = [];
let shipmentsCache = [];
let alertsCache = [];
let shipmentMarkerById = {};
let statusChart;
let riskChart;
let shipmentModal;

function riskClass(level) {
    if (level === "High") return "risk-high";
    if (level === "Medium") return "risk-medium";
    return "risk-low";
}

function alertBadgeClass(type) {
    if (type === "Weather alert") return "text-bg-info";
    if (type === "Delay alert") return "text-bg-warning";
    return "text-bg-danger";
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

async function loadDashboardStats() {
    // Fetch aggregated stats and map them to role-specific cards.
    const response = await fetch("/api/dashboard");
    if (!response.ok) return;
    const data = await response.json();
    setText("total-shipments", data.total_shipments);
    setText("active-shipments", data.active_shipments);
    setText("delayed-shipments", data.delayed_shipments);
    setText("high-risk-alerts", data.high_risk_alerts);
}

async function loadAlerts() {
    // Pull latest alert feed for user/admin side panels.
    const response = await fetch("/alerts");
    if (!response.ok) return;
    const alerts = await response.json();
    alertsCache = alerts;
    setText("alerts-count", alerts.length);

    const container = document.getElementById("alerts-container");
    if (!container) return;
    container.innerHTML = "";

    if (alerts.length === 0) {
        container.innerHTML = '<div class="text-muted">No alerts available.</div>';
        return;
    }

    alerts.forEach((alert) => {
        const row = document.createElement("div");
        row.className = "alert-item d-flex justify-content-between align-items-start gap-2";
        row.innerHTML = `
            <div>
                <div class="fw-semibold">${alert.message}</div>
                <small class="text-muted">${alert.timestamp}</small>
            </div>
            <span class="badge ${alertBadgeClass(alert.alert_type)}">${alert.alert_type}</span>
        `;
        container.appendChild(row);
    });

    drawMapMarkers();
}

function clearMapLayer(markers) {
    markers.forEach((marker) => map.removeLayer(marker));
}

function createCircleMarker(lat, lng, colorHex) {
    return L.circleMarker([lat, lng], {
        radius: 8,
        color: colorHex,
        fillColor: colorHex,
        fillOpacity: 0.85,
        weight: 1,
    }).addTo(map);
}

function drawMapMarkers() {
    // Draw normal shipment (blue) and alert (red) markers in sync.
    if (!map) return;
    clearMapLayer(shipmentMarkers);
    clearMapLayer(alertMarkers);
    shipmentMarkers = [];
    alertMarkers = [];
    shipmentMarkerById = {};

    shipmentsCache.forEach((shipment) => {
        const marker = createCircleMarker(shipment.current_lat, shipment.current_lng, "#2d6cdf");
        marker.bindPopup(`
            <div>
                <strong>Shipment ${shipment.id}</strong><br/>
                ${shipment.source} -> ${shipment.destination}<br/>
                Status: ${shipment.status}<br/>
                Risk: ${shipment.risk_level} (${shipment.risk_percentage}%)
            </div>
        `);
        shipmentMarkers.push(marker);
        shipmentMarkerById[shipment.id] = marker;
    });

    alertsCache.forEach((alert) => {
        const color = alert.risk === "HIGH" ? "#d92d20" : "#2d6cdf";
        const marker = createCircleMarker(alert.lat, alert.lng, color);
        marker.bindPopup(`
            <div>
                <strong>Alert for Shipment ${alert.shipment_id}</strong><br/>
                ${alert.message}<br/>
                Risk: ${alert.risk}<br/>
                Time: ${alert.timestamp}
            </div>
        `);
        alertMarkers.push(marker);
    });
}

function renderUserShipments(shipments) {
    const tbody = document.getElementById("user-shipments-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    shipments.forEach((shipment) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${shipment.id}</td>
            <td>${shipment.source}</td>
            <td>${shipment.destination}</td>
            <td>${shipment.status}</td>
            <td><span class="${riskClass(shipment.risk_level)}">${shipment.risk_level} (${shipment.risk_percentage}%)</span></td>
            <td>${shipment.risk_reason}</td>
            <td><button class="btn btn-sm btn-outline-secondary user-view-btn" data-id="${shipment.id}">View</button></td>
        `;
        tbody.appendChild(row);
    });

    document.querySelectorAll(".user-view-btn").forEach((btn) => {
        btn.addEventListener("click", () => focusShipmentOnMap(Number(btn.dataset.id)));
    });
}

function renderAdminShipments(shipments) {
    const tbody = document.getElementById("admin-shipments-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    shipments.forEach((shipment) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${shipment.id}</td>
            <td>${shipment.source}</td>
            <td>${shipment.destination}</td>
            <td>${shipment.status}</td>
            <td><span class="${riskClass(shipment.risk_level)}">${shipment.risk_level}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-secondary me-1 view-btn" data-id="${shipment.id}">View</button>
                <button class="btn btn-sm btn-outline-primary me-1 edit-btn" data-id="${shipment.id}">Edit</button>
                <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${shipment.id}">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    document.querySelectorAll(".view-btn").forEach((btn) => {
        btn.addEventListener("click", () => focusShipmentOnMap(Number(btn.dataset.id)));
    });
    document.querySelectorAll(".edit-btn").forEach((btn) => {
        btn.addEventListener("click", () => openEditModal(Number(btn.dataset.id)));
    });
    document.querySelectorAll(".delete-btn").forEach((btn) => {
        btn.addEventListener("click", () => deleteShipment(Number(btn.dataset.id)));
    });
}

function focusShipmentOnMap(id) {
    // Center map on selected shipment and show its exact location details.
    const shipment = shipmentsCache.find((item) => item.id === id);
    if (!shipment || !map) return;

    map.setView([shipment.current_lat, shipment.current_lng], 10);
    const marker = shipmentMarkerById[id];
    if (marker) {
        marker.openPopup();
    } else {
        L.popup()
            .setLatLng([shipment.current_lat, shipment.current_lng])
            .setContent(`<strong>Shipment ${shipment.id}</strong><br/>${shipment.location}`)
            .openOn(map);
    }
}

function drawAdminCharts(shipments) {
    // Build pie/bar charts for shipment status and risk distribution.
    const statusCounts = { "On-time": 0, "Delayed": 0, "Risk": 0 };
    const riskCounts = { Low: 0, Medium: 0, High: 0 };
    shipments.forEach((shipment) => {
        statusCounts[shipment.status] = (statusCounts[shipment.status] || 0) + 1;
        riskCounts[shipment.risk_level] = (riskCounts[shipment.risk_level] || 0) + 1;
    });

    if (document.getElementById("status-chart")) {
        if (statusChart) statusChart.destroy();
        statusChart = new Chart(document.getElementById("status-chart"), {
            type: "pie",
            data: {
                labels: Object.keys(statusCounts),
                datasets: [{ data: Object.values(statusCounts), backgroundColor: ["#3a86ff", "#f5c400", "#ef476f"] }],
            },
            options: { plugins: { legend: { position: "bottom" } } },
        });
    }

    if (document.getElementById("risk-chart")) {
        if (riskChart) riskChart.destroy();
        riskChart = new Chart(document.getElementById("risk-chart"), {
            type: "bar",
            data: {
                labels: Object.keys(riskCounts),
                datasets: [{ label: "Shipments", data: Object.values(riskCounts), backgroundColor: ["#22c55e", "#f59e0b", "#dc2626"] }],
            },
            options: { scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }, plugins: { legend: { display: false } } },
        });
    }
}

async function fetchShipments() {
    const response = await fetch("/shipments");
    if (!response.ok) return;
    const shipments = await response.json();
    shipmentsCache = shipments;

    if (CURRENT_USER_ROLE === "admin") {
        renderAdminShipments(shipments);
        drawAdminCharts(shipments);
    } else {
        renderUserShipments(shipments);
    }

    drawMapMarkers();
}

function initMap() {
    const mapElement = document.getElementById("map");
    if (!mapElement) return;
    map = L.map("map").setView([20.5937, 78.9629], 5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);
}

function openAddModal() {
    document.getElementById("shipment-modal-title").textContent = "Add Shipment";
    document.getElementById("shipment-form").reset();
    document.getElementById("shipment-id").value = "";
    shipmentModal.show();
}

function openEditModal(id) {
    const shipment = shipmentsCache.find((item) => item.id === id);
    if (!shipment) return;
    document.getElementById("shipment-modal-title").textContent = `Edit Shipment #${id}`;
    document.getElementById("shipment-id").value = shipment.id;
    document.getElementById("source").value = shipment.source;
    document.getElementById("destination").value = shipment.destination;
    document.getElementById("location").value = shipment.location;
    document.getElementById("current-lat").value = shipment.current_lat;
    document.getElementById("current-lng").value = shipment.current_lng;
    document.getElementById("destination-lat").value = shipment.destination_lat;
    document.getElementById("destination-lng").value = shipment.destination_lng;
    document.getElementById("weather-condition").value = shipment.weather_condition;
    document.getElementById("traffic-level").value = shipment.traffic_level;
    document.getElementById("eta-delay").value = shipment.eta_delay_minutes;
    shipmentModal.show();
}

async function saveShipment(event) {
    event.preventDefault();
    const shipmentId = document.getElementById("shipment-id").value;
    const payload = {
        source: document.getElementById("source").value,
        destination: document.getElementById("destination").value,
        location: document.getElementById("location").value,
        current_lat: Number(document.getElementById("current-lat").value),
        current_lng: Number(document.getElementById("current-lng").value),
        destination_lat: Number(document.getElementById("destination-lat").value || document.getElementById("current-lat").value),
        destination_lng: Number(document.getElementById("destination-lng").value || document.getElementById("current-lng").value),
        weather_condition: document.getElementById("weather-condition").value,
        traffic_level: document.getElementById("traffic-level").value,
        eta_delay_minutes: Number(document.getElementById("eta-delay").value || 0),
    };

    const method = shipmentId ? "PUT" : "POST";
    const url = shipmentId ? `/api/shipments/${shipmentId}` : "/api/shipments";
    const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (response.ok) {
        shipmentModal.hide();
        await fetchShipments();
        await loadDashboardStats();
    } else {
        alert("Unable to save shipment. Ensure you are logged in as admin.");
    }
}

async function deleteShipment(id) {
    if (!confirm(`Delete shipment #${id}?`)) return;
    const response = await fetch(`/api/shipments/${id}`, { method: "DELETE" });
    if (response.ok) {
        await fetchShipments();
        await loadDashboardStats();
    } else {
        alert("Unable to delete shipment.");
    }
}

function bindAdminActions() {
    const modalElement = document.getElementById("shipmentModal");
    if (!modalElement) return;
    shipmentModal = new bootstrap.Modal(modalElement);
    document.getElementById("shipment-form").addEventListener("submit", saveShipment);

    const openBtn = document.getElementById("open-add-modal-btn");
    const inlineBtn = document.getElementById("open-add-modal-btn-inline");
    if (openBtn) openBtn.addEventListener("click", openAddModal);
    if (inlineBtn) inlineBtn.addEventListener("click", openAddModal);
}

async function initializeDashboard() {
    initMap();
    if (CURRENT_USER_ROLE === "admin") {
        bindAdminActions();
    }

    await loadDashboardStats();
    await loadAlerts();
    await fetchShipments();

    setInterval(loadDashboardStats, 15000);
    setInterval(loadAlerts, 10000);
    setInterval(fetchShipments, 20000);
}

initializeDashboard();
