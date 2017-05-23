#This is a watchdog on some cloud instance (preferably close to the origin server); can also be placed at the origin.
#It constantly checks for connection with user_server (e.g., by pinging it).
#If user_server is under heavy load / attack, the watchdog will wake up the cloud servers.


import sys
import socket
import threading
import SocketServer
from time import sleep
from random import randint
import ping
import ec2_agent



SELF_IP_ADDR = 'localhost'
SELF_TCP_PORT = 0 # Port 0 means to select an arbitrary unused port
TO_PING = "www.bbc.co.uk", "www.yahoo.com", "www.facebook.com" # some random urls to ping from origin
MAX_TIMEOUTS = 2 #how many of the above pings may result in timeout
TIMEOUT_RETRIES = 0 #times to retry in case of a timeout
PING_UPPER_DELAY_RATIO = 0.5 # number of times to take initial ping result to set a "heavy load" threshold
LOWSLEEP = 3 # min num of seconds to sleep between latency checks
HIGHSLEEP = 6 # max num of seconds to sleep between latency checks

# client file as parsed from apache server's logs; should contain clients' ip addresses
CLIENT_FILE_PATH = "/var/log/apache2/clients.log"
#CLIENT_FILE_PATH = "c:\\temp\\clients.log"
TAKE_N_LAST_CLIENTS = 200 # look at this number of clients in the log file above


class Watchdog():

    heavyLoad = False

    def __init__(self):
        print "Initializing Watchdog"

        
    def expPing(self, urlsToPing):
        delay = 0
        timeouts = 0
        for url in urlsToPing:
            try:
                response = ping.Ping(url, timeout=5000).do() #result in msec
            except socket.error as e:
                print "Ping Error: ", e, ", exiting"
                exit
            except:
                print "Ping Error, exiting"
                exit
            if (response == "Request timed out."):
                timeouts += 1
                continue
            else:
                delay += response
            
        return delay, timeouts


    def checkLatency(self, urlsToPing):
        gotTimeouts = 0
        for tries in range (0, TIMEOUT_RETRIES+1):
            try: gotLatency, gotTimeouts = self.expPing(urlsToPing) #simplification: url's still not cached, will provide a good upper limit for delay. can modify to get a better estimation (e.g., as RTO calculation in TCP)
            except socket.error as e:
                print("Initial Ping Error:", e)
                gotTimeouts += 1;
            except:
                print("Ping exception")
                gotTimeouts += 1;
            if (gotTimeouts > MAX_TIMEOUTS):
                print "Got ", gotTimeouts, " timeouts"
                continue
            expectedLatency = PING_UPPER_DELAY_RATIO * gotLatency
            print "\nexpected upper latency limit: ", expectedLatency, "\n"
            break #no timeouts

        if (gotTimeouts > MAX_TIMEOUTS):
            print "Too many timeouts, assuming origin is under heavy load"
            return True
        
        #now check again every now and then and compare
        measuredLatency = 0
        while(measuredLatency <= expectedLatency and gotTimeouts <= MAX_TIMEOUTS):
            timeToSleep = randint(LOWSLEEP, HIGHSLEEP)
            print "checkLatency: Sleeping for ", timeToSleep, " seconds"
            sleep(timeToSleep)
            try: measuredLatency, measuredTimeouts = self.expPing(urlsToPing)
            except socket.error as e:
                print "Ping Error:", e
                gotTimeouts += 1
                continue
            gotTimeouts = 0
            print "Measured new latency: ", measuredLatency, " Timeouts: ", measuredTimeouts
        print "Exceeded Heavy Load threshold"
        self.heavyLoad = True
        return True
    

    def loadWatcher(self):

        print "Running Load Watcher"
        self.checkLatency(TO_PING) # checkLatency is a blocking function, only returns on True
        print "Heavy Load detected"
        ec2_agent1 = ec2_agent.EC2Agent()
        self.cloudNodesInitWakeUp(ec2_agent1)
        # now check load on each Cloud Server
        self.heavyLoad = False
        threads = []
        cur_ip = []
        for i in range(len(ec2_agent1.workingCloudServersIP)):
            del cur_ip[:]
            cur_ip.append(ec2_agent1.workingCloudServersIP[i])
            print "Pinging ", cur_ip[0]
            t = threading.Thread(target=self.checkLatency, args=(cur_ip,))
            t.daemon = False
            threads.append(t)
            print "Starting Cloud Load Watcher Thread ", i
            t.start()
        if (self.heavyLoad == True):
            print "Cloud Server experiences heavy load!"
        


    def cloudNodesInitWakeUp(self, ec2_agent1):
        fname = CLIENT_FILE_PATH
        #get only up to TAKE_N_LAST_CLIENTS last elements of the client ip list, then make a set
        with open(fname) as logfile:
            content = logfile.readlines()
            last_n = min(len(content), TAKE_N_LAST_CLIENTS)
            latestClients = content[-last_n:]
            latestClientsStripped = map(str.strip, latestClients)
            activeClientsSet = set(latestClientsStripped)
            activeClientsList = list(activeClientsSet)
            #remove blank elements
            while '' in activeClientsList:
                activeClientsList.remove('')
            print activeClientsList
        ec2_agent1.cloudNodesInitWakeUp(activeClientsList)
        print "Cloud Nodes Awoken:"
        for item in ec2_agent1.workingCloudServersIP:
            print item
        return ec2_agent1


        


if __name__ == "__main__":
    

    # Create a watchdog
    watchdog = Watchdog()

    # Start a thread for loadWatcher
    loadWatcherThread = threading.Thread(target=watchdog.loadWatcher)
    loadWatcherThread.daemon = False
    loadWatcherThread.start()
    print "Watchdog loadWatcher running in thread:", loadWatcherThread.name
    



