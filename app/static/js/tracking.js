let map;
let shipmentMarkers = [];
let alertMarkers = [];
let shipmentsCache = [];
let alertsCache = [];

function riskClass(level) {
    // CSS class mapping for risk labels in table.
    if (level === "High") return "risk-high";
    if (level === "Medium") return "risk-medium";
    return "risk-low";
}

function clearMarkers() {
    // Remove previous marker references before redraw.
    shipmentMarkers.forEach((marker) => map.removeLayer(marker));
    alertMarkers.forEach((marker) => map.removeLayer(marker));
    shipmentMarkers = [];
    alertMarkers = [];
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

function drawShipmentsOnMap() {
    // Plot normal shipments and alert points together.
    clearMarkers();
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

function renderRouteDetails(shipment) {
    // Show current route vs optimized route for selected shipment.
    const container = document.getElementById("route-details");
    container.innerHTML = `
        <p><strong>Shipment:</strong> ${shipment.id}</p>
        <p><strong>Current route:</strong><br/>${shipment.current_route}</p>
        <p><strong>Optimized route:</strong><br/>${shipment.optimized_route}</p>
        <p><strong>Recommendation:</strong> ${shipment.route_note}</p>
    `;
}

function renderShipmentsTable(shipments) {
    // Render shipment data and attach row-level action handlers.
    const tbody = document.getElementById("shipments-body");
    tbody.innerHTML = "";

    shipments.forEach((shipment) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${shipment.id}</td>
            <td>${shipment.source}</td>
            <td>${shipment.destination}</td>
            <td>${shipment.status}</td>
            <td>
                <span class="${riskClass(shipment.risk_level)}">
                    ${shipment.risk_level} (${shipment.risk_percentage}%)
                </span>
            </td>
            <td>${shipment.risk_reason}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" data-shipment-id="${shipment.id}">
                    View Route
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    document.querySelectorAll("[data-shipment-id]").forEach((button) => {
        button.addEventListener("click", (event) => {
            const selectedId = Number(event.target.getAttribute("data-shipment-id"));
            const selectedShipment = shipmentsCache.find((item) => item.id === selectedId);
            if (selectedShipment) {
                renderRouteDetails(selectedShipment);
                map.setView([selectedShipment.current_lat, selectedShipment.current_lng], 8);
            }
        });
    });
}

async function fetchShipments() {
    // Load latest shipment telemetry from backend.
    const response = await fetch("/shipments");
    if (!response.ok) return;

    const shipments = await response.json();
    shipmentsCache = shipments;
    renderShipmentsTable(shipments);
    drawShipmentsOnMap();
}

async function fetchAlerts() {
    // Load alert coordinates for red risk markers.
    const response = await fetch("/alerts");
    if (!response.ok) return;
    alertsCache = await response.json();
    drawShipmentsOnMap();
}

function initMap() {
    // Initialize Leaflet map with OpenStreetMap tiles.
    map = L.map("map").setView([20.5937, 78.9629], 5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    fetchShipments();
    fetchAlerts();
    setInterval(fetchShipments, 20000);
    setInterval(fetchAlerts, 10000);
}

// Start map immediately because Leaflet is loaded before this script.
initMap();
