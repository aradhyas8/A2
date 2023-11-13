'''
    *  Description:  Class for communication between server and client.
    *  
    *  FOR EDUCATION PURPOSES OF ONLY. DO NOT DITSRIBUTE.    
'''
import struct

from enum import Enum

'''

This file shouldn't be changed

'''

class Message(bytes, Enum):
     CHALLENGE  = bytes("CHALLENGE", "ascii")
     RESPONSE =  bytes("RESPONSE", "ascii")
     SUCCESS  = bytes("SUCCESS", "ascii")
     SESSION_MESSAGE = bytes("SESSION_MESSAGE", "ascii")

 

class Conn(object):
    def __init__(self, conn,
                 client=False,
                 server=False,
                 user=None,
                 verbose=False):
        self.conn = conn
        self.cipher = None
        self.client = client
        self.server = server
        self.verbose = verbose
        self.user = user


    def send(self, data):
  
        # Encode the data's length into an unsigned two byte int ('H')
        pkt_len = struct.pack('H', len(data))
        self.conn.sendall(pkt_len)
        self.conn.sendall(data)

        #for testing
        #print("Sending to ", self.conn)
        return (struct.pack('H', len(data)), data)

    def recv(self):
        # Decode the data's length from an unsigned two byte int ('H')
        pkt_len_packed = self.conn.recv(struct.calcsize('H'))
        unpacked_contents = struct.unpack('H', pkt_len_packed)
        pkt_len = unpacked_contents[0]

        data = self.conn.recv(pkt_len)

        return data

    def close(self):
        self.conn.close()
