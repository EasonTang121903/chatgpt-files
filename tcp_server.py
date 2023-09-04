#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket,threading
import time
import os
import sys


def tcplink(sock, addr):
    import serial
    print 'A new connection from  %s : %s ...' % (addr[0], addr[1])
    while True:
        time.sleep(0.3)
        data = sock.recv(1024)
        print'receive data: ', data.decode('utf-8', 'ignore')
        if len(data) <= 0:
            print("connection close!")
            break
        elif 'serial_port' in data:
            data = data.split(",")
            serial_port = data[1]
            baud_rate = data[3]
            # Open the serial & send log info to server
            serial = serial.Serial(serial_port, baud_rate)
            if serial.isOpen():
                print 'serial open success'
            else:
                print 'serial open failed'
                break

            data = sock.recv(1024)
            print 'receive data: ', data.decode('utf-8', 'ignore')
            data = data.split(",")
            filename = data[1]

            # create log file , case by case
            dir_path = './serial_log/serial_' + serial_port
            file_path = dir_path + "/" + filename + ".txt"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            else:
                for i in os.listdir(dir_path):
                    file_data = dir_path + "/" + i
                    if os.path.isfile(file_data) is True:
                        os.remove(file_data)

            fo = open(file_path, "a+")
            while True:
                time.sleep(0.3)
                log_data = serial.read_all()
                print log_data
                time.sleep(0.01)

                # write date into file
                fo.write(log_data)

                data = sock.recv(1024)
                if "close serial" in data:
                    log_data = serial.read_all()
                    print log_data
                    
                    # write date into file
                    fo.write(log_data)
                    fo.flush()
                    fo.close()
                    print 'serial closed'
                    serial.close()
                    break
            time.sleep(3)
            #update file
            if os.path.isfile(file_path):
                size = os.stat(file_path).st_size
                sock.send(str(size).encode('utf-8'))
                print 'file size:', size / 1024, 'KB'

                sock.recv(1024)
                f = open(file_path, 'rb')
                for line in f:
                    sock.send(line)

                f.close()
            else:
                sock.send('file not exist'.encode("utf-8"))
            break



#
#def main():
#    server = ThreadingTCPServer(('127.0.0.1', 8888), Handler)
#    print("Listening")
#    server.serve_forever()


if __name__ == '__main__':
    #create socket
    soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    #listen port
    soc.bind(('0.0.0.0',8124))
    soc.listen(5)
    print "Wait for connection..."

    while True:
        # Receive a new connection
        sock,addr = soc.accept()

        #create a new thread to process TCP connection
        thread = threading.Thread(target=tcplink,args=(sock,addr))
        thread.start()