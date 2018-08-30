#!/usr/bin/python
import requests
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),'settings.ini'))

#Get Tenable credentials 
Tenable_Client_Id = Config.get('Settings', 'Tenable_Client_Id')
Tenable_Secret_Id = Config.get('Settings', 'Tenable_Secret_Id')

targets = ['0.0.0.0'] #Fill out the targets to be serached

Target_Group_ID = {}
Target_Group = {}

#Santize IP
def sanitize_ip(ip):
	numbers = ip.split('.')
	if len(numbers) == 4:
		for i in numbers:
			try:
				if not (int(i) >= 0 and int(i) < 256):
					print 'ERROR: ' + ip + ' is not a valid IP address'
					return False
			except Exception, e:
				if 'invalid literal for int()' in e.message:
					print 'ERROR: ' + ip + ' is not an IP address'
					return False
	else:
		return False

	if ip == '0.0.0.0':
		return False
	elif ip == '255.255.255.255':
		return False
	
	return True

def main():
	targets = raw_input("Enter IPs (Eg: 125.23.56.34,56.45.254.254): ")
	targets = targets.split(',')    
	headers = {'X-ApiKeys':'accessKey=' + Tenable_Client_Id + '; secretKey=' + Tenable_Secret_Id,'Content-Type':'application/json'}
	r = requests.get("https://cloud.tenable.com/target-groups",headers=headers)
	response = r.json()
    
	for target in response['target_groups']:
		Target_Group_ID[target["name"]] = target["id"]
        	Target_Group[target["name"]] = (target["members"]).encode('utf-8').split(', ')
   
    	for group in Target_Group:
        	for target in targets:
			if sanitize_ip(target):
				target = target.split('.')
				count = 0
				for i in target:
					target[count] = int(i)
					count = count + 1
				target = '.'.join(['%s' % str(i) for i in target])

		    		if target in Target_Group[group]:
		        		print target + "---->" + group

if __name__ == "__main__":
    main()
