#https://docs.python.org/3/howto/sockets.html#socket-howto
#https://github.com/python/cpython/blob/3.8/Lib/socketserver.py
import socketserver

'''
    How the 'socketserver' framework was used:
        # Implemented "AuthTCPServer" which inherits code from "socketserver.ThreadingTCPServer"
            - overrided     "def get_request(self)"   <hotspot>
            - Implemented :
                "def auth(self, request)"                     -> returns privilage level and username 
                "def get_db(self,privilage_lvl, username)"    -> returns   (dictionary ,dictionary)     <one for reading other for writing>
                "def signup(self, username, passed, request)" -> creates a user/manager and returns the privilage level and username
                
        = explaination for data members in "__init__":
                "self.managers"        ->  Contains list of mangangers and their password as tuple. 
                                            (needed for authentication)
                "self.user"            ->  Containts list of users(those who are not managers).
                                            (needed for authentication)

                "self.db"              ->  maintains information given by clients.
                                            (its a dictionary of dictionary)

                                        dictionary
                                            key   -> username
                                            value -> dictionary
                                                        key   -> attribute name
                                                        value -> attribute value

                "guest_db"              -> needed to provide separate namespace if multiple guests are connected at same time.
                                           (an integer acts as identifier for each guest)

    ----------------------------------------------------------------------------------------------------------------------------------------------------------

        # Implemented "GET_PUT_TCPHandler" which inherits code form "socketserver.BaseRequestHandler"
            - overrided   "def handle(self)"        ->    everytime clientsocket sends data to server this code in this function handles it accepts it.
            - Implemented :
                " def GET(self, attr, view, username, privilage_lvl) ":
                                        ->   Every GET request calls this function
                                                TYPES OF GET REQUEST:
                                                    - GET __all__           => prints the whole dictionary that holds the data for users and managers.
                                                    - GET '[<username>]'    => prints the server.db[<username>]  i.e all attributes and values of <username>
                                                                                NOTE THAT '[]'BRACKETS ARE are part of query
                                                                                 i.e GET [priyanshu] is valid query
                                                    - GET <attibute_name>   => prints the attribute name stored by the client.


                                                WHAT "GET" FUNCTION DOES NOT DO?
                                                    - GET function does not allow manager to see a particular value. i.e GET  [priyanshu].place
                                                        if you ask why? 
                                                        because how can a mananger know what I have stored if he has not seen
                                                        the whole "server.db['priyanshu']" dictionary.


                " def PUT(self, attr, value, my_db_space)" :
                                        ->  write the key:value pair in the client's dictionary.

                                        WHAT "PUT" FUNCTION DOES NOT DO?
                                            - PUT function does not allow a client to write to other's memory space.



'''

class AuthTCPServer(socketserver.ThreadingTCPServer):
    guest_id = 0    #when a client connests as guest this id will separate the views of each guest

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        self.managers = []
        self.users = []
        self.db = {}            #  {<username1> : {attribute: value ...}  ,<username2> : {attribute: value ...} ...} 
        self.guest_db = {}


    def signup(self, username, passwd, request):
        confirmation_msg = "\nYou may start making GET and PUT requests\n"
        request.send(bytes("Make it a manager account(y/n)", "utf-8"))

        if str(request.recv(1024),"utf-8")=='y':
            self.managers.append((username, passwd))
            request.send(bytes("manager authenticated."+confirmation_msg, "utf-8"))
            return 0, username
        else:
            self.users.append((username, passwd))
            request.send(bytes("user authenticated."+confirmation_msg, "utf-8"))
            return 1, username


    def auth(self, request):
        confirmation_msg = "\nYou may start making GET and PUT requests."
        request.send(bytes("Enter the username (\"guest\" for temp. session):", "utf-8"))
        username = str(request.recv(1024),"utf-8")

        if username == "guest":
            request.send(bytes("Logging in as guest."+confirmation_msg, "utf-8"))
            AuthTCPServer.guest_id += 1
            return 2, "guest"

        request.send(bytes("Enter the password :", "utf-8"))
        passwd = str(request.recv(1024),"utf-8")

        if (username, passwd) in self.users:
            request.send(bytes("user authenticated."+confirmation_msg, "utf-8"))
            return 1, username

        if (username,passwd) in self.managers:
            request.send(bytes("manager authenticated."+confirmation_msg, "utf-8"))
            return 0, username

        
        #valid password check
        if username in map(lambda x: x[0], self.users) or username in map(lambda x:x[0], self.managers):
            request.send(bytes("Invalid Credentials\n", "utf-8"))
            return self.auth(request)

        request.send(bytes("Unknown username. Do you wish to signup(y/n)", "utf-8"))
        answer = str(request.recv(1024),"utf-8")
        if answer == 'y':
            return self.signup(username, passwd, request)
        
        #if client says no restart authentication process
        return self.auth(request)


    def get_request(self):
        clientsocket, address = self.socket.accept()
        print("Receiving from", address)
        return (clientsocket, address)


    def get_db(self,privilage_lvl, username):
        if username == "guest":
            self.guest_db[AuthTCPServer.guest_id] = {}
            return self.guest_db[AuthTCPServer.guest_id], self.guest_db[AuthTCPServer.guest_id]  #for guests updation of guest id is handled when a user logs in as guest. 
        
        if not username in self.db.keys():
            self.db[username] = {}

        if privilage_lvl == 0:
            return self.db, self.db[username] 

        if privilage_lvl == 1:
            return self.db[username] , self.db[username]

        raise Exception ("INVALID PRIVILAGE LEVEL")


class GET_PUT_TCPHandler(socketserver.BaseRequestHandler):
    def GET(self, attr, view, username, privilage_lvl):

        #display data of all users
        if attr == "__all__":
            self.request.send(bytes("server: " + ((attr + " = " +  str(server.db)) if privilage_lvl == 0 else "Unauthorised access"), "utf-8"))
            return

        #display all data of a particular user
        if attr[0] == '[' and attr[-1] == ']':
            self.request.send(bytes("server: " + ((attr + " = " + str(view.get(attr[1:-1],"User does not exist."))) if privilage_lvl == 0 else "Unauthorised access"), "utf-8"))
            return

        #display data of the the logged in user
        self.request.send(bytes("server: " + attr + " = " +  (view[username].get(attr, "<blank>") if privilage_lvl == 0 else view.get(attr,"<blank>")), "utf-8"))
        return
        

    def PUT(self, attr, value, my_db_space):
        my_db_space[attr] = value
        self.request.send(bytes("server: "+attr+" stored.", "utf-8"))


    def handle(self):
        privilage_lvl, username = server.auth(self.request)
        view, my_db_space = server.get_db(privilage_lvl, username)

        while (data := self.request.recv(1024)):
            received = (str(data,"utf-8"))
            args = received.split(' ')
            # print(args)
            print(f"{username}: '{received}'")

            if args[0].upper() == "GET":
                self.GET(args[1], view, username, privilage_lvl)

            if args[0].upper() == "PUT":
                self.PUT(args[1], args[2], my_db_space)

            if args[0].upper() != "GET" and args[0].upper() != "PUT":
                self.request.send(bytes("server:  INVALID REQUEST", "utf-8"))

        print(f"Queries processed for {username}")

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    with AuthTCPServer((HOST,PORT), GET_PUT_TCPHandler) as server:
        server.serve_forever()