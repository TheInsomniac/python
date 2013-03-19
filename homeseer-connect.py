#!/usr/bin/env python
import requests
import sys
import os
import time
import lxml
from lxml import html
#import re

''' ******** CHANGE ME TO YOUR HOMESEER IP ADDRESS ******** '''
#url = 'http://127.0.0.1'
url = 'http://192.168.10.102'
''' ******** CHANGE ME TO YOUR HOMESEER IP ADDRESS ******** '''

if len(sys.argv) == 1:
    #clear screen first
    os.system('cls' if os.name=='nt' else 'clear')
    print '''
    To control an HS device supporting on/off/dim then enter the following:

    On   :\texec housecode on
    Off  :\texec housecode off
    DDim :\texec housecode ddim level (dims to absolute dim value)
    Dim  :\texec housecode dim level (dims relative to current level)

    example :\texec B10 ddim 10
    \t\texec B10 on

    To set the string of a device such as as virtual device supporting
    Play/Pause/Stop any other status bit enter the following:

    string housecode status_string

    example :\tstring B10 Stopped
    \t\tstring B10 Connected

    ** DON'T FORGET TO CHANGE THE URL PARAMETER IN THE SCRIPT **
    ** TO MATCH THE IP ADDRESS OF YOUR HOMESEER SERVER        **
    '''
    sys.exit(0)

script_raw_command = str.lower(sys.argv[1])
device_housecode = sys.argv[2]
device_command = str.lower(sys.argv[3])

if sys.argv[4:]:
    x10 = ",%s" % (sys.argv[4])
else:
    x10 = ''

if script_raw_command == "exec":
    script_command = "execx10"
elif script_raw_command == "string":
    script_command = "setdevicestring"

payload = {'devlist':'0','dev_value':'','devaction':'', \
'delay_hours':'0', 'delay_minutes':'0','delay_seconds':'0','message':'', \
'hosts':'','runscript':'Execute+Command','ref_page':'ctrl','scriptcmd': \
'&hs.%s("%s","%s"%s)' % (script_command, device_housecode, \
                                                device_command, x10)}

''' send request to Homeseer '''
try:
    r = requests.post(url, data=payload, timeout=2)
except:
    print '''
    Could not connect to server. Check that Homeseer is running and that the ip
    address is correct.
    '''
    sys.exit(0)
#print r.text

''' wait 1 second before checking status as it takes a moment for HS to update '''
time.sleep(1)

''' Connect to Homeseer and open the log file. Way nicer than the regex but requires lxml.
if not using lxml "import re" above and comment out the tree, elements, and results line '''

try:
    website = requests.get(url + "/elog", timeout=2)
    tree = lxml.html.fromstring(website.content)
    ''' Search for the latest log entry '''
    elements = tree.xpath("//td[@class='LOGEntry0']")
    results = elements[0].text_content()
    website.close()
except:
    print '''
    Could not connect to server. Check that Homeseer is running and that the ip
    address is correct. Is your logfile unusually long??
    '''
    sys.exit(0)

''' Uncomment the below if using re instead of lxml:
Parse Homeseer's log file until it finds the newest LOGEntry then save the data and stop
reading. Finally close the connection. '''

#while True:
#    data = website.content
#    if re.search('(?<=LOGEntry0"><Font Color="#\d\d\d\d\d\d">)(.*?)<', data):
#        regexp = re.search('(?<=LOGEntry0"><Font Color="#\d\d\d\d\d\d">)(.*?)<',\
#                                        data)
#        break
#website.close()

print '''
Your string was    :\t%s
Your housecode was :\t%s
Your command was   :\t%s
Your options were  :\t%s ''' \
    % (script_raw_command, device_housecode, device_command, x10[1:])
#print ("Response : " + ''.join(regexp.groups())) # uncomment if using re instead of lxml
print ("Response : " + results) # comment out if using re instead of lxml
