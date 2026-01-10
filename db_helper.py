import db_client


def check_password(name, password, host: str, port: int):
    db_query = db_client.execute_query(
        f'SELECT * FROM Users WHERE Users.username = {name} AND Users.password = {password};', host, port)
    if len(db_query) != 1:
        return 0
    else:
        return 1

