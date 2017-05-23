The source code in this directory implements the clientless secure-object mechanism.

First execute the EnbapsulateServerDir.py python script with parameters indicating 
the website's object directory and private key file (used to sign the objects). The script 
will create a new directory called "enc" with the files in encapsulated form. These files 
should be stored for distribution on the CDN.

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