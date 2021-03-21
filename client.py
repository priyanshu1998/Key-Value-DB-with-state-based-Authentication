import socket
import sys

def main(args):
    HOST, PORT = "localhost", 9999  

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))                  #think of it as connect request
        print(sock.recv(1024).decode())                      #think of it as a response to it.
        while (data := input()).upper() != "EXIT":          #last second hack to avoid broken pipes  
            sock.send(bytes(data, "utf-8"))                  #request
            print(sock.recv(1024).decode())                  #response
        sock.send(b"")
       
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))