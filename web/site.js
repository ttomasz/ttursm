function openingHoursReplace(s) {
    return s
        .replace('Mo', 'Pn')
        .replace('Tu', 'Wt')
        .replace('We', 'Śr')
        .replace('Th', 'Czw')
        .replace('Fr', 'Pt')
        .replace('Sa', 'Sb')
        .replace('Su', 'Nd')
        .replace('PH off', 'w święta nieczynne')
        .replace('PH on', 'w święta czynne')
        .replace(',PH', ' i w święta')
        .replace('PH', 'w święta')
        .replace('"only after registration"', 'rezerwacje indywidualne')
        .replaceAll(' off', ' nieczynne')
        .replaceAll('"', '')
    ;
}

function cuisineReplace(s) {
    return s
        .replaceAll(';', ' | ')
        .replaceAll(',', ' | ')
        .replace('asian', 'azjatycka')
        .replace('bakery', 'wypieki')
        .replace('barbecue', 'BBQ')
        .replace('bubble_tea', 'bubble tea')
        // .replace('burger', '')
        .replace('cake', 'ciasta')
        .replace('chicken', 'kurczak')
        .replace('chinese', 'chińska')
        .replace('coffee', 'kawa')
        // .replace('coffee_shop', '')
        .replace('georgian', 'gruzińska')
        // .replace('grill', '')
        .replace('ice_cream', 'lody')
        .replace('indian', 'indyjska')
        .replace('international', 'międzynarodowa')
        .replace('italian', 'włoska')
        .replace('japanese', 'japońska')
        // .replace('kebab', '')
        .replace('middle_eastern', 'bliskowschodnia')
        // .replace('pasta', '')
        // .replace('pizza', '')
        .replace('polish', 'polska')
        .replace('regional', 'regionalna')
        .replace('salad', 'sałatki')
        .replace('steak', 'steki')
        // .replace('sushi', '')
        .replace('thai', 'tajska')
        .replace('turkish', 'turecka')
        .replace('vietnamese', 'wietnamska')
    ;
}

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
        html += '<strong style="font-size: 1.3em;">Parking</strong><br><br>';
        
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
        let emoji = [];
        let html = '<div style="min-width:120px">';
        if (props['@label']) {
            html += `<span class="popup-label kategoria-${props['@kategoria']}">${props['@label']}</span>`;
        } else {
            html += '<br>';
        }
        html += '<hr>';
        if (props.name) {
            html += `<h3 class="popup-place-name">${props.name}</h3>`;
        }
        if (props.opening_hours) {
            let oh = openingHoursReplace(props.opening_hours);
            html += `<strong>Godziny otwarcia</strong>: ${oh}<br>`;
        }
        if (props.cuisine) {
            let oh = cuisineReplace(props.cuisine);
            html += `<strong>Kuchnia</strong>: ${oh}<br>`;
        }
        if (props.toilets) {
            if (props.toilets === 'yes') {
                html += '<strong>Toaleta</strong>: Tak<br>';
                emoji.push("🚾");
            } else if (props.toilets === 'no') {
                html += '<strong>Toaleta</strong>: Nie<br>';
            } else if (props.toilets === 'customers') {
                html += '<strong>Toaleta</strong>: Dla klientów<br>';
                emoji.push("🚾");
            }
        }
        if (props.phone) {
            html += `<strong>Telefon</strong>: ${props['phone']}<br>`;
        }
        if (props.deliveries === 'yes') {
                html += '<strong>Dostawy</strong>: Tak<br>';
            }
        if (props.wheelchair === 'yes') {
            emoji.push("♿️");
        }
        if (props.website) {
            html += `<a href="${props['website']}" target="_blank">Strona WWW</a><br>`;
        }
        if (emoji) {
            let icons = emoji.join([separator = ' | ']);
            html += `${icons}<br>`;
        }
        // for (const key in props) {
        //     html += `<strong>${key}</strong>: ${props[key]}<br>`;
        // }
        html += `<hr><a href="${props['@url']}" target="_blank">Link do obiektu w OSM</a>`;

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