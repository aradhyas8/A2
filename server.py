'''
    *  Full Name:
    *  Course:EECS 3482 A
    *  Description:  Server program. Accepts connections from client programs
    *  FOR EDUCATION PURPOSES OF ONLY. DO NOT DITSRIBUTE.
'''
import socket
import threading
import sys, getopt
import logging
import pyfiglet
import ssl
import pickle

from lib.comms import Conn
from lib.comms import Message



class Server:

    def __init__(self, 
                 server_private_key_path, 
                 server_key_password,
                 server_cert_path,
                 client_pub_key,
                 server_port):      
        """
            server_key_path: the server’s private key
            server_key_password: the password used to protect the server’s private key
            server_cert_path: path to the server’s certificate
            client_pub_key: the client’s public key (used for challenge-response authentication).
            server_port:  integer representing the TCP port on which the server should listen
            
        
        """     
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='server.log',
                            filemode='w')        
        
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)        
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')        
        console.setFormatter(formatter)        
        logging.getLogger('').addHandler(console)

        self.server_log =  logging.getLogger(self.__class__.__name__)
    
        
        
        #do not change internal variables    
        self._port = server_port
        self.server_key = server_private_key_path
        self.server_key_password = server_key_password
        self.server_cert = server_cert_path
        self.client_pub_key = client_pub_key
    

    def get_protocol_state(self):
        """
            Return: string

            This function returns the current protocol state: 
            START, CHALLENGE, RESPONSE, SUCCESS, END, ABORT.
            
        """        
        return self.protocol_state
    
    def protocol_abort(self):
         self.server_log.info('Abort protocol intiated')
         self.protocol_state = 'ABORT'
         exit()
         

    def get_new_challenge(self):
        """
         Return: string
         
         This function should generate a challenge (encoded as a string) to send to the client.          
        """
        return  bytes.hex(b'01'*16)
    
    def process_client_msg(self, sconn):
        """
        sconn: socket wrapper between client and server                
        
        Return: nothing
        """       

        while True:
            """
                The input consists of two fields: type and message. 
                The type field can take on four possible values:
                CHALLENGE, RESPONSE, SUCCESS, and SESSION_MESSAGE. 

            """                
            data = sconn.recv()
            try:

                recv_msg = pickle.loads(data)
            except:
                self.server_log.info('connection closed')     
                self.protocol_abort()   

            if recv_msg['type'] == Message.RESPONSE:
                if self.protocol_state != 'CHALLENGE':
                    self.protocol_abort()
                    break
                
                #TODO: check challenge response
                response_correct = True

                if response_correct:
                    self.protocol_state = 'SUCCESS'
                    msg = pickle.dumps({"type":Message.SUCCESS, 'msg':None})
                    sconn.send(msg)
                else:
                    self.protocol_state = 'ABORT'
                    self.protocol_abort()
                    break
                                    

                
            elif recv_msg['type'] == Message.SESSION_MESSAGE:                  
                    if self.protocol_state != 'SUCCESS':
                        self.protocol_abort()

                    #echo meesage back
                    message = recv_msg['msg']
                    self.server_log.info("Ping msg [%s]" % message.decode())
                    msg = pickle.dumps({"type":Message.SESSION_MESSAGE, 'msg':message})
                    sconn.send(msg)
                    self.protocol_abort()
                    break
                
                    


    def on_connect(self, sconn):     
        """
         sconn: socket wrapper between client and server
         
         Return: nothing
        """
        # TODO: check challenge response
        self.challenge = self.get_new_challenge()
        self.server_log.info('generated challenge: [%s] ' % self.challenge)

        self.protocol_state = 'CHALLENGE'
        
        msg = pickle.dumps({"type":Message.CHALLENGE, 'msg':self.challenge})         
        sconn.send(msg)

        self.server_log.info('sent challenge to client')
        self.process_client_msg(sconn)

    def server_thread(self, port):
        """
         port: server port to start a thread to accept client connection
         
         Return: nothing
        """        

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)       
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        try:
         
            s.bind(("localhost", port))      
            self.server_log.info("Listening on port %d" % port)     
            s.listen(1)          
            
            # TODO: provide values     
            server_ssl_options ={'certfile': None,
                                'keyfile': None,  
                                'password': None}
            
            if server_ssl_options['certfile']:            
                secure_socket = context.wrap_socket(s, server_side=True)         
                context.load_cert_chain(**server_ssl_options)
            else:    
                # when we don't have the TSL setup
                self.server_log.warning("Initiated Insecure Communication")
                secure_socket = s


            while True:
                conn, address = secure_socket.accept()      
                self.server_log.info("Accepted a connection from %s..." % (address,))

                self.protocol_state = None

                self.server_log.info('Received client connection')

                sconn = Conn(conn, server=True, verbose = True) 
                
                # Start a new thread per connection
                threading.Thread(target=self.on_connect,
                                    kwargs={'sconn': sconn}).start()            
        except socket.error as e:            
            self.server_log.info("Port %d not available [%s]" % port, e )
         
    def start(self):
        """
        starts a server thread the server listens to self._port

        Return: nothing
        """
        # Start a new thread to accept client connection
        threading.Thread(daemon=True, 
                               target=self.server_thread(self._port)).start()
   
        
        


  

def main(argv):
    port=1337
    try:
        opts, args = getopt.getopt(argv,"hp:",["port="])
    except getopt.GetoptError:
        print('server.py -port <port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('server.py -port <port>')
            sys.exit()
        elif opt in ("-p", "--port"):
            if arg:
                port = int(arg)

    welcome_msg= pyfiglet.figlet_format("Welcome to EECS 3482 A Net", font = "digital" )
    print(welcome_msg)
    Server('None',
                None,
                None,
                None,
                port).start()
if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:                
        print("\nDone!")
        exit()

