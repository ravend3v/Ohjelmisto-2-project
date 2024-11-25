function renderMap(airports) {
    let currentLocation = airports[0]

    const map = L.map('map').setView([currentLocation['latitude_deg'], currentLocation['longitude_deg']], 7)
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
            map.setView([currentLocation['latitude_deg'], currentLocation['longitude_deg']], 7)
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
        const { ident, name, longitude_deg, latitude_deg } = airport
        
        let iconColor = 'red'
        if (longitude_deg == currentLocation['longitude_deg'] && latitude_deg == currentLocation['latitude_deg']) {
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

        marker.on('click', () => {
            let flyTo = confirm(`Do you want to fly to ${name}`)
            if (flyTo) alert('yay')
            else alert('aaawww man :(')
        })
    }
}
