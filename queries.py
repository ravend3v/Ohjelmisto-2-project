GET_GAMES = """
    SELECT pg.game_id, g.location, p.user_name
    FROM player_game pg
    JOIN player p ON pg.player_id = p.Id
    JOIN game g ON pg.game_id = g.Id
    WHERE g.game_over = 0 AND p.Id = %s
    GROUP BY pg.game_id;
"""

GET_GAMES_CURRENT_LOCATION_DATA = """
    SELECT airport.ident, airport.name, airport.latitude_deg, airport.longitude_deg, airport.continent, game.money, country.name
    FROM airport
    JOIN game
    ON airport.ident = game.location
    JOIN country
    ON airport.iso_country = country.iso_country
    WHERE game.Id = %s
"""

GET_ALL_AIRPORTS = """
    SELECT airport.ident, airport.name, airport.latitude_deg, airport.longitude_deg, airport.continent, country.name
    FROM airport
    JOIN country
    ON airport.iso_country = country.iso_country
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

GET_VISITED_CONTINENTS = """
    SELECT GROUP_CONCAT(DISTINCT gv.visited_continent ORDER BY gv.visited_continent SEPARATOR '|') AS visited_locations
    FROM game_visited gv
    WHERE game_id = %s;
"""