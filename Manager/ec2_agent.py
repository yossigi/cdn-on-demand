import boto
import boto.ec2
import paramiko # for ssh
import time
import os
import ec2_regions
import socket
import sys
import collections

#import geoip_distance_win # for linux use the other file
import geoip_distance_lin

SERVERS_HIGH_BOUND = 4 #maximum number of servers to open
MIN_REQS_TO_OPEN_SRV = 5 #minimum clients for a server needed to open that server

servers_filename = "/var/www/files/servers.txt" #path to a list of currently available servers

class EC2Agent():

    cloudServers = []
    workingCloudServersIP = []
    activeInstances = []
    requestedCloudServers = []
    requestedCloudServersNames = []
    
    def __init__(self):
        self.cloudServers = ec2_regions.init()
    
    def cloudNodesInitWakeUp(self, activeClientsSet):
        
        print "Active Clients: ", activeClientsSet
        for client in activeClientsSet:
            bestServer = self.calcIpDistance(client, self.cloudServers)
            print "Picked Cloud Server in region ", bestServer.regionName, "for client ", client
            self.requestedCloudServers.append(bestServer)
            self.requestedCloudServersNames.append(bestServer.regionName)
            

        counterRequestedServers=collections.Counter(self.requestedCloudServers)
        counterRequestedServersNames=collections.Counter(self.requestedCloudServersNames)
        print "Best matching servers are: ", counterRequestedServersNames
        mostCommonServers = counterRequestedServers.most_common(SERVERS_HIGH_BOUND)
        mostCommonServersNames = counterRequestedServersNames.most_common(SERVERS_HIGH_BOUND)
        print SERVERS_HIGH_BOUND, " most commonly requested servers: ", mostCommonServersNames
        print "Minimum clients needed to open: ", MIN_REQS_TO_OPEN_SRV
        for serverReq in mostCommonServers:
            if (serverReq[1] >= MIN_REQS_TO_OPEN_SRV):
                print "Opening server ", serverReq[0].regionName
                self.cloudNodeInitWakeUp(serverReq[0])
            

    def calcIpDistance(self, clientIp, cloudServers):
        minDistance = sys.maxint
        prevMinDistance = minDistance
        bestCloudServer = cloudServers[0]

        #GeoIpDistanceCalc = geoip_distance_win.GeoIpDistance() # for linux use the other file!
        GeoIpDistanceCalc = geoip_distance_lin.GeoIpDistance()
        
        for cloudServer in cloudServers:
            minDistance = min(minDistance, GeoIpDistanceCalc.calcDistance(clientIp, cloudServer.lastPublicIP))
            if (minDistance < prevMinDistance):
                bestCloudServer = cloudServer
                prevMinDistance = minDistance
        return bestCloudServer

    
    def cloudNodeInitWakeUp(self, cloudToWake):
        print "Waking up cloud servers"
        if (cloudToWake in self.activeInstances):
            print "This cloud server is already active"
            return
        
        print "Looking in Region ", cloudToWake.regionName
        region = boto.ec2.regioninfo.RegionInfo(name = cloudToWake.regionName, endpoint = cloudToWake.endpoint)
        conn = boto.ec2.connect_to_region(region.name, aws_access_key_id=ec2_regions.aws_access_key_id, aws_secret_access_key=ec2_regions.aws_secret_access_key)

        #list reservations, each contain several instances
        reservations = conn.get_all_instances()
        #pick the first reservation
        instances = reservations[0].instances
        #start the first instance from the first reservation
        instance = instances[0]
        print "Starting CloudServer ", instance, " in region ", region
        conn.start_instances([instance.id])

        #update the current state of the instance
        #time.sleep(10)
        instance.update()
        #examine the instance's parameters
        state = instance.state
        wasAsleep = False
        if (state != "running"):
            wasAsleep = True
        print "CloudServer state: ", state
        while (state != "running"):
            print "Waiting till CloudServer is up"
            time.sleep(5)
            instance.update()
            state = instance.state

        print "CloudServer is up"
        
        if (cloudToWake not in self.activeInstances):
            self.activeInstances.append(cloudToWake)
            #now update servers file so that clients could use the new server
            servers_file = open(servers_filename, 'w')
            for item in self.activeInstances:
                servers_file.write("http://%s\n" % item.serverURL)
            servers_file.close()
                
            
        ip_address = instance.ip_address
        print "CloudServer ip_address: ", ip_address
        if ip_address not in self.workingCloudServersIP:
            self.workingCloudServersIP.append(ip_address)

        #connecting to instance using paramiko's SSH:
        if (wasAsleep == True):
            time.sleep(10) #if the server has just finished waking up, need to wait some time before trying to connect
        print "Connecting to %s as user %s" % (instance.ip_address, 'ubuntu')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(instance.ip_address, username='ubuntu', key_filename=os.path.expanduser(cloudToWake.keys))
                
        #just to check sending commands to instance through SSH:
        print "Testing connection: "
        stdin, stdout, stderr = ssh.exec_command("uptime")
        stdin.flush()
        data = stdout.read().splitlines()
        for line in data:
            print line

        #close the testing ssh for now.
        print "Closing connection"
        ssh.close



    def to_num(self, addr):
        #parse the address string into integer quads
        quads = map(ord, socket.inet_aton(addr))
        #spread the quads out 
        return reduce(lambda x,y: x * 0x10000 + y, quads)

    def distance(self, a, b):
        
        def to_num(addr):
            # parse the address string into integer quads
            quads = map(ord, socket.inet_aton(addr))
            # spread the quads out 
            return reduce(lambda x,y: x * 0x10000 + y, quads)
        
        return abs(to_num(a) - to_num(b))



