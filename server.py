import datetime
import json
import socket
import threading
import IlyasMessageProtocol
import db_helper
import db_client

full_message = b'start chat\n'


def client_handler(client_socket):
    global full_message
    global connected_clients
    attempts = 3
    while attempts != 0:
        name = IlyasMessageProtocol.receive(client_socket)[1]
        password = IlyasMessageProtocol.receive(client_socket)[1]
        if not db_helper.check_password(name, password):
            attempts -= 1
            IlyasMessageProtocol.send(client_socket, '2'.encode(), 'ERR')
        else:
            IlyasMessageProtocol.send(client_socket, '1'.encode(), 'ERR')
            break
    connected_clients[name] = client_socket
    IlyasMessageProtocol.send(client_socket, full_message, 'TXT')
    while True:
        string_and_type = IlyasMessageProtocol.receive(client_socket)
        print(string_and_type)
        if string_and_type[0] != 'ERR':
            string = string_and_type[1].encode()
            full_message += string
        if string_and_type[1] == '200' and string_and_type[0] == 'ERR':
            del connected_clients[name]
            IlyasMessageProtocol.send(client_socket, '200'.encode(), 'ERR')
            client_socket.close()
            break
        if string.decode()[0] == '/':
            if string.decode() == '/users':
                all_users = db_client.execute_query('SELECT username FROM Users;', '62.60.178.229', 10052)
                print(all_users)
                for user in all_users:
                    if user in connected_clients:
                        user['status'] = 'online'
                    else:
                        user['status'] = 'offline'
                IlyasMessageProtocol.send(client_socket, json.dumps(all_users).encode(), 'JSN')
        else:
            if string.decode()[0] == '@':
                names_and_message = string.decode().split(' ')
                direct_names = []
                message_list = []
                message = b''

                for index in range(len(names_and_message)):
                    if names_and_message[index][0] == '@':
                        direct_names.append(names_and_message[index].split('@')[1])
                    else:
                        message_list.append(names_and_message[index])
                print(direct_names)
                receivers = ','.join(direct_names)
                message = ' '.join(message_list).encode()
                for direct_name in direct_names:

                    if direct_name in connected_clients:
                        IlyasMessageProtocol.send(connected_clients[direct_name],
                                                  ' '.join([name, message.decode()]).encode(), 'TXT', 'a')
                    else:
                        IlyasMessageProtocol.send(client_socket, f'User @{direct_name} offline'.encode(), 'TXT', 'a')
            else:
                message = string
                for client_name in connected_clients:
                    if client_name != name:
                        IlyasMessageProtocol.send(connected_clients[client_name], f'{name}:{string.decode()}'.encode(),
                                                  'TXT', 'a')
                receivers = 'no users'
            current_time = datetime.datetime.now()
            date = current_time.date().strftime('%d.%m.%y')
            time = current_time.time().strftime('%H:%M:%S')

            print(db_client.execute_query(f'INSERT INTO messages (text, author, date, time, receivers) VALUES ({message.decode()}, {name}, {date}, {time}, {receivers});', '62.60.178.229', 10052))

    client_socket.close()


connected_clients = {}

socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket_server.bind(('0.0.0.0', 8652))

socket_server.listen()

try:
    while True:
        print('wait connection')
        client = socket_server.accept()

        client_socket = client[0]
        client_address = client[1]
        print(f'{client_address} has connected.')

        thread = threading.Thread(target=client_handler, args=[client_socket])
        thread.start()
except KeyboardInterrupt:
    print('server is closing')
finally:
    socket_server.close()
