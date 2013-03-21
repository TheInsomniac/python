'''
A basic Homeseer control base class.

Usage:
 - import homeseer :
    hs = homeseer.HSConnect("IPADDRESS")
 - from homeseer import HSConnect
     hs = HSConnect("IPADDRESS")

Implemented functions
 - control:
        to control Homeseer interfaces
 - status:
        to display the current status interfaces

To do:
 - implement more robust control and status. Hopefully be able to manage entire HS
   setup from Python.
'''
__version__ = "0.4"

import requests
import sys
import os
import time
import lxml
from lxml import html


class HSConnect(object):

    ''' Homeseer base class.
    Requires the Homeseer base URL or IP address passed to init.
    such as "http://127.0.0.1" or "http://localhost"

    To control an HS device supporting on/off/dim then enter the following:

        On   :exec housecode on
        Off  :exec housecode off
        DDim :exec housecode ddim level (dims to absolute dim value)
        Dim  :exec housecode dim level (dims relative to current level)

        example :exec B10 ddim 10
                      exec B10 on

    To set the string of a device such as as virtual device supporting
    Play/Pause/Stop any other status bit enter the following:

        string housecode status_string

        example :string B10 Stopped
                      string B10 Connected

    To obtain the status of a Homeseer interface pass the interface name as the
    first argument. If your string has spaces be sure to enclose it in quotes
    such as "Motion Detectors". Homeseer IS case sensitive so keep this in mind.
    zwave is NOT equivalent to ZWave.

        example: ZWave
                      "Motion Detectors"
    '''

    def __init__(self, url):
        self.url = url

    def control(self, script_command, device_housecode, device_command, dim_level=''):
        '''To control an HS device supporting on/off/dim then enter the following:

        Init:
        hs = HSconnect("http://127.0.0.1")
        hs.control(exec, B10, on)

        On   :exec housecode on
        Off  :exec housecode off
        DDim :exec housecode ddim level (dims to absolute dim value)
        Dim  :exec housecode dim level (dims relative to current level)

        example :exec B10 ddim 10
                      exec B10 on

        To set the string of a device such as as virtual device supporting
        Play/Pause/Stop any other status bit enter the following:

        string housecode status_string

        example :string B10 Stopped
                      string B10 Connected
        '''

        if str.lower(script_command) == "exec":
            script_command = "execx10"
        elif str.lower(script_command) == "string":
            script_command = "setdevicestring"

        payload = {'devlist':'0','dev_value':'','devaction':'', \
        'delay_hours':'0', 'delay_minutes':'0','delay_seconds':'0','message':'', \
        'hosts':'','runscript':'Execute+Command','ref_page':'ctrl','scriptcmd': \
        '&hs.%s("%s","%s"%s)' % (script_command, device_housecode, \
                                                        device_command, dim_level)}
        url = self.url + "/elog"

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
            website = requests.get(url, timeout=2)
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

        return results

    def status(self, script_command):
        '''To obtain the status of a Homeseer interface pass the interface name as the
        first argument. If your string has spaces be sure to enclose it in quotes
        such as "Motion Detectors". Homeseer IS case sensitive so keep this in mind.
        zwave is NOT equivalent to ZWave.

        Init:
        hs = HSconnect("http://127.0.0.1")
        hs.status("ZWave")

        example: ZWave
                      "Motion Detectors"
        '''

        url = self.url + "/stat?location=" + script_command

        website = requests.get(url)
        tree = lxml.html.fromstring(website.content)
        website.close()
        ''' parse xpath and retrieve appropriate tables '''
        elements = tree.xpath("//td[contains(@class, 'table') and not (contains(@id, 'dx')) \
                              and not (contains(@class, 'tableheader')) \
                                  and not (contains(form/@name, 'statform')) \
                                      and not (contains(text(), 'Control'))]//text()[normalize-space()]")

        ''' strip all line feeds '''
        output = []
        for i in range(0, len(elements)):
            output.append(elements[i].strip())

        ''' function to split lists into chunks of (x) size '''
        def chunker(seq, size):
            return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

        '''call chunker function and output lists of 6 as that's how many rows Homeseer has.
         Return only the rows we want '''
        results = []
        for group in chunker(output, 6):
            results.append(group[0])
            results.append(group[2])
            results.append(group[5])

        return results

def main():

    ''' **** CHANGE THIS TO YOUR HOMESEER SERVER IP ADDRESS **** '''
    hs = HSConnect("http://192.168.10.102")
    ''' **** CHANGE THIS TO YOUR HOMESEER SERVER IP ADDRESS **** '''

    if len(sys.argv) == 1:
        ''' clear screen first '''
        os.system('cls' if os.name=='nt' else 'clear')
        print '''
        To control an HS device supporting on/off/dim then enter the following:

        On   :\thousecode on
        Off  :\thousecode off
        DDim :\thousecode ddim level (dims to absolute dim value)
        Dim  :\thousecode dim level (dims relative to current level)

        example :\tB10 ddim 10
        \t\tB10 on

        To set the string of a device such as as virtual device supporting
        Play/Pause/Stop any other status bit enter the following:

        string housecode status_string
        or
        s housecode status_string

        example :\tstring B10 Stopped
        \t\tsB10 Connected

        To obtain the status of a Homeseer interface pass the interface name as the
        first argument. If your string has spaces be sure to enclose it in quotes
        such as "Motion Detectors". Homeseer IS case sensitive so keep this in mind.
        zwave is NOT equivalent to ZWave.

        example: \t ZWave
        \t\t "Motion Detectors"

        ** DON'T FORGET TO CHANGE THE URL PARAMETER IN THE SCRIPT **
        ** TO MATCH THE IP ADDRESS OF YOUR HOMESEER SERVER        **
        '''
        sys.exit(0)

    def run_control(command):
        results = hs.control(command, device_housecode, device_command, dim_level)
        print '''
        Your string was    :\t%s
        Your housecode was :\t%s
        Your command was   :\t%s
        Your options were  :\t%s ''' \
            % (command, device_housecode, device_command, dim_level[1:])
        print ("Response : " + results)

    def run_status(command):
        results = hs.status(command)
        ''' clear screen first '''
        os.system('cls' if os.name=='nt' else 'clear')
        count = 0
        ''' iterate through list in 3s as this is the number of rows of data. Limit the second row
        "Name" to be no more than 35 characters + two ".." for proper screen formatting on
        an 80 row wide terminal '''
        for i in range(len(results)/3):
            print str(results[(count)]).ljust(20) +  \
                str(results[(count+1)][:35] + (results[(count+1)][35:] and '..')).ljust(39) \
                      + str(results[(count+2)])
            count += 3

    commandline = sys.argv[1]

    if 1 < len(commandline) <= 3:
        device_housecode = sys.argv[1]
        device_command = str.lower(sys.argv[2])
        if sys.argv[3:]:
            dim_level = ",%s" % (sys.argv[3])
        else:
            dim_level = ''
        run_control("exec")

    elif len(commandline) == 1 and commandline == 's':
        device_housecode = sys.argv[2]
        device_command = (sys.argv[3]).title()
        dim_level = ''
        run_control("string")

    elif sys.argv[2:3]:
        device_housecode = sys.argv[2]
        device_command = str.lower(sys.argv[3])
        if sys.argv[4:]:
            dim_level = ",%s" % (sys.argv[4])
        else:
            dim_level = ''
        run_control(commandline)

    else:
        interface = sys.argv[1]
        run_status(interface)

if __name__ == "__main__":
    main()