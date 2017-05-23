#This product includes GeoLite2 data created by MaxMind, available from <a href="http://www.maxmind.com">http://www.maxmind.com</a>.

#This code is for python running under linux. For windows, use other file!
import GeoIP

import geopy
import geopy.distance


class GeoIpDistance():
    
    def calcDistance(self, ipAddr1, ipAddr2):

        gi = GeoIP.open("GeoLiteCity.dat", GeoIP.GEOIP_INDEX_CACHE | GeoIP.GEOIP_CHECK_CACHE)
        #gi = GeoIP("c:\\temp\\GeoLiteCity.dat")
        gir1 = gi.record_by_name(ipAddr1)
        gir2 = gi.record_by_name(ipAddr2)
        #Calculate distance
        #print "Calculating Distance between IP ", ipAddr1, " and IP ", ipAddr2
        pt1 = geopy.Point(gir1['latitude'], gir1['longitude'])
        pt2 = geopy.Point(gir2['latitude'], gir2['longitude'])
        #print "Distance:"
        dist1 = geopy.distance.distance(pt1, pt2).km
        #print dist1
        return dist1






