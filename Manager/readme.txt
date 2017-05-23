CDN-on-Demand is demonstrated here using Python 2.7 on EC2. The code, consisting of several files, implements
a Manager server, and should be placed and operated from either the origin or a cloud server.
The internal documentation is rather self-explanatory; still, below are some guidelines for adapting
the code for your needs.

You’ll need to get an AWS key pair and key pair(s) for your instances, and place them - or refer to
them - in ec2_regions.py. The same file is dynamically filled to contain all instances registered
to you (not necessarily active instances). In ec2_agent.py, you control several additional
parameters, such as the maximum allowed number of active instances; you can also issue initial
commands to the instances of your choice. Also, select the geoip_distance file according to your OS.
Cloud_watchdog.py implements the main command and control functions of a watchdog; several
configuration variables should be set here. Finally, ping.py implements a ping function and should
be run with administrator privileges.