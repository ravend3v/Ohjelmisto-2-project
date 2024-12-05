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
    SELECT airport.ident, airport.name, airport.latitude_deg, airport.longitude_deg, airport.continent, player.money
    FROM airport
    JOIN player
    ON airport.ident = player.location
    WHERE player.Id = %s
"""

UPDATE_PLAYER_DATA = """
    UPDATE player
    SET location = %s, co2_consumed = co2_consumed + %s, money = money + %s
    WHERE Id = %s
"""

UPDATE_PLAYER_VISITED = """
    INSERT INTO player_visited (player_id, visited_continent)
    SELECT %s, %s
    WHERE NOT EXISTS (
        SELECT 1 FROM player_visited
        WHERE player_id = %s AND visited_continent = %s
    )
"""