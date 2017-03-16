import re   #regular expresion
import datetime as dt, time as tm

def split_request(request):
	r = request['request'].split()
	endpoint = r[1]
	m = re.compile(r'\/.+\.html')
	endpoint = m.match(endpoint)
	return {
		'request': r[0],
		'endpoint': endpoint.group(0),
		'protocol': r[2]
		}

def get_status(request):
	return request['status']

def convert_mylist(lines):
	parts = [
	    r'\S+',                   							# host %h
	    r'\S+',                             				# indent %l (unused)
	    r'\S+',			                   				 	# user %u
	    r'\[(?P<datetime>.+):[0-9]{2}\s\+[0-9]{4}\]',    	# time %t
	    r'"(?P<request>.+)"',       						# request "%r"
	    r'(?P<status>[0-9]+)',              				# status %>s
	    r'\S+',                   							# size %b (careful, can be '-')
	    r'".*"',               								# referer "%{Referer}i"
	    r'".*"',                 							# user agent "%{User-agent}i"
	]
	pattern = re.compile(r'\s+'.join(parts) + r'\s*\Z')

	#let's make our input list
	mylist = list()
	for line in lines:
		m = pattern.match(line)
		if m:
			mylist.append(m.groupdict())
	return mylist

## param: datetime - log string datetime
## retrun datetime object ex: 2017-02-22 18:45:00
def datetime_convert(request):
	r = request if type(request) == str else request['datetime']
	r = dt.datetime.strptime(r, '%d/%b/%Y:%H:%M')
	return r 

## param: datetime - converted datetime
## retrun string ex: 2017-02-22T18:45
def datetime_encode(datetime):
	return str(datetime).replace(" ", "T")

## param: string ex: 2017-02-22T18:45
## retrun datetime object ex: 2017-02-22 18:45:00
def datetime_decode(dtime):
	if type(dtime) == str:
		if "T" in dtime:
			dtime = dtime.replace("T", " ")+":00"
	else:
		dtime = str(dtime)
	r =  dt.datetime.strptime(dtime, '%Y-%m-%d %H:%M:%S')
	return r

def filter_by_date(mylist, start, end, interval):
	mylist = sorted(mylist, key=lambda x: (datetime_convert(x), x['request'])) # sort by date
	start = datetime_decode(
				datetime_convert(mylist[0]['datetime']) 
				if start == None else start
			)
	end = datetime_decode(
				datetime_convert(mylist[len(mylist)-1]['datetime']) \
				if end == None else end
				)
	def filter_my_data(x):
		if datetime_convert(x) >= datetime_decode(start) \
			and datetime_convert(x) <= datetime_decode(end):
				x['request'] = split_request(x)['endpoint']
				x['datetime'] = datetime_encode(dt.datetime.strptime(x['datetime'], '%d/%b/%Y:%H:%M'))[:-3]
				return x

	newlist = filter(None, [map(lambda x: filter_my_data(x), mylist)][0])
	return newlist