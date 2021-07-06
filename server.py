from os import wait
import threading
import socket
import time
from random import randint

# host = int(input("Da ip u la host:")) nu i nevoe !

host = None
port = None
clients = []
nicknames = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def init_socket():
    global host
    global server

    host1 = socket.gethostname()
    myIP = socket.gethostbyname(host1)
    # host = f'{myIP}'
    host = str(myIP)
    server.bind((host, port))
    server.listen()


def port_number():
    global port
    try:
        port = randint(1025, 65535)
    except ValueError:
        print("Floating point number passed to randint()")
    except TypeError:
        print("Not numeric type value passed to randint()")


def kick_user(name, client):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked'.encode('ascii'), name_index)
    else:
        client.send('ERROR404'.encode('ascii'))


def broadcast(message, index):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)

            if msg.decode('ascii') == '!@#$%^&*()':  # schimbatul culorii
                broadcast(msg, clients.index(client))
                color = client.recv(1024).decode('ascii')
                broadcast(color.encode('ascii'), clients.index(client))

            elif msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin' and msg.decode('ascii')[5:] != 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick, client)
                else:
                    client.send('Command was refused!'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin' and msg.decode('ascii')[4:] != 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban, client)
                    if name_to_ban in nicknames:
                        with open('/home/valase/Scripts/manual/pynetworking/chat/simple_chat/bans.txt', 'a') as f:
                            f.write(f'{name_to_ban}\n')
                        print(f'{name_to_ban} was banned!')
                else:
                    client.send('Command was refused!'.encode('ascii'))
            else:
                if (msg.decode('ascii') == '!exit'):
                    index = clients.index(index)
                    clients.remove(client)
                    client.close()
                    nickname = nicknames[index]
                    broadcast(f'{nickname} has left'.encode('ascii'), index)
                    nicknames.remove(nickname)
                index = clients.index(client)
                broadcast(message, index=index)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} has left'.encode('ascii'), index)
            nicknames.remove(nickname)
            break


def receive():
    global client
    global address
    while True:
        client, address = server.accept()

        print(f'CONNECTED WITH {str(address)}')

        client.send('NICK'.encode('ascii'))

        nickname = client.recv(1024).decode('ascii')
        print(nickname not in nicknames)
        if nickname not in nicknames:
            client.send('OK'.encode('ascii'))
        else:
            print("Duplicat")
            client.send('!OK'.encode('ascii'))
        #               while client.recv(1024).decode('ascii') != 'OK*':

        #        with open('/home/valase/Scripts/manual/pynetworking/chat/simple_chat/bans.txt','r') as f:
        #            bans = f.readlines()
        #
        #        if nickname + '\n' in bans:
        #            client.send('BAN'.encode('ascii'))
        #            continue

        if nickname == 'admin':
            client.send("PASS".encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if password != 'secretpass':
                client.send("REFUSED\n".encode('ascii'))
                client.close()
                continue

        nicknames.append(nickname)
        print(nicknames)
        client.send('CONNECTED'.encode('ascii'))
        clients.append(client)
        print(f'CONNECTED WITH {nickname}')
        broadcast(f'{nickname} ENTERED'.encode('ascii'), clients.index(client))
        client.send('SUCCESFUL CONNECTED'.encode('ascii'))

        handle_server = threading.Thread(target=handle, args=(client,))
        handle_server.start()


def main():
    port_number()
    init_socket()
    print("[*] SERVER LISTENING ...")
    print("[*] IP : " + str(host))
    print("[*] PORT : " + str(port))
    receive()


if __name__ == '__main__':
    main()
