The repo contains four separate folders: one for each of CDN-on-Demand's entities (see paper).
The Origin provides an example of content in the origin.


The implementation of the clientless secure-object mechanism is in divided into two:
1. the origin gateway contains the encapsulation mechanism
First execute the EnbapsulateServerDir.py python script with parameters indicating
the website's object directory and private key file (used to sign the objects). The script
will create a new directory called "enc" with the files in encapsulated form. These files
should be stored for distribution on the CDN.

2. the origin contains the root.js which the client uses to decapsulate.
In order to display a web-page, the client retrieves the encapsulated objects embedded
in that page from the CDN (e.g., HTML and CSS files, images and videos). Decapsulation
of these objects and construction of the page is performed at the client-side, by a
JavaScript which we name the Root JavaScript (RJS). RJS works as follows: given a web-page's
URI, RJS retrieves it from the CDN, decapsulates and presents it to the user. Next, RJS
retrieves and decapsulates the objects embedded in that page from the CDN (e.g., images)
and uses their rendering information to display them on the page (objects on the same page
are fetched simultaneously). While loading the fetched objects, RJS validates their authenticity.

In order to use the RJS, update your public key and CDN address in the script and update
the server's public key in the root.js file. Then import root.js in your homepage file, which should
be otherwise empty (see www folder in the example directory).

Managers:
CDN-on-Demand is demonstrated here using Python 2.7 on EC2. The code, consisting of several files, implements
a Watchdog server, and should be placed and operated from either the origin or a cloud server.
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

Proxy folder:
Place here the encapsulated files and deploy on your proxy machines.

