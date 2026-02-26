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

map.on('load', function () {

    // click feature to get popup with info
    map.on('click', 'parking_fill', function (e) {
        if (!e.features || !e.features.length) return;
        const feature = e.features[0];
        const props = feature.properties;
        let html = '<div style="min-width:120px">';
        html += '<strong>Parking</strong><br>';
        
        if (props.access) {
            const accessMap = {
                'yes': 'Publiczny',
                'permissive': 'Publiczny',
                'customers': 'Dla klientów',
                'private': 'Prywatny (np. mieszkańców, pracowników)'
            };
            const accessValue = accessMap[props.access] || props.access;
            html += `<strong>Rodzaj</strong>: ${accessValue}<br>`;
        } else {
            html += '<strong>Rodzaj</strong>: <i>brak danych</i><br>';
        }
        
        if (props.fee === 'yes') {
            html += '<strong>Płatny</strong>: Tak<br>';
            if (props.charge) {
                let oplata = props.charge.replace('hour', 'h');
                html += `<strong>Opłata</strong>: ${oplata}<br>`;
            }
        } else if (props.fee === 'no') {
            html += '<strong>Płatny</strong>: Nie<br>';
        } else {
            html += '<strong>Płatny</strong>: <i>brak danych</i><br>';
        }
        
        if (props.capacity) {
            html += `<strong>Liczba miejsc</strong>: ${props.capacity}<br>`;
        } else {
            html += `<strong>Liczba miejsc</strong>: <i>brak danych</i><br>`;
        }
        
        if (props['capacity:disabled']) {
            html += `<strong>Liczba miejsc dla niepełnosprawnych</strong>: ${props['capacity:disabled']}<br>`;
        }

        html += `<a href="${props['@url']}" target="_blank">Link do obiektu w OSM</a>`;

        // html += '<hr>'
        // html += '<div class="popup-section-foldable">';
        // for (const key in props) {
        //     html += `<strong>${key}</strong>: ${props[key]}<br>`;
        // }
        // html += '</div>';
        html += '</div>';
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(html)
            .addTo(map);
    });
    map.on('click', 'shops_and_food_symbols', function (e) {
        if (!e.features || !e.features.length) return;
        const feature = e.features[0];
        const props = feature.properties;
        let html = '<div style="min-width:120px">';
        html += '<hr>';
        for (const key in props) {
            html += `<strong>${key}</strong>: ${props[key]}<br>`;
        }
        html += '</div>';
        new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(html)
            .addTo(map);
    });

    // zoom when clicking cluster
    map.on('click', 'shops_and_food_clusters', function (e) {
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

    // Change cursor to pointer when hovering over object
    map.on('mouseenter', 'shops_and_food_symbols', function () {
        map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'shops_and_food_symbols', function () {
        map.getCanvas().style.cursor = '';
    });
    map.on('mouseenter', 'parking_fill', function () {
        map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'parking_fill', function () {
        map.getCanvas().style.cursor = '';
    });
    map.on('mouseenter', 'shops_and_food_clusters', function () {
        map.getCanvas().style.cursor = 'pointer';
    });
    map.on('mouseleave', 'shops_and_food_clusters', function () {
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