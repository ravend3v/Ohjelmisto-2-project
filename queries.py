GET_GAMES = """
    SELECT pg.game_id, 
        GROUP_CONCAT(p.user_name ORDER BY p.user_name ASC SEPARATOR ',  ') AS players
    FROM player_game pg
    JOIN player p ON pg.player_id = p.Id
    JOIN game g ON pg.game_id = g.Id
    WHERE g.game_over = 0 AND p.Id = %s
    GROUP BY pg.game_id;
"""

GET_CURRENT_PLAYER_LOCATION_DATA = """
    SELECT airport.ident, airport.name, airport.latitude_deg, airport.longitude_deg, player.money
    FROM airport
    JOIN player
    ON airport.ident = player.location
    WHERE player.Id = %s
"""