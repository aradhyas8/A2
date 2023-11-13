# EECS3482: Introduction to Computer Security

## Assignment 2: TLS

You're presented with a simple client/sever  application.


### Files

* server.py - server app
* client.py  - client app
* lib folder - includes helper function to facilitate communication 
* data folder - contains keys
	- rootCA.pem : root certificate (password: eecs3482)
	- server.key : server private key
	- server.pem : server certificate (password: eecs3482server)
	- client_priv_key.pem: client private key 
	- client_pub_key.pem : client public key
	 

### Set-up

To install all the relevant packages run:

* make clean
* make




## Instructions 

### Server app
To run a server in a  terminal run 
	* make server
	or (without make)
	*  python3 server.py –p [port #]

### Client app
*  client.py is client app 
    *  To run a client: make client
    *   or python3 client.py –p [port #]













