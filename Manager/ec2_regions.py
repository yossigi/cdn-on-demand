
ACCESS_KEY_ID = 'YOUR_KEY_ID'
SECRET_ACCESS_KEY = 'YOUR_ACCESS_KEY'
INSTANCE_KEY_PATH = 'PATH_TO_YOUR_INSTANCE_KEY'

cloudServers = []

class cloudRegion():

    regionName = ""
    endpoint = ""
    aws_access_key_id = ""
    aws_secret_access_key = ""
    lastPublicIP = "0.0.0.0"
    keys = ""
    serverURL = ""

    def __init__(self, regionName = "", endpoint = "", lastPublicIP = "", keysLocation = "", serverURL = ""):
        self.regionName = regionName
        self.endpoint = endpoint
        self.lastPublicIP = lastPublicIP #last known public IP address
        self.keys = keysLocation
        self.serverURL = serverURL

    
#initial instances to open. Change this accordingly to your available cloud instances (e.g., fill dinamically by a script)
def init():

    Oregon = cloudRegion(regionName = "us-west-2", endpoint = "ec2.us-west-2.amazonaws.com", lastPublicIP = "THIS_INSTANCE_PUBLIC_IP", keysLocation = INSTANCE_KEY_PATH, serverURL = "oregon1.autocdn.org")
    Ireland = cloudRegion(regionName = "eu-west-1", endpoint = "ec2.eu-west-1.amazonaws.com", lastPublicIP = "THIS_INSTANCE_PUBLIC_IP", keysLocation = INSTANCE_KEY_PATH, serverURL = "ireland1.autocdn.org")
    NVirginia = cloudRegion(regionName = "us-east-1", endpoint = "ec2.us-east-1.amazonaws.com", lastPublicIP = "THIS_INSTANCE_PUBLIC_IP", keysLocation = INSTANCE_KEY_PATH, serverURL = "nvirginia.autocdn.org")
    NCalifornia = cloudRegion(regionName = "us-west-1", endpoint = "us-west-1.amazonaws.com", lastPublicIP = "THIS_INSTANCE_PUBLIC_IP", keysLocation = INSTANCE_KEY_PATH, serverURL = "ncalifornia1.autocdn.org")
    Singapore = cloudRegion(regionName = "ap-southeast-1", endpoint = "ap-southeast-1.amazonaws.com", lastPublicIP = "THIS_INSTANCE_PUBLIC_IP", keysLocation = INSTANCE_KEY_PATH, serverURL = "singapore1.autocdn.org")
    Tokyo = cloudRegion(regionName = "ap-northeast-1", endpoint = "ap-northeast-1.amazonaws.com", lastPublicIP = "THIS_INSTANCE_PUBLIC_IP", keysLocation = INSTANCE_KEY_PATH, serverURL = "tokyo1.autocdn.org")    
    Sydney = cloudRegion(regionName = "ap-southeast-2", endpoint = "ap-southeast-2.amazonaws.com", lastPublicIP = "THIS_INSTANCE_PUBLIC_IP", keysLocation = INSTANCE_KEY_PATH, serverURL = "sydney1.autocdn.org")
    SaoPaulo = cloudRegion(regionName = "sa-east-1", endpoint = "sa-east-1.amazonaws.com", lastPublicIP = "THIS_INSTANCE_PUBLIC_IP", keysLocation = INSTANCE_KEY_PATH, serverURL = "saopaulo.autocdn.org")

    cloudServers = [Oregon, Ireland, NVirginia, NCalifornia, Singapore, Tokyo, Sydney, SaoPaulo]
    
    return cloudServers
