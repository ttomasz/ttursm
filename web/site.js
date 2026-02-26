const map = new maplibregl.Map({
    container: "map",
    style: "https://ttomasz.github.io/ttursm/styles/map_style.json",
    dragRotate: false,
    hash: "map",
    maplibreLogo: true,
    minZoom: 12,
    maxZoom: 20,
    center: [20.8828989, 52.1960985],
    zoom: 15,
});
map.addControl(new maplibregl.NavigationControl(), "top-right");

// Add click event for layers: parking_fill, shops_and_food_symbols, shops_and_food_clusters
map.on('load', function() {
['parking_fill', 'shops_and_food_symbols'].forEach(layer => {
    map.on('click', layer, function(e) {
    if (!e.features || !e.features.length) return;
    const feature = e.features[0];
    const props = feature.properties;
    let html = '<div style="min-width:120px">';
    for (const key in props) {
        html += `<strong>${key}</strong>: ${props[key]}<br>`;
    }
    html += '</div>';
    new maplibregl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(html)
        .addTo(map);
    });
    // Change cursor to pointer
    map.on('mouseenter', layer, function() {
    map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', layer, function() {
    map.getCanvas().style.cursor = '';
    });
});
// zoom when clicking cluster
map.on('click', 'shops_and_food_clusters', function(e) {
    let features = map.queryRenderedFeatures(e.point, {
        layers: ['shops_and_food_clusters']
    });
    map
    .getSource('shops_and_food_points')
    .getClusterExpansionZoom(features[0].properties.cluster_id)
    .then(zoom => {
    map.easeTo({
        center: features[0].geometry.coordinates,
        zoom: zoom
    });
    });
});
// Change cursor to pointer
map.on('mouseenter', 'shops_and_food_clusters', function() {
    map.getCanvas().style.cursor = 'pointer';
});
map.on('mouseleave', 'shops_and_food_clusters', function() {
    map.getCanvas().style.cursor = '';
});
});

// load summary
fetch("https://ttomasz.github.io/ttursm/data/summary.json")
.then(response => response.json())
.then(data => {
    document.getElementById("count-med").textContent = `(${data.med})`;
    document.getElementById("count-food").textContent = `(${data.food})`;
    document.getElementById("count-shops").textContent = `(${data.shops})`;
    document.getElementById("count-services").textContent = `(${data.services})`;
    document.getElementById("count-vacant").textContent = `(${data.vacant})`;
    document.getElementById("data-date").textContent = data.download_dt;
    for (let [key, value] of Object.entries(data.poi_subcategories)) {
        let doc = document.getElementById(`subcount-${key}`);
        if (doc !== null) {
            doc.textContent = `(${value})`;
        }
    }
})
.catch(error => {
console.error("Error loading summary data:", error);
document.getElementById("data-date").textContent = "Błąd ładowania danych";
});