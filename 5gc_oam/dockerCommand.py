import os

def rmContainer(containers, target):
    os.system('docker rm -f ' + containers[target]['Name'])

    print("Stop ", target)

def runContainer(containers, target):
    cmd = 'docker run --privileged'
    cmd += ' -v ' + os.environ['mountPath'] + ':/usr/etc'
    cmd += ' -itd --network ' + os.environ['sbiName']
    cmd += ' --ip ' + containers[target]['Ip']
    cmd += ' --name ' + containers[target]['Name']
    cmd += ' --hostname ' + containers[target]['Name']
    cmd += ' ' + containers[target]['Image']

    print(target, " IP ", containers[target]['Ip'])

    os.system(cmd)

    if 'UPF' == target:
        os.system('docker network connect --ip 10.254.254.6 ' + os.environ['n6Name'] + ' ' + containers[target]['Name'])

    print("Start ", target)
