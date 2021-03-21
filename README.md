# Key-Value-DB-with-state-based-Authentication
Simplified Redis like key-value DB using “socketserver” framework


###### Language: Python
###### Framework: socketserver


### Motivation:
    Developed a part of 4th year assigment as a part of key-value pair based assignment.
    Work involved developing a architecture has a simple yet efficient login implementation.
        
    Objective was to develop an application that efficiently use OOP paradime.



### Problem Statement:
    Implement a TCP-based key-value store. The server implements the key-value store and clients make use of it. 
    The server must accept clients’ connections and serve their requests for ‘get’ and ‘put’ key value pairs.
        
    All key-value pairs should be stored by the server only in memory. Keys and values are strings.
    The client accepts a variable no of command line arguments where the first argument is the server hostname
    followed by port no. It should be followed by any sequence of “get <key>” and/or “put <key> <value>”.


    The server should be running on a TCP port. The server should support multiple clients and maintain their key-value stores separately.
    Implement authorization so that only few clients having the role “manager” can access other’s key-value stores. 
    A user is assigned the “guest” role by default. The server can upgrade a “guest” user to a “manager” user. 


### Execution:
    # First execute the server. (server runs on port on port 9999)
    python auth_server.py

    # on a different terminal execute
    python client.py

    #NOTE: minimum python 3.9 required (use of "walrus operator") 


### References:
    https://docs.python.org/3/howto/sockets.html#socket-howto
    https://docs.python.org/3/library/socketserver.html#socketserver-tcpserver-example

