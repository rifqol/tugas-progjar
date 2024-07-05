from socket import *
import socket
import threading
import sys
import os
import json
import uuid
import logging
from queue import  Queue

class RealmThreadCommunication(threading.Thread):
    def __init__(self, chats, realm_dest_address, realm_dest_port):
        self.chats = chats
        self.chat = {
            'users': {},
            'groups': {}
        }
        self.realm_dest_address = realm_dest_address
        self.realm_dest_port = realm_dest_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.realm_dest_address, self.realm_dest_port))
            threading.Thread.__init__(self)
        except:
            return None

    def sendstring(self, string):
        try:
            self.sock.sendall(string.encode())
            receivedmsg = ""
            while True:
                data = self.sock.recv(32)
                print("diterima dari server", data)
                if (data):
                    receivedmsg = "{}{}" . format(receivedmsg, data.decode())
                    if receivedmsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivedmsg)
        except:
            self.sock.close()
            return {'status': 'ERROR', 'message': 'Gagal'}

    def put_private(self, message):
        dest = message['msg_to']
        try:
            self.chat['users'][dest].put(message)
        except KeyError:
            self.chat['users'][dest] = Queue()
            self.chat['users'][dest].put(message)
    
    def put_group(self, message):
        dest = message['msg_to']
        try:
            self.chat['groups'][dest].put(message)
        except KeyError:
            self.chat['groups'][dest] = Queue()
            self.chat['groups'][dest].put(message)

class Chat:
    def __init__(self):
        self.sessions={}
        self.users = {}
        self.users['messi']={ 'nama': 'Lionel Messi', 'negara': 'Argentina', 'password': 'surabaya', 'incoming' : {}, 'outgoing': {}}
        self.users['henderson']={ 'nama': 'Jordan Henderson', 'negara': 'Inggris', 'password': 'surabaya', 'incoming': {}, 'outgoing': {}}
        self.users['lineker']={ 'nama': 'Gary Lineker', 'negara': 'Inggris', 'password': 'surabaya','incoming': {}, 'outgoing':{}}
        self.groups = {}
        self.realms = {}
        self.realms_info = {}

    def proses(self,data):
        j=data.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                logging.warning("AUTH: auth {} {}" . format(username,password))
                return self.autentikasi_user(username,password)
            
            # Fitur Baru Autentikasi
            elif command == "register":
                nama = j[1].strip()
                negara = j[2].strip()
                username = j[3].strip()
                password = j[4].strip()
                logging.warning("REGISTER: register {} {}".format(username, password))
                return self.register(nama, negara, username, password)
            
            elif (command == "logout"):
                return self.logout()
            
            elif (command=='send'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                message=""
                for w in j[3:]:
                    message="{} {}" . format(message,w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
                return self.send_message(sessionid,usernamefrom,usernameto,message)

            elif (command=='inbox'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOX: {}" . format(sessionid))
                return self.get_inbox(username)

            # Local Group-related
            elif (command=='getgroups'):
                return self.get_groups()
            
            elif (command=='addgroup'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                groupname=j[2].strip()
                password=j[3].strip()
                logging.warning("ADDGROUP: session {} username {} addgroup {} {}" . format(sessionid, username, groupname, password))
                return self.add_group(sessionid,username,groupname,password)

            elif (command=='joingroup'):
                sessionid = j[1].strip()
                username = self.sessions[sessionid]['username']
                groupname=j[2].strip()
                password=j[3].strip()
                logging.warning("JOINGROUP: session {} username {} joingroupgroup {} {}" . format(sessionid, username, groupname, password))
                return self.join_group(sessionid,username,groupname,password)

            elif (command=='sendgroup'):
                sessionid = j[1].strip()
                groupname = j[2].strip()
                message=""
                for w in j[3:]:
                    message="{} {}" . format(message,w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SENDGROUP: session {} send message from {} to group {}" . format(sessionid, usernamefrom, groupname))
                return self.send_group(sessionid,usernamefrom,groupname,message)

            elif (command=='inboxgroup'):
                sessionid = j[1].strip()
                groupname = j[2].strip()
                username = self.sessions[sessionid]['username']
                logging.warning("INBOXGROUP: {}" . format(groupname))
                return self.get_inbox_group(sessionid, username, groupname)
            
            # File-related
            elif (command=='sendfile'):
                sessionid = j[1].strip()
                usernameto = j[2].strip()
                filename = j[3].strip()
                filecontent=""
                for w in j[4:]:
                    filecontent="{} {}" . format(filecontent,w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SENDFILE: session {} send file from {} to {}" . format(sessionid, usernamefrom,usernameto))
                return self.send_file(sessionid,usernamefrom,usernameto,filename,filecontent)
            
            elif (command=='downloadfile'):
                sessionid = j[1].strip()
                fileid = j[2].strip()
                filename = j[3].strip()
                logging.warning("DOWNLOADFILE: {} {}" . format(fileid,filename))
                return self.download_file(sessionid,fileid,filename)
          
            elif (command=='sendgroupfile'):
                sessionid = j[1].strip()
                groupname = j[2].strip()
                filename = j[3].strip()
                filecontent=""
                for w in j[4:]:
                    filecontent="{} {}" . format(filecontent,w)
                usernamefrom = self.sessions[sessionid]['username']
                logging.warning("SENDGROUPFILE: session {} send file from {} to {}" . format(sessionid, usernamefrom,groupname))
                return self.send_group_file(sessionid,usernamefrom,groupname,filename,filecontent)
            
            elif (command=='downloadgroupfile'):
                sessionid = j[1].strip()
                groupname = j[2].strip()
                fileid = j[3].strip()
                filename = j[4].strip()
                logging.warning("DOWNLOADGROUPFILE: {} {}" . format(fileid,filename))
                return self.download_group_file(sessionid,groupname,fileid,filename)
       
            
            elif command == "sessioncheck":
                return self.sessioncheck()
            
            else:
                return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}

        except KeyError:
            return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
        except IndexError:
            return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}


# IMPLEMENTATION FUNCTIONS
    def autentikasi_user(self,username,password):
        if (username not in self.users):
            return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
        if (self.users[username]['password']!= password):
            return { 'status': 'ERROR', 'message': 'Password Salah' }
        tokenid = str(uuid.uuid4()) 
        self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
        return { 'status': 'OK', 'tokenid': tokenid }

    # FITUR AUTENTIKASI BARU
    def register(self, nama, negara, username, password):
        nama = nama.replace("-", " ")
        if username in self.users:
            return {"status": "ERROR", "message": "User Sudah Terdaftar"}
        self.users[username] = {"nama": nama, "negara": negara, "password": password, "incoming": {}, "outgoing": {}}
        tokenid = str(uuid.uuid4())
        self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
        return {"status": "OK", "tokenid": tokenid}
    
    def logout(self):
        if bool(self.sessions) == True:
            self.sessions.clear()
            return {"status": "OK"}
        else:
            return {"status": "ERROR", "message": "User Belum Login"}
    
    def get_user(self,username):
        if (username not in self.users):
            return False
        return self.users[username]

    def send_message(self,sessionid,username_from,username_dest,message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)

        if (s_fr==False or s_to==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': message }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:	
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from]=Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from]=Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def get_inbox(self,username):
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        msgs={}
        for users in incoming:
            msgs[users]=[]
            temp_queue = incoming[users].queue.copy()
            while len(temp_queue) > 0:
                msgs[users].append(temp_queue.pop())

        return {'status': 'OK', 'messages': msgs}

    # Local Group-related
    def get_group(self,groupname):
        if (groupname not in self.groups):
            return False
        return self.groups[groupname]

    def add_group(self,sessionid,username,groupname,password):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (groupname in self.groups):
            return { 'status': 'ERROR', 'message': 'Group sudah ada' }
        self.groups[groupname]={
            'nama': groupname,
            'password': password,
            'incoming' : {},
            'members' : [],
            'incomingrealm' : {}
        }
        self.groups[groupname]['members'].append(username)
        return { 'status': 'OK', 'message': 'Add group berhasil' }

    def join_group(self,sessionid,username,groupname,password):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (groupname not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (self.groups[groupname]['password']!= password):
            return { 'status': 'ERROR', 'message': 'Password Salah' }
        if (username in self.groups[groupname]['members']):
            return { 'status': 'ERROR', 'message': 'User sudah join' }
        self.groups[groupname]['members'].append(username)
        return { 'status': 'OK', 'message': 'Join group berhasil' }

    def send_group(self,sessionid,username_from,group_dest,message):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (group_dest not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (username_from not in self.groups[group_dest]['members']):
            return { 'status': 'ERROR', 'message': 'Bukan member group' }
        s_fr = self.get_user(username_from)
        g_to = self.get_group(group_dest)

        if (s_fr==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        if (g_to==False):
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}

        message = { 'msg_from': s_fr['nama'], 'msg_ufrom': username_from, 'msg_to': g_to['nama'], 'msg': message }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = g_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from]=Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from]=Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Message Sent'}

    def get_inbox_group(self,sessionid, username, groupname):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (groupname not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (username not in self.groups[groupname]['members']):
            return { 'status': 'ERROR', 'message': 'Bukan member group' }
        s_fr = self.get_group(groupname)
        incoming = s_fr['incoming']
        msgs={}
        for users in incoming:
            msgs[users]=[]
            temp_queue = incoming[users].queue.copy()
            while len(temp_queue) > 0:
                msgs[users].append(temp_queue.pop())

        return {'status': 'OK', 'messages': msgs}

    
    # File-related
    def send_file(self,sessionid,username_from,username_dest,filename,filecontent):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_dest)

        if (s_fr==False or s_to==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

        message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'],'fileid': str(uuid.uuid4()),'filename': filename, 'filecontent':filecontent }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from]=Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from]=Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'File Sent', 'fileid': message['fileid']}
    
    def download_file(self,sessionid,fileid,filename):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        username = self.sessions[sessionid]['username']
        s_fr = self.get_user(username)
        incoming = s_fr['incoming']
        filecontent=""
        for users in incoming:
            temp_queue = incoming[users].queue.copy()
            while len(temp_queue) > 0:
                msg = temp_queue.pop()
                print("MSG: {}". format(msg))
                if 'fileid' in msg and msg['fileid']==fileid:
                    return {'status': 'OK', 'message': msg['filecontent']}
        return {'status': 'ERROR', 'message': 'File tidak ditemukan'}
    
    def send_group_file(self,sessionid,username_from,group_dest,filename,filecontent):
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (group_dest not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (username_from not in self.groups[group_dest]['members']):
            return { 'status': 'ERROR', 'message': 'Bukan member group' }
        s_fr = self.get_user(username_from)
        g_to = self.get_group(group_dest)

        if (s_fr==False):
            return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}
        if (g_to==False):
            return {'status': 'ERROR', 'message': 'Group Tidak Ditemukan'}

        message = { 'msg_from': s_fr['nama'], 'msg_to': g_to['nama'], 'fileid': str(uuid.uuid4()), 'filename': filename, 'filecontent':filecontent }
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = g_to['incoming']
        try:
            outqueue_sender[username_from].put(message)
        except KeyError:
            outqueue_sender[username_from]=Queue()
            outqueue_sender[username_from].put(message)
        try:
            inqueue_receiver[username_from].put(message)
        except KeyError:
            inqueue_receiver[username_from]=Queue()
            inqueue_receiver[username_from].put(message)
        return {'status': 'OK', 'message': 'Group File Sent'}
    
    def download_group_file(self,sessionid,groupname,fileid,filename):
        username = self.sessions[sessionid]['username']
        if (sessionid not in self.sessions):
            return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
        if (groupname not in self.groups):
            return { 'status': 'ERROR', 'message': 'Group belum ada' }
        if (username not in self.groups[groupname]['members']):
            return { 'status': 'ERROR', 'message': 'Bukan member group' }
        s_fr = self.get_group(groupname)
        incoming = s_fr['incoming']
        filecontent=""
        for users in incoming:
            temp_queue = incoming[users].queue.copy()
            while len(temp_queue) > 0:
                msg = temp_queue.pop()
                print("MSG: {}". format(msg))
                if 'fileid' in msg and msg['fileid']==fileid:
                    return {'status': 'OK', 'message': msg['filecontent']}
        return {'status': 'ERROR', 'message': 'File tidak ditemukan'}
    
    def get_groups(self):
        return {"status": "OK", "message": self.groups}

    def sessioncheck(self):
        return {"status": "OK", "message": self.sessions}

if __name__=="__main__":
    j = Chat()
#     sesi = j.proses("auth messi surabaya")
#     print(sesi)
#     #sesi = j.autentikasi_user('messi','surabaya')
#     #print sesi
#     tokenid = sesi['tokenid']
#     print(j.proses("send {} henderson hello gimana kabarnya son " . format(tokenid)))
#     print(j.proses("send {} messi hello gimana kabarnya mess " . format(tokenid)))

#     #print j.send_message(tokenid,'messi','henderson','hello son')
#     #print j.send_message(tokenid,'henderson','messi','hello si')
#     #print j.send_message(tokenid,'lineker','messi','hello si dari lineker')


#     print("isi mailbox dari messi")
#     print(j.get_inbox('messi'))
#     print("isi mailbox dari henderson")
#     print(j.get_inbox('henderson'))

    sesi = j.proses("auth henderson surabaya")
    print(sesi)
    token_id = sesi['tokenid']