#!/usr/bin/env python
import requests
import lxml
from lxml import html
from sys import argv as cmd

''' Homeseer's IP address '''
url = "http://192.168.10.102"

''' Shouldn't need to be changed for most installations '''
stat = "/stat?location="

''' name of your "Interface" in Homeseer  or cmd[1] to supply the argument on the command
    line. If supplying from the command line and your string has spaces be sure to enclose it
    in quotes such as "Motion Detectors"
'''
#location = "ZWave"
location = cmd[1]

website = requests.get(url + stat + location)
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
