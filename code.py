from flask import Flask, request, jsonify
from datetime import datetime
import time, random
import logging.handlers
from dateutil import parser
app=Flask(__name__)
methods=['GET', 'POST', 'PUT', 'DELETE']
zeros=[0,0,0]
global_dict={key: zeros.copy() for key in methods}
count=0

logging.basicConfig(filename='req.log', datefmt= '%Y-%m-%d %H:%M:%S',format='%(asctime)s %(message)s', filemode='a', level=logging.ERROR)
lgr=logging.getLogger('ReqLog')

@app.route('/process/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def hello_world():
    now=datetime.now()
    global global_dict,count
    count+=1
    global_dict[request.method][0]+=1
    dt=dict()
    dt['time']=now.strftime('%H:%M')
    dt['method']=request.method
    dt['headers']=dict(request.headers)
    dt['query_string']=dict(request.args.items())
    dt['body']=request.data.decode('utf-8')
    time.sleep(random.randrange(2,3))
    duration = datetime.now() - now
    dt['duration'] = duration.seconds
    global_dict[request.method][1]+=duration.seconds
    global_dict[request.method][2] = global_dict[request.method][1] / global_dict[request.method][0]
    lgr.error(str(request.method) + ' ' + str(dt['duration']))
    return jsonify(str(dt))

@app.route('/stats')
def statspath():
    st=''
    for k,v in global_dict.items():
        st+=k+'\nTotal req.s: '+str(v[0])+'\nAverage response time: '+str(v[2])+'\n\n'
    rq = open('req.log')
    lines=reversed(rq.readlines())
    stats_now=datetime.now()
    minute_dict={key: zeros.copy() for key in methods}
    hour_dict={key: zeros.copy() for key in methods}
    for i in lines:
        if (stats_now-datetime.strptime(str(i[:19]), '%Y-%m-%d %H:%M:%S')).seconds <60:
            minute_dict[i.split()[2]][0]+=1
            minute_dict[i.split()[2]][1]+=int(i.split()[3])
        if (stats_now-datetime.strptime(str(i[:19]), '%Y-%m-%d %H:%M:%S')).seconds<3600:
            hour_dict[i.split()[2]][0] += 1
            hour_dict[i.split()[2]][1] += int(i.split()[3])
        else:
            break
    for k, v in minute_dict.items():
        try:
            v[2]=v[1]/v[0]
        except ZeroDivisionError:
            pass
    for k, v in hour_dict.items():
        try:
            v[2]=v[1]/v[0]
        except ZeroDivisionError:
            pass
    return jsonify(st+'Last minute stats - { METHOD: [ No. of reqs, TAT for all reqs., Avg TAT}:\n'+str(minute_dict)+'\nLast hour stats - { METHOD: [ No. of reqs, TAT for all reqs., Avg TAT}:\n'+str(hour_dict))

if __name__=='__main__':
    app.run()