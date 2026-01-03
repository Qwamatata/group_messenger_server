import db_client
import IlyasMessageProtocol


def check_password(name, password):
    db_query = db_client.execute_query(
        f'SELECT * FROM Users WHERE Users.username = {name} AND Users.password = {password};', '62.60.178.229', 10052)
    if len(db_query) != 1:
        return 0
    else:
        return 1

