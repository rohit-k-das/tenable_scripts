#!/usr/bin/python
import boto3
import requests
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),'settings.ini'))

#Get Tenable credentials 
Tenable_Client_Id = Config.get('Settings', 'Tenable_Client_Id')
Tenable_Secret_Id = Config.get('Settings', 'Tenable_Secret_Id')

Public_IP = []

def account(profile):
	session = boto3.session.Session(profile_name = profile)
	regions = session.get_available_regions('ec2')
        Account_Public_IPs = []

	for region in regions:
		client = session.client('ec2',region_name = region)
		response = client.describe_addresses()
	        Region_Public_IPs = publicIPs(client,response)
                Account_Public_IPs = Region_Public_IPs + Account_Public_IPs
        return Account_Public_IPs

def publicIPs(client,response):
	All_Elastic_IP = []
	Allocated_Elastic_IP = []
	Instance_Public_IP = []

		
	for address in response['Addresses']:
		All_Elastic_IP.append(address['PublicIp'])
		if 'NetworkInterfaceOwnerId' in address:
			Allocated_Elastic_IP.append(address['PublicIp'])
			Public_IP.append(address['PublicIp'])

	public_IP_instance = client.describe_instances()
	for instance in public_IP_instance['Reservations']:
		for address in instance['Instances']:
			if 'PublicIpAddress' in address:
				if address['PublicIpAddress'] not in Allocated_Elastic_IP:
				    Instance_Public_IP.append(address['PublicIpAddress'])
                                    Public_IP.append(address['PublicIpAddress'])
	
        return Allocated_Elastic_IP + Instance_Public_IP
		

def http_post(tenable_target_group,IPs):
    data = {}
    data['name'] = tenable_target_group
    data['members'] = str(','.join(IPs))
    data['type'] = 'system'
    data['acls'] = [{"type":"default","permissions":32},{"type":"group","permissions":64,"name":"Security","id":"3","owner":"0"}]
    headers = {'X-ApiKeys':'accessKey=' + Tenable_Client_Id + '; secretKey=' + Tenable_Secret_Id,'Content-Type':'application/json'}
    r = requests.post("https://cloud.tenable.com/target-groups",headers=headers,json=data)
    print r.status_code

#Get all AWS account profiles from aws credentials file
def get_profiles(cred_file):
    profiles = []
    try:
        with open(cred_file) as f:
            for line in f.readlines():
                if '[' in line:
                    line = line.replace('[','').replace(']','').strip('\n')
                    profiles.append(line)
    except Exception,e:
        print "Error:" +str(e)
    return profiles

#Get default home dir of user executing the script
def get_home_dir():
    current_user_id = os.getuid()
    with  open('/etc/passwd') as passwd_file:
        for line in passwd_file.readlines():
            field = line.split(':')
            if current_user_id == int(field[2]):
                home_dir = field[5]
    return home_dir

def main():
	IP_Not_Covered_Tenable = []
	Tenable_IP = []
	
	home_dir = get_home_dir()
	cred_file_path = home_dir + '/.aws/credentials'

	#Checks if aws credential file exists and get all AWS account profiles
	if os.path.exists(cred_file_path):
		profile_names = get_profiles(cred_file_path)
   	else:
		cred_file_path = raw_input("Please enter credential files absolute path: ")
		profile_names = get_profiles(cred_file_path)

	for profile in profile_names:
		tenable_target_group = 'AWS ' + profile.capitalize()
                AWS_Public_IPs = account(profile)
                http_post(tenable_target_group,AWS_Public_IPs)


if __name__ == "__main__":
	main()

