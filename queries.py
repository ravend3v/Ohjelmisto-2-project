GET_GAMES = """
    SELECT pg.game_id, g.location, p.user_name
    FROM player_game pg
    JOIN player p ON pg.player_id = p.Id
    JOIN game g ON pg.game_id = g.Id
    WHERE g.game_over = 0 AND p.Id = %s
    GROUP BY pg.game_id;
"""

GET_GAMES_CURRENT_LOCATION_DATA = """
    SELECT airport.ident, airport.name, airport.latitude_deg, airport.longitude_deg, airport.continent, game.money
    FROM airport
    JOIN game
    ON airport.ident = game.location
    WHERE game.Id = %s
"""

UPDATE_GAME_DATA = """
    UPDATE game
    SET location = %s, co2_consumed = co2_consumed + %s, money = money + %s
    WHERE Id = %s
"""

UPDATE_PLAYER_VISITED = """
    INSERT INTO game_visited (game_id, visited_continent)
    SELECT %s, %s
    WHERE NOT EXISTS (
        SELECT 1 FROM game_visited
        WHERE game_id = %s AND visited_continent = %s
    )
"""

CREATE_PLAYER_BASE_STATS = """
    UPDATE player
    SET location = %s, money = %s
    WHERE Id = %s
"""

CREATE_GAME = """
    INSERT INTO game (game_over, money, co2_consumed, location)
    VALUES (0, %s, %s, %s)
"""

CREATE_PLAYER_GAME = """
    INSERT INTO player_game (player_id, game_id) VALUES (%s, %s)
"""