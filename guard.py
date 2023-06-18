import re
import os
import subprocess

	
def app():
	ips = {}

	for line in open('/var/log/apache2/access.log'):
		m = re.match('^(\d+.\d+.\d+.\d+) - - (\[\d+/.+/\d+:\d+:\d+:\d+ \+\d+\])', line)

		if m:
			ip = m.group(1)
			date = m.group(2)

			if ip in ips.keys():
				if date in ips[ip].keys():
					ips[ip][date] = ips[ip][date] + 1
				else:
					ips[ip].update({date : 0})
			else:
				ips.update({ip : {date : 0}})


	return ips

		



	
