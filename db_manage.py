import database

session, engine = database.connect_to_database()

while True:
    print('"D" for dump, "D" to add song, "GS" to get song, "G" to get genre, "AG" to add genre')
    print('"RF" to fill database, "AU" to add user, "GLS" to get listened songs, "ALS" to add listened songs\n')
    action = input()

    if action == 'D' or action == 'd':
        database.dump_database(engine)

    if action == 'A' or action == 'a':
        link = input('input link to song ==>    ')
        genre = input('input song genre ==>    ')
        result = database.add_song(genre, link, session)
        print(result)

    if action == 'gs'or action == 'GS':
        genre = input('input song genre ==>    ')
        database.get_random_song_from_genre(session, genre)

    if action == 'G' or action == 'G':
        genres = database.genres
        print(genres)

    if action == 'RF' or action == 'rf':
        database.random_fill(session, engine)

    if action == 'AU':
        telegram_id = input('input id')
        database.add_user(telegram_id)

    if action == 'GLS':
        telegram_id = input('input id')
        genre = input('input genre')
        listened = database.get_listened_from_genre(telegram_id, genre)
        print(listened)

    if action == 'ALS':
        telegram_id = input('input id')
        genre = input('input genre')
        link = input('input link')
        database.add_song_to_listened(telegram_id, link, genre)

    if action == 'q' or action == 'Q':
        break

    else:
        continue
