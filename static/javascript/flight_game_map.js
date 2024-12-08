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
        const { ident, name, longitude_deg, latitude_deg, continent, cost_of_flight, co2_consumption, flyable } = airport
        
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

        marker.on('click', () => {
            let confirmFlightPopup = document.getElementById('confirm-flight-popup')
            let confirmFlightTitle = document.getElementById('confirm-flight-title')

            let trivia = document.getElementById('trivia')

            if (flyable) {
                confirmFlightPopup.style.display = 'flex'
                confirmFlightTitle.innerHTML = `Do you want to fly to ${name}`

                document.getElementById('deny-flight').onclick = () => {
                    confirmFlightPopup.style.display = 'none'
                }
                document.getElementById('confirm-flight').onclick = () => {
                    confirmFlightPopup.style.display = 'none'
                    trivia.style.display = 'flex'

                    /* INSERT TRIVIA API REQUEST HERE */

                    document.getElementById('trivia-form').onsubmit = async (e) => {
                        e.preventDefault()

                        const checkedOption = document.querySelector('.trivia-checkbox:checked')
                        
                        const updateLocationRequest = await fetch(`/api/fly_to/${ident}`, {
                            method: 'POST',
                            headers: {
                                'Authorization': `Bearer ${access_token_data['access_token']}`,
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                'user_Id': access_token_data['user_Id'],
                                'winnings': Math.random() * (cost_of_flight * 2 - cost_of_flight * 0.5) + cost_of_flight * 0.5,
                                continent,
                                cost_of_flight,
                                co2_consumption
                            })
                        })
                        const updateLocationResponse = await updateLocationRequest.json()
                        if (!updateLocationResponse['error']) {
                            location.reload()
                        } else {
                            alert(updateLocationResponse['message'])
                        }
                    }
                }
            }
            else {
                alert('Unable to fly to airport')
            }
        })
    }
}

function HandleCheckBoxClick(clickedCheckBox) {
    const checkBoxes = document.querySelectorAll('.trivia-checkbox')
    checkBoxes.forEach(checkBox => {
        if (checkBox !== clickedCheckBox) { checkBox.checked = false }
    })
}
