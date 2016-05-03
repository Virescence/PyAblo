import mysql.connector
import sys
import socket
import threading
import json


class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        threading.Thread(target=self.listen).start()

    def listen(self):
        while True:
            try:
                print("test")
                data, addr = self.sock.recvfrom(1024)
                data = data.decode()
                data = json.loads(data)
                print(data)
                sql(data[0][0], data[0][1], (data[1][0], data[1][1]))
            except:
                pass

    def send(self, message_to_send, specific_client=None):
        self.sock.sendto(message_to_send.encode(), specific_client)


def check_un(db_u):
    if db_u:
        for row in db_u:
            return True
    else:
        return False


def check_pw(db_p, user_p):
    for row in db_p:
        if row[0] == user_p:
            return True
        else:
            return False


def sql(user, passw, addr):

    # cnx = mysql.connector.connect(user='sec_user', password='eemVhBtQENp8Yzz', host='127.0.0.1', port='3306',
                                  # database='secure_login')

    cnx = mysql.connector.connect(user='sec_user', password='eemVhBtQENp8Yzz', host='dylanschlabach.com', port='23060',
                                  database='secure_login')

    cursor_un = cnx.cursor()
    cursor_pw = cnx.cursor()

    query1 = ("SELECT id,username FROM members WHERE username = '%s';" % (user))
    print(query1)
    cursor_un.execute(query1)

    result1 = cursor_un.fetchall()

    print(result1)
    for row in result1:
        objid = row[0]
        print(objid)

    if check_un(result1):
        print("Username is valid")
    else:
        print("Invalid Username")
        cursor_un.close()
        cursor_pw.close()
        cnx.close()
        message = addr
        message = "^db^False" + json.dumps(message)
        print(message)
        svr.send(message, ("localhost", 1234))

    query2 = ("SELECT password FROM members WHERE username = '%s';" % (user))
    cursor_pw.execute(query2)
    result2 = cursor_pw.fetchall()

    if check_pw(result2, passw):
        print("Valid Password")
        message = [user, objid, addr]
        message = "^db^" + json.dumps(message)
        print(message)
        svr.send(message, ("localhost", 1234))
        # svr.send('^id^' + str(objid), ("localhost", 1234))
    else:
        print("Invalid Password")
        message = addr
        message = "^db^False" + json.dumps(message)
        print(message)
        svr.send(message, ("localhost", 1234))
        # svr.send('^db^False', ("localhost", 1234))

    cursor_un.close()
    cursor_pw.close()

    cnx.close()


svr = Server("", 1235)

sys.exit()