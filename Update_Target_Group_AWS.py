#!/usr/bin/python
import requests
import boto3
import json
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),'settings.ini'))

#Get Tenable credentials 
Tenable_Client_Id = Config.get('Settings', 'Tenable_Client_Id')
Tenable_Secret_Id = Config.get('Settings', 'Tenable_Secret_Id')

Public_IP = []
AWS_Target_Group_ID = {}
AWS_Target_Group = {}

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


def load_AWS_Target_Group():
    headers = {'X-ApiKeys':'accessKey=' + Tenable_Client_Id + '; secretKey=' + Tenable_Secret_Id,'Content-Type':'application/json'}

    r = requests.get("https://cloud.tenable.com/target-groups",headers=headers)
    response = r.json()

    for target in response['target_groups']:
        if 'AWS' in target["name"]:
            AWS_Target_Group_ID[target["name"]] = target["id"]
	    AWS_Target_Group[target["name"]] = (target["members"]).encode('utf-8').split(', ')

def http_put(ID,IPs,name):
    data = {}
    data['name'] = name
    data['members'] = str(','.join(IPs)) 
    data['type'] = 'system'
    data['acls'] = [{"type":"default","permissions":32},{"type":"group","permissions":64,"name":"Security","id":"3","owner":"0"}]
    headers = {'X-ApiKeys':'accessKey=' + Tenable_Client_Id + '; secretKey=' + Tenable_Secret_Id,'Content-Type':'application/json'}
    url = "https://cloud.tenable.com/target-groups/" + str(ID)
    r = requests.put(url,headers=headers,json=data)
    print ID
    print IPs
    print (r.status_code)
    print ID
    print

def main():
    home_dir = get_home_dir()
    cred_file_path = home_dir + '/.aws/credentials'

    #Checks if aws credential file exists and get all AWS account profiles
    if os.path.exists(cred_file_path):
        profile_names = get_profiles(cred_file_path)
    else:
        cred_file_path = raw_input("Please enter credential files absolute path: ")
        profile_names = get_profiles(cred_file_path)
    
    load_AWS_Target_Group()
    if len(AWS_Target_Group_ID) == 0:
        print "No AWS groups. Run create target group script"
        return
    
    for profile in profile_names:
                tenable_target_group = 'AWS ' + profile.capitalize()
                AWS_Public_IPs = account(profile)
                IP = []
		for address in AWS_Public_IPs:
		    if address not in AWS_Target_Group['AWS ' + profile.capitalize()]:
                        IP.append(address)
                        break
                if IP:
                    http_put(AWS_Target_Group_ID['AWS ' + profile.capitalize()], AWS_Public_IPs, tenable_target_group)

if __name__ == "__main__":
    main()
