CREATE TABLE `airport`(
    `id` INT(11) NOT NULL,
    `ident` VARCHAR(40) NOT NULL,
    `type` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `name` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `latitude_deg` DOUBLE NULL DEFAULT 'DEFAULT NULL',
    `longitude_deg` DOUBLE NULL DEFAULT 'DEFAULT NULL',
    `elevation_ft` INT(11) NULL DEFAULT 'DEFAULT NULL',
    `continent` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `iso_country` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `iso_region` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `municipality` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `scheduled_service` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `gps_code` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `iata_code` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `local_code` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `home_link` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `wikipedia_link` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `keywords` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    PRIMARY KEY(`ident`)
);
ALTER TABLE
    `airport` ADD INDEX `airport_iso_country_index`(`iso_country`);
CREATE TABLE `country`(
    `iso_country` VARCHAR(40) NOT NULL,
    `name` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `continent` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `wikipedia_link` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    `keywords` VARCHAR(40) NULL DEFAULT 'DEFAULT NULL',
    PRIMARY KEY(`iso_country`)
);
CREATE TABLE `game`(
    `Id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `game_over` TINYINT(1) NULL DEFAULT 'DEFAULT NULL'
);
CREATE TABLE `player`(
    `Id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `user_name` VARCHAR(255) NOT NULL,
    `password` CHAR(60) NOT NULL,
    `co2_consumed` INT(11) NOT NULL,
    `money` INT(11) NOT NULL,
    `location` VARCHAR(255) NOT NULL
);
CREATE TABLE `player_game`(
    `player_id` INT(11) NOT NULL,
    `game_id` INT(11) NOT NULL,
    PRIMARY KEY(`player_id`)
);
ALTER TABLE
    `player_game` ADD PRIMARY KEY(`game_id`);
CREATE TABLE `country_questions`(
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `iso_country` VARCHAR(40) NOT NULL,
    `country_name` VARCHAR(255) NOT NULL,
    `question_text` LONGTEXT NOT NULL,
    `option1` TEXT NOT NULL,
    `option2` TEXT NOT NULL,
    `option3` TEXT NOT NULL,
    `option4` TEXT NOT NULL
);
ALTER TABLE
    `player` ADD CONSTRAINT `player_id_foreign` FOREIGN KEY(`Id`) REFERENCES `player_game`(`player_id`);
ALTER TABLE
    `country_questions` ADD CONSTRAINT `country_questions_iso_country_foreign` FOREIGN KEY(`iso_country`) REFERENCES `country`(`iso_country`);
ALTER TABLE
    `player` ADD CONSTRAINT `player_location_foreign` FOREIGN KEY(`location`) REFERENCES `airport`(`ident`);
ALTER TABLE
    `airport` ADD CONSTRAINT `airport_iso_country_foreign` FOREIGN KEY(`iso_country`) REFERENCES `country`(`iso_country`);
ALTER TABLE
    `game` ADD CONSTRAINT `game_id_foreign` FOREIGN KEY(`Id`) REFERENCES `player_game`(`game_id`);