from flask import Flask, render_template, request, jsonify
import subprocess
from socket import *
import time
import io
import sys
from contextlib import redirect_stdout

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_pinger', methods=['POST'])
def run_pinger():
    result = run_function(pinger)
    return jsonify({'result': result})

@app.route('/run_port_scanner', methods=['POST'])
def run_port_scanner():
    result = run_function(portScanner)
    return jsonify({'result': result})

def run_function(func):
    output = io.StringIO()
    with redirect_stdout(output):
        func()
    return output.getvalue()

def pinger():
    serverIP ="127.0.0.1"
    serverPort = 12345
    clientSocket=socket(AF_INET,SOCK_DGRAM) #Creating Client UDP Socket
    rtts=[] #RTTs array to save every RTT and do the statstics
    lost=0 #Accumlator for the lost requests to calculate Loss Rate
    for i in range(1,11): #range(start default=0,end+1,step default=1)
        pingMsg = f"Ping {i} {time.ctime()}" #Message format as Specified, ctime() -> prints current time
        start = time.process_time()  #Start timer before sending ping message to calculate RTT
        clientSocket.sendto(pingMsg.encode(),(serverIP,serverPort))
        try:
            clientSocket.settimeout(1) #Set socket time out to 1 sec, if no operation happened during this period
                #it will raise timeOut exception,it applies to a single call to socket read/write operation.
            serverResponse, serverAddress = clientSocket.recvfrom(1024)
            end = time.process_time()
            rtt = end - start #Calculating RTT
            print(f"Server Responded with {serverResponse.decode()} taking {rtt} seconds")
            rtts.append(rtt)
            clientSocket.settimeout(None) #Removing timeOut as the server already responded
        except timeout:
            lost+=1
            print("Request Timed Out!")

    print(f"\nMinimum RTT: {min(rtts)}")
    print(f"Maximum RTT: {max(rtts)}")
    print(f"Average RTT: {sum(rtts)/len(rtts)}")
    print(f"Packet Loss Rate: {lost/10*100}%") #10 --> # of Packets

def portScanner():
    serverIP ="127.0.0.1"
    for i in range(1,25024):
        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.connect((serverIP, i))
            print("Connection successful on port" + str(i))
        except error as e:
            pass
if __name__ == '__main__':
    app.run(debug=True,port=8080)
