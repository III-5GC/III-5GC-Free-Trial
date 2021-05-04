from flask import Flask, request, render_template, redirect, url_for, json
import io, libconf
import configReadWrite, dockerCommand
import requests
import re

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

@app.route('/oam/api/ues', methods=['GET', 'POST'])
def ues():
    if request.method == 'GET':
        res = requests.get(ems_conf['amf-service_url'] + "/ues")
        if res.status_code == requests.codes.ok:
            ret = json.loads(res.text)
            # add disconnected ues
            ue_set = set()
            for ue in ret["uelist"]:
                ue_set.add(ue["imsi"].replace('.', ''))
            for ue in config["UE_INFO"]:
                if ue["imsi"].replace('.', '') not in ue_set:
                    ue_tmp = {}
                    ue_tmp["imsi"] = ue["imsi"]
                    ue_tmp["uekey"] = ue["key"]["k"]
                    ue_tmp["status"] = "DISCONNECTED"
                    ret["uelist"].append(ue_tmp)
            return ret
        else:
            return '{ "message" : "cannot get data from amf-service" }'
    elif request.method == 'POST': # create ue
        # create ue in config
        req_data_str = request.data.decode('ascii')
        # convert str to dict
        req_dict = json.loads(req_data_str)
        # convert dict to attrdict type string
        req_gen_conf = gen_conf(req_dict)
        # convert string to attrdict
        new_ue = libconf.loads(req_gen_conf[1: -1])
        # check ue format
        if not type_check(new_ue, "ue"):
            return '{ "message" : "wrong ue format" }'
        # check if imsi already exist
        ue_list_tmp = list(config["UE_INFO"])
        for ue_tmp in ue_list_tmp:
            if ue_tmp["imsi"].replace('.', '') == new_ue["imsi"].replace('.', ''):
                return '{ "message" : "ue already exist" }'
        imsi = new_ue["imsi"].replace('.', '')
        new_ue["imsi"] = imsi[:3] + "." + imsi[3:5] + "." + imsi[5:]
        ue_list_tmp.append(new_ue)
        config["UE_INFO"] = tuple(ue_list_tmp)
        configReadWrite.writeConfig(config, 'conf/all.conf')
        configReadWrite.genNfConf(config, containers)
        # create ue in 5gc
        post_data = {}
        post_data["imsi"] = new_ue["imsi"]
        post_data["key"] = {}
        post_data["key"]["k"] = new_ue["key"]["k"]
        if "op" in new_ue["key"]:
            post_data["key"]["op"] = new_ue["key"]["op"]
        if "opc" in new_ue["key"]:
            post_data["key"]["opc"] = new_ue["key"]["opc"]
        res = requests.post(ems_conf['amf-service_url'] + "/ues", data = json.dumps(post_data))
        if res.status_code == requests.codes.ok:
            return '{ "message" : "ue created" }'
        else:
            return '{ "message" : "cannot create ue in amf" }'

@app.route('/oam/api/ues/<string:imsi>', methods=['GET', 'PUT', 'DELETE'])
def uesimsi(imsi):
    if not type_check(imsi, "imsi"):
        return '{ "message" : "wrong imsi format" }'
    if request.method == 'GET': # read ue
        res = requests.get(ems_conf['amf-service_url'] + "/ues")
        if res.status_code == requests.codes.ok:
            data = json.loads(res.text)
            if "uelist" in data:
                for ue in data["uelist"]:
                    if ue["imsi"].replace('.', '') == imsi.replace('.', ''):
                        return ue
            # search in conf
            for ue in config["UE_INFO"]:
                if ue["imsi"].replace('.', '') == imsi.replace('.', ''):
                    ue_tmp = {}
                    ue_tmp["imsi"] = imsi
                    ue_tmp["uekey"] = ue["key"]["k"]
                    ue_tmp["status"] = "DISCONNECTED"
                    return ue_tmp
            return '{ "message" : "ue not exist" }'
        else:
            return '{ "message" : "cannot get data from amf-service" }'
    elif request.method == 'PUT': # update ue
        # update ue in config
        for ue in config["UE_INFO"]:
            if ue["imsi"].replace('.', '') == imsi.replace('.', ''):
                ue_list_tmp = list(config["UE_INFO"])
                for i, ue_tmp in enumerate(ue_list_tmp):
                    if ue_tmp["imsi"].replace('.', '') == imsi.replace('.', ''):
                        req_data_str = request.data.decode('ascii')
                        # convert str to dict
                        req_dict = json.loads(req_data_str)
                        # convert dict to attrdict type string
                        req_gen_conf = gen_conf(req_dict)
                        # convert string to attrdict
                        new_ue = libconf.loads(req_gen_conf[1: -1])
                        if not type_check(new_ue, "key"):
                            return False
                        ue_list_tmp[i]["key"] = new_ue
                        break
                config["UE_INFO"] = tuple(ue_list_tmp)
                configReadWrite.writeConfig(config, 'conf/all.conf')
                configReadWrite.genNfConf(config, containers)
                # update ue in 5gc
                put_data = {}
                put_data["k"] = new_ue["k"]
                if "op" in new_ue:
                    put_data["op"] = new_ue["op"]
                if "opc" in new_ue:
                    put_data["opc"] = new_ue["opc"]
                imsi = imsi.replace('.', '')
                res = requests.put(ems_conf['amf-service_url'] + "/ues/" + imsi[:3] + "." + imsi[3:5] + "." + imsi[5:], data = json.dumps(put_data))
                if res.status_code == requests.codes.ok:
                    return '{ "message" : "ue updated" }'
                else:
                    return '{ "message" : "cannot update ue in amf" }'
        return '{ "message" : "ue not exist" }'
    elif request.method == 'DELETE': # delete ue
        # delete ue in config
        for ue in config["UE_INFO"]:
            if ue["imsi"].replace('.', '') == imsi.replace('.', ''):
                ue_list_tmp = list(config["UE_INFO"])
                for ue_tmp in ue_list_tmp:
                    if ue_tmp["imsi"].replace('.', '') == imsi.replace('.', ''):
                        ue_list_tmp.remove(ue_tmp)
                        break
                config["UE_INFO"] = tuple(ue_list_tmp)
                configReadWrite.writeConfig(config, 'conf/all.conf')
                configReadWrite.genNfConf(config, containers)
                # delete ue in 5gc
                imsi = imsi.replace('.', '')
                res = requests.delete(ems_conf['amf-service_url'] + "/ues/" + imsi[:3] + "." + imsi[3:5] + "." + imsi[5:])
                if res.status_code == requests.codes.ok:
                    return '{ "message" : "ue deleted" }'
                else:
                    return '{ "message" : "cannot delete ue in amf" }'
        return '{ "message" : "ue not exist" }'

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

def type_check(obj, obj_type):
    if obj_type == "ue":
        if "imsi" not in obj:
            return False
        if "key" not in obj:
            return False
        return type_check(obj["imsi"], "imsi") and type_check(obj["key"], "key")
    elif obj_type == "imsi":
        return re.fullmatch(r"[0-9]{3}([0-9]{2}|\.[0-9]{2}\.)[0-9]{10}", obj) != None
    elif obj_type == "key":
        if "k" not in obj:
            return False
        if ("op" not in obj) and ("opc" not in obj):
            return False
        if "op" in obj:
            return type_check(obj["k"], "k") and type_check(obj["op"], "op")
        else:
            return type_check(obj["k"], "k") and type_check(obj["opc"], "opc")
    elif obj_type == "k":
        return re.fullmatch(r"([0-9a-fA-F]{8}\.){3}[0-9a-fA-F]{8}", obj) != None
    elif obj_type == "op" or obj_type == "opc":
        return re.fullmatch(r"([0-9a-fA-F]{8}\.){3}[0-9a-fA-F]{8}", obj) != None
    return False

if __name__ == "__main__":
    app.run()
