# Tenable.io python scripts
Python scripts to create and update Tennable.io Target groups; find target group from IP

Pre-requisite:
1. AWS account with console access (Access ID & Key) and appropriate permissions.
2. AWS-CLI installed & configured to use the Access ID & Key.
3. Python 2.7
4. Boto3 library (pip install boto3)
5. Tenable Access Key and Secret Key

Environment: Linux, OSX

Fill out settings.ini before running the python scripts

Assumption in Update_Target_Group_AWS.py: Target groups have the group name 'AWS <profile_name' where the profile name is taken from ~/.aws/credentials
