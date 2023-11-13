'''
    *  Full Name:
    *  Course:EECS 3482 A
    *  Description:  Client program. Established connection with the server
    *  FOR EDUCATION PURPOSES OF ONLY. DO NOT DITSRIBUTE.
'''
import socket
import sys, os, getopt
import pickle

import ssl
import pyfiglet
import logging


from lib.comms import Conn
from lib.comms import Message

from Crypto.PublicKey import ECC

class Client:

       def __init__(self, 
                    client_key_password,
                    ca_crt_path,
                    port):
            """    
            client_key_password: the password used to protect the client’s private key
            ca_crt_patj: path to the certificate for the certificate authority (CA)
            port: integer representing the TCP port on which the client connects to the server

            """

            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M',
                                filename='client.log',
                                filemode='w')
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)


            self.client_log =  logging.getLogger(self.__class__.__name__)
            

            #do not change internal variables
            
            self._port = port            
            self.client_key_password = client_key_password
            self.client_priv_key = None
            self.ca_crt_path = ca_crt_path

            self.protocol_state = 'START'

            self.generate_client_keys()
           
            
       def generate_client_keys(self):
            
            key = ECC.generate(curve='P-256')

            if not os.path.exists("data/client_priv_key.pem"):
                f = open('data/client_priv_key.pem','wt')
                f.write(key.export_key(format='PEM'))
                f.close()

            if not os.path.exists("data/client_pub_key.pem"):
                f = open('data/client_pub_key.pem','wt')
                f.write(key.public_key().export_key(format='PEM'))
                f.close()

            
            self.client_priv_key = ECC.import_key(open('data/client_priv_key.pem').read())

    
       def protocol_abort(self):
        """
         Return: nothing

         This function should generate a challenge (encoded as a string) to send to the client.          
        """            
        self.client_log.info('Abort protocol intiated')
        self.protocol_state = 'ABORT'
        exit()
    
  
       def check_cert(self, cert):
        """        
        Return Booleain: True the cetificate is valid
        """
        # TODO: implement the X.509 certificate checks

        return True
        



       def process_server_msg(self,sconn):
            """
            sconn: socket wrapper between client and server                
        
            Return: nothing
            """      
                       
            while True:
                data = sconn.recv()
                
                recv_msg = pickle.loads(data)
                if recv_msg['type'] == Message.CHALLENGE:      
                    if self.protocol_state != 'START':
                        self.protocol_abort()

                    self.protocol_state = 'CHALLENGE'
                    self.client_log.info('Challenge received')

                    # TODO:Respond to chanllenge
                    self.client_log.info('Sending response')
                    msg = pickle.dumps({"type":Message.RESPONSE, 'msg':'my_response'})
                    sconn.send(msg)
                


                elif recv_msg['type'] ==  Message.SUCCESS:
                    if self.protocol_state != 'CHALLENGE':
                         self.protocol_abort()
                    
                    self.protocol_state = 'SUCCESS'                    
                
                    msg = pickle.dumps({"type":Message.SESSION_MESSAGE, \
                                        'msg':bytes("Hello Word"," ascii")})
                    sconn.send(msg)


                elif recv_msg['type']== Message.SESSION_MESSAGE:
                    if self.protocol_state != 'SUCCESS':
                         self.protocol_abort()

                    message = recv_msg['msg']
                    self.client_log.info("Pong msg [%s]" % message.decode())
                    self.protocol_state = 'END'
                    self.protocol_abort()
                    
                
          
       def connect(self):
            """
            Establishes connections between client and client on self._port.

            Return: nothing
            """
                
            try:
                client_ssl_options = {
                    # TODO: Fill in options
                    "ca_certificate": None,
                    "host": None,
                    "port": None,         
                    }

                if client_ssl_options['ca_certificate']:
                    self.client_log.info("Found server on port %d" % self._port)                    

                    # Create a socket and wrap it with SSL context
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    context.verify_mode = ssl.CERT_REQUIRED     
                    context.load_verify_locations(client_ssl_options['ca_certificate'])
            
                    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                              
                    secure_socket = context.wrap_socket(conn, server_hostname=client_ssl_options['host'])                    
                    secure_socket.connect((client_ssl_options['host'],client_ssl_options['port']))

                    # Get the peer's certificate
                    peer_certificate = secure_socket.getpeercert()                                 

                    #Check if the certificate is valid
                    if not self.check_cert(peer_certificate):
                        self.client_log.error('invalid certificate received')                        
                        self.protocol_abort()
                else:
                    # without proper TLS setup we are on unsecure channel
                    self.client_log.warning("Initiated Insecure Communication")
                    secure_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
                    secure_socket.connect(("localhost", self._port))          
                
                self.client_log.info('Connected to server')                
                sconn = Conn(secure_socket, client=True)
                self.process_server_msg(sconn)

            except socket.error as se:
                    self.client_log.error("No server found on port %d" % self._port,se)



def main(argv):

    #default port
    server_port=1337
    try:
        opts, args = getopt.getopt(argv,"hp:",["port="])
    except getopt.GetoptError:
        print('client.py -port <port>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('client.py -port <port>')
            sys.exit()
        elif opt in ("-p", "--port"):
            if arg:
                server_port = int(arg)

    Client(None, 
         None, 
         server_port).connect()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nDone!")
