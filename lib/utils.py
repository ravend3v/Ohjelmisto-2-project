import geopy.distance

def get_flyable_airports(current_airport, all_airports):
    flyable_airports = []

    current_lat = current_airport[2]
    current_lon = current_airport[3]
    player_money = current_airport[5]

    for airport in all_airports:
        distance_to_airport = geopy.distance.geodesic(
            (current_lat, current_lon), (airport[2], airport[3])
        ).km

        if distance_to_airport > 0:
            cost_of_flight = int(distance_to_airport * 0.5)
            co2_consumption = int(distance_to_airport * 0.2)

            if player_money >= cost_of_flight:
                flyable_airports.append({
                    'ident': airport[0],
                    'name': airport[1],
                    'latitude_deg': airport[2],
                    'longitude_deg': airport[3],
                    'continent': airport[4],
                    'country': airport[5],
                    'cost_of_flight': cost_of_flight,
                    'co2_consumption': co2_consumption,
                    'flyable': True
                })

    return flyable_airports
