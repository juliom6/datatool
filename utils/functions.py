def dict_factory(cursor, row):
    d = {}
    for key, col in enumerate(cursor.description):
        d[col[0]] = row[key]
    return d