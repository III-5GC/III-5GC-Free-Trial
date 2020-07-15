from flask import Flask, request, render_template, redirect, url_for
import io, libconf
import configReadWrite, dockerCommand

app = Flask(__name__)

layout = ''
config = ''
containers = ''

with io.open('conf/all.conf') as f:
    config = libconf.load(f)

with io.open('conf/param.conf') as f:
    layout = libconf.load(f)

with io.open('conf/component.conf') as f:
    containers = libconf.load(f)
    configReadWrite.syncNfAddr(config, containers)

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

@app.route('/oam/test', methods=['GET'])
def test():
    return render_template("test.html")

if __name__ == "__main__":
    app.run()
