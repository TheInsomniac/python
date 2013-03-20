#!/usr/bin/env python
import requests
import sys
import os
import time
import lxml
from lxml import html

''' **** CHANGE THIS TO YOUR HOMESEER SERVER IP ADDRESS **** '''
base_url = "http://192.168.10.102"
''' **** CHANGE THIS TO YOUR HOMESEER SERVER IP ADDRESS **** '''

class Homeseer(object):

    def __init__(self, url):
        self.url = url

    def control(self, script_command, device_housecode, device_command, dim_level):
        payload = {'devlist':'0','dev_value':'','devaction':'', \
        'delay_hours':'0', 'delay_minutes':'0','delay_seconds':'0','message':'', \
        'hosts':'','runscript':'Execute+Command','ref_page':'ctrl','scriptcmd': \
        '&hs.%s("%s","%s"%s)' % (script_command, device_housecode, \
                                                        device_command, dim_level)}
        try:
            r = requests.post(self.url, data=payload, timeout=2)
        except:
            print " \
                    Could not connect to server. Check that Homeseer is running and that the ip \
                    address is correct."
            sys.exit(0)

        ''' wait 1 second before checking status as it takes a moment for HS to update '''
        time.sleep(1)

        ''' Connect to Homeseer and open the log file. '''
        try:
            website = requests.get(self.url, timeout=2)
            tree = lxml.html.fromstring(website.content)
            ''' Search for the latest log entry '''
            elements = tree.xpath("//td[@class='LOGEntry0']")
            results = elements[0].text_content()
            website.close()
        except:
            print "\
                    Could not connect to server. Check that Homeseer is running and that the ip \
                    address is correct. Is your logfile unusually long?? "
            sys.exit(0)

        print '''
        Your string was    :\t%s
        Your housecode was :\t%s
        Your command was   :\t%s
        Your options were  :\t%s ''' \
            % (script_raw_command, device_housecode, device_command, dim_level[1:])
        print ("Response : " + results)

    def status(self):
        website = requests.get(self.url)
        tree = lxml.html.fromstring(website.content)
        website.close()
        elements_name = tree.xpath("//td[starts-with(@class, 'tablerow')]")
        elements_status = tree.xpath("//td[starts-with(@id, 'dv')]")
        output_name = []
        output_status = []

        for i in range(0, len(elements_name)-1):
            output_name.append(elements_name[i].text_content().strip())

        for i in range(0, len(elements_status)):
            output_status.append(elements_status[i].text_content().strip())

        output_name = filter(None, output_name)
        output_name = [output_name for output_name in output_name if output_name != \
                 "0%10%20%30%40%50%60%70%80%90%100%"]

        def chunker(seq, size):
            return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

        devices = []
        for group in chunker(output_name, 5):
            devices.append(group[1:-3])

        count = 0
        for sublist in devices:
            sublist.insert(0, output_status[count])
            count += 1

        status_output = [item for sublist in devices for item in sublist]
        for group in chunker(status_output, 2):
            print ' ==> '.join(group)

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

    To obtain the status of a Homeseer interface pass the interface name as the
    first argument. If your string has spaces be sure to enclose it in quotes
    such as "Motion Detectors"

    example: \t ZWave
    \t\t "Motion Detectors"

    ** DON'T FORGET TO CHANGE THE URL PARAMETER IN THE SCRIPT **
    ** TO MATCH THE IP ADDRESS OF YOUR HOMESEER SERVER        **
    '''
    sys.exit(0)

script_raw_command = str.lower(sys.argv[1])

if sys.argv[2:3]:
    device_housecode = sys.argv[2]
    device_command = str.lower(sys.argv[3])

if sys.argv[4:]:
    dim_level = ",%s" % (sys.argv[4])
else:
    dim_level = ''

if script_raw_command == "exec":
    script_command = "execx10"
elif script_raw_command == "string":
    script_command = "setdevicestring"
else:
    script_command = script_raw_command

if script_command == "execx10" or script_command == "setdevicestring":
    hscontrol = Homeseer(base_url + "/elog")
    hscontrol = hscontrol.control(script_command, device_housecode, \
                                                device_command, dim_level)
    sys.exit(0)
else:
    hsstatus = Homeseer(base_url + "/stat?location=" + script_command)
    hstatus = hsstatus.status()
    sys.exit(0)
