#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import threading
import time
import os

stop_signal = False


class Client:
    def __init__(self):
        # ipv4  TCP
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, server_ip, server_port):
        print 'Connect server :', server_ip, ':', server_port
        self.client.connect((server_ip, server_port))

    def run(self, case_name, serial_port, baud_rate):
        message = "serial_port," + serial_port + ",baud_rate," + baud_rate
        self.client.send(message)
        time.sleep(1)
        message2 = "case_name," + case_name
        self.client.send(message2)
        time.sleep(1)

        while True:
            time.sleep(0.3)
            self.client.send('Running')
            if stop_signal is True:
                self.client.send("close serial")
                print "connection close!"
                break

        time.sleep(3)
        while True:
            time.sleep(0.3)
            server_response = self.client.recv(1024)
            try:
                file_size = int(server_response.decode("utf-8"))
            except:#   delete
                print 'file not exist'
                break
            print 'file size:', file_size / 1024, 'KB'
            self.client.send("Ready to recv")
            
            dir_path = './serial_log/serial_' + serial_port
            file_path = dir_path + "/" + case_name + ".txt"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                
            fo = open(file_path, "wb")
            received_size = 0

            while received_size < file_size:
                size = 0
                if file_size - received_size > 1024:
                    size = 1024
                else:
                    size = file_size - received_size

                data = self.client.recv(size)
                data_len = len(data)
                received_size += data_len
                print 'Receiving...:', int(received_size / file_size * 100), "%"
                fo.write(data)
            fo.close()
            self.client.close()
            break

    def wait_result(self):
        self.thread.join()

    def disconnected(self):
        global stop_signal
        stop_signal = True

    def check_thread_state(self):
        status = self.thread.is_alive()
        
        return status

    def create_connect_thread(self,ip, case_name, serial_port, port = 13999, baud_rate = 115200):
        if ip is None:
            print '[Error]~~~~~~~~~~~ip is empty'
            sys.exit(0)
        elif serial_port is None:
            print '[Error]~~~~~~~~~~~serial_port is empty'
            sys.exit(0)
        else:
            client = Client()
            client.connect(ip, port)
            self.thread = threading.Thread(target=client.run, args=(case_name, serial_port, baud_rate))
            self.thread.start()



if __name__ == '__main__':

    client = Client()
    client.connect('127.0.0.1', 8888)
    thread = threading.Thread(target=client.run, args=("ASAN","test_msp.av.mt_xxx_test"))
    thread.start()
    time.sleep(50)
    active_stop()
