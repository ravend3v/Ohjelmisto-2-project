function renderMap(airports, current_airport, access_token_data) {
    const map = L.map('map').setView([current_airport['latitude_deg'], current_airport['longitude_deg']], 7)
    const tile = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.{ext}', {
        minZoom: 4,
        maxZoom: 12,
        attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        ext: 'png',
    });
    const bounds = L.latLngBounds(
        [-85.05112878, -180], 
        [85.05112878, 180] 
    )

    map.setMaxBounds(bounds)
    tile.addTo(map)

    map.zoomControl.setPosition('topright')

    const returnToCurrentLocationButton = L.control({ position: 'topright' })
    returnToCurrentLocationButton.onAdd = (map) => {
        const container = L.DomUtil.create('div', 'leaflet-bar')

        const button = L.DomUtil.create('a', '', container)
        button.href = '#'
        button.title = 'Return to current location'
        button.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i>'

        L.DomEvent.on(button, 'click', (e) => {
            e.preventDefault()
            map.setView([current_airport['latitude_deg'], current_airport['longitude_deg']], 7)
        })

        return container
    }
    returnToCurrentLocationButton.addTo(map)

    const iconData = {
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        shadowSize: [41, 41]
    }

    for (const index in airports) {
        const airport = airports[index]
        const { ident, name, longitude_deg, latitude_deg, cost_of_flight, co2_consumption, flyable } = airport
        
        let iconColor = 'red'
        if (longitude_deg == current_airport['longitude_deg'] && latitude_deg == current_airport['latitude_deg']) {
            iconColor = 'blue'
        }
        const iconUrl = `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-${iconColor}.png`

        const icon = L.icon({ ...iconData, iconUrl })

        const marker = L.marker([latitude_deg, longitude_deg], { icon: icon })
        marker.bindTooltip(name, {
                permament: false,
                direction: 'top'
            })
        marker.addTo(map)

        marker.on('click', async () => {
            if (flyable) {
                let flyTo = confirm(`Do you want to fly to ${name}`)
                if (flyTo) {
                    const req = await fetch(`/api/fly_to/${ident}`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${access_token_data['access_token']}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            'user_Id': access_token_data['user_Id'],
                            cost_of_flight,
                            co2_consumption
                        })
                    })
                    const res = await req.json()
                    console.log(res)
                }
            }
            else {
                alert('Unable to fly to airport')
            }
        })
    }
}
