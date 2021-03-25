from flask import Flask, request, render_template, redirect, url_for, json
import io, libconf
import configReadWrite, dockerCommand
import requests

app = Flask(__name__)

layout = ''
config = ''
containers = ''
ems_conf = ''

with io.open('conf/all.conf') as f:
    config = libconf.load(f)

with io.open('conf/param.conf') as f:
    layout = libconf.load(f)

with io.open('conf/component.conf') as f:
    containers = libconf.load(f)
    configReadWrite.syncNfAddr(config, containers)

with io.open('conf/ems.conf') as f:
    ems_conf = libconf.load(f)

def modifyAllStatus(status):
    global containers

    for key in containers:
        modifyStatus(key, status)

def modifyStatus(target, status):
    global containers

    if 'stop' == status:
        dockerCommand.rmContainer(containers, target)
    else:
        dockerCommand.runContainer(containers, target)

    containers[target]['status'] = status

def gen_conf(obj):
    ret = ''
    if isinstance(obj, dict):
        ret = ret + '{'
        for el in obj:
            ret = ret + str(el) + '='
            ret = ret + gen_conf(obj[el])
            ret = ret + ';'
        ret = ret + '}'
        return ret
    elif isinstance(obj, list):
        ret = ret + '('
        for el in obj:
            ret = ret + gen_conf(el)
            ret = ret + ','
        ret = ret + ')'
        return ret
    elif isinstance(obj, str):
        return '"' + obj + '"'
    else:
        return str(obj)

@app.route('/oam/edit', methods=['GET', 'POST'])
def confpage():
    if 'POST' == request.method:
        configReadWrite.storeConfig(layout=layout, config=config, data=request.form)
        configReadWrite.writeConfig(config, 'conf/all.conf')
        configReadWrite.genNfConf(config, containers)

        return redirect(url_for('homepage'))
    return render_template("editConfig.html", layout=layout, config=config)

@app.route('/oam/container', methods=['POST'])
def containerpage():
    if 'POST' == request.method:
        for key, value in request.form.items():
            if 'all' == key:
                modifyAllStatus(value)
            else:
                modifyStatus(key, value)
    return redirect(url_for('homepage'))

@app.route('/oam/', methods=['GET'])
def homepage():
    return render_template("showConfig.html", layout=layout, config=config, containers=containers)

@app.route('/oam/api/config', methods=['GET', 'POST'])
def configapi():
    global config
    if request.method == 'GET':
        # convert attrdict to json string
        return json.dumps(config)
    elif request.method == 'POST':
        req_data_str = request.data.decode('ascii')
        # convert str to dict
        req_dict = json.loads(req_data_str)
        # convert dict to attrdict type string
        req_gen_conf = gen_conf(req_dict)
        # convert string to attrdict
        config = libconf.loads(req_gen_conf[1: -1])
        # write config to config files
        configReadWrite.writeConfig(config, 'conf/all.conf')
        configReadWrite.genNfConf(config, containers)
        return '{ "message" : "success" }'

@app.route('/oam/api/ues', methods=['GET'])
def ues():
    res = requests.get(ems_conf['amf-service_url'] + "/ues")
    if res.status_code == requests.codes.ok:
        return res.text
    else:
        return "cannot get data from amf-service"

@app.route('/oam/api/ues/search', methods=['POST'])
def uessearch():
    if "status" not in request.json:
        return "no status in request data"
    res = requests.post(ems_conf['amf-service_url'] + "/ues/search", data = '{"status":"' + request.json['status'] + '"}')
    if res.status_code == requests.codes.ok:
        return res.text
    else:
        return "cannot get data from amf-service"

@app.route('/oam/api/sm/algo', methods=['GET'])
def smalgo():
    algo = dict()
    algo["Core_NEA0_Support"] = 1
    algo["Core_NEA1_Support"] = config["CN_Info"]["AMF_Info"]["Core_NEA1_Support"]
    algo["Core_NEA2_Support"] = config["CN_Info"]["AMF_Info"]["Core_NEA2_Support"]
    algo["Core_NEA3_Support"] = config["CN_Info"]["AMF_Info"]["Core_NEA3_Support"]
    algo["Core_NIA0_Support"] = 1
    algo["Core_NIA1_Support"] = config["CN_Info"]["AMF_Info"]["Core_NIA1_Support"]
    algo["Core_NIA2_Support"] = config["CN_Info"]["AMF_Info"]["Core_NIA2_Support"]
    algo["Core_NIA3_Support"] = config["CN_Info"]["AMF_Info"]["Core_NIA3_Support"]
    return json.dumps(algo)

@app.route('/oam/test', methods=['GET'])
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.run()
