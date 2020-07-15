import os
import io, libconf

def writeConfig(data, filePath):
    with io.open(filePath, 'w') as f:
        libconf.dump(data, f)

def genNfConf(config, containers):
    genAmfConf(config)
    genSmfConf(config)
    genPcfConf(config)
    genUpfConf(config)
    syncNfAddr(config, containers)
    writeConfig(containers, 'conf/component.conf')

def genUpfConf(config):
    upfConfig = {}

    upfConfig['SMF_N4_Address'] = config['NF_Address']['SMF_Address']
    upfConfig['UPF_N3_Address'] = config['NF_Address']['UPF_Address']
    upfConfig['UPF_N4_Address'] = config['NF_Address']['UPF_Address']
    upfConfig['UPF_N6_Address'] = "10.254.254.6"

    upfConfig['UPF_N6_NIC_NAME'] = "eth1"

    writeConfig(upfConfig, 'conf/upf.conf')

def genPcfConf(config):
    pcfConfig = {}

    pcfConfig['PLMN'] = config['CN_Info']['PLMN']

    pcfConfig['PCF_SBI_Address'] = config['NF_Address']['PCF_Address']
    pcfConfig['SMF_SBI_Address'] = config['NF_Address']['SMF_Address']

    pcfConfig['UeList'] = list()
    for ue in config['UE_INFO']:
        pcfConfig['UeList'].append({'imsi':ue['imsi']})
    pcfConfig['UeList'] = tuple(pcfConfig['UeList'])

    writeConfig(pcfConfig, 'conf/pcf.conf')

def genSmfConf(config):
    smfConfig = {}

    smfConfig['PLMN'] = config['CN_Info']['PLMN']
    smfConfig['DNN'] = config['CN_Info']['DataNetwork']['DNN']

    smfConfig['AMF_SBI_Address'] = config['NF_Address']['AMF_Address']
    smfConfig['SMF_SBI_Address'] = config['NF_Address']['SMF_Address'] 
    smfConfig['SMF_N4_Address'] = config['NF_Address']['SMF_Address'] 
    smfConfig['PCF_SBI_Address'] = config['NF_Address']['PCF_Address'] 
    smfConfig['UPF_N3_Address'] = config['NF_Address']['UPF_Address'] 
    smfConfig['UPF_N4_Address'] = config['NF_Address']['UPF_Address'] 
    smfConfig['IUPF_N3_Address'] = config['NF_Address']['UPF_Address'] 
    smfConfig['IUPF_N4_Address'] = config['NF_Address']['UPF_Address'] 
    smfConfig['IUPF_N9_Address'] = config['NF_Address']['UPF_Address'] 

    smfConfig['UeList'] = list()
    for ue in config['UE_INFO']:
        smfConfig['UeList'].append({'imsi':ue['imsi']})
    smfConfig['UeList'] = tuple(smfConfig['UeList'])

    writeConfig(smfConfig, 'conf/smf.conf')

def genAmfConf(config):
    amfConfig = {}
    plmnConfig = {}
    
    plmnConfig['PLMN'] = config['CN_Info']['PLMN']
    plmnConfig['SliceList'] = config['CN_Info']['SliceList']

    amfConfig['PLMN_SupportList'] = list()
    amfConfig['PLMN_SupportList'].append(plmnConfig)
    amfConfig['PLMN_SupportList'] = tuple(amfConfig['PLMN_SupportList'])

    amfConfig['AMF_Name'] = config['CN_Info']['AMF_Info']['AMF_Name']
    amfConfig['AMF_Region_ID'] = config['CN_Info']['AMF_Info']['AMF_Region_ID']
    amfConfig['AMF_Set_ID'] = config['CN_Info']['AMF_Info']['AMF_Set_ID']
    amfConfig['AMF_Pointer'] = config['CN_Info']['AMF_Info']['AMF_Pointer']

    amfConfig['AMF_SBI_Address'] = config['NF_Address']['AMF_Address']
    amfConfig['AMF_N2_Address'] = config['NF_Address']['AMF_Address']
    amfConfig['AMF_N2HO_Address'] = config['NF_Address']['AMF_Address']

    amfConfig['SMF_SBI_Address'] = config['NF_Address']['SMF_Address']

    amfConfig['UeKeyList'] = config['UE_INFO']

    writeConfig(amfConfig, 'conf/amf.conf')

def storeConfig(layout, config, data, index=0, postfix=''):
    for key in layout:
        keyI = key + postfix

        if (0 != index):
            keyI = keyI + str(index)

        if ('type' in layout[key]) and ('group' == layout[key]['type']):
            if ('list' in layout[key]) and ('true' == layout[key]['list']):
                config[key] = list(config[key])
                storeListConfig(key, layout[key]['data'], config[key], data)
                config[key] = tuple(config[key])
            else:
                if (('' != postfix) or ('key' == key)):
                    storeConfig(layout[key]['data'], config[key], data, postfix=keyI)
                else:
                    storeConfig(layout[key]['data'], config[key], data)
        else:
            if (keyI not in data):
                if ('op'==key) or ('opc'==key):
                    config.pop(key, None)
                    continue
                return False

            if ('type' in layout[key]) and ('num' == layout[key]['type']):
                config[key] = int(data.get(keyI))
            else:
                config[key] = data.get(keyI)

    return True

def storeListConfig(key, layout, config, data):
    rmAry = []
    length = len(config)

    for i in range(length, int(data[key + 'MaxLen'])):
        config.append(config[0].copy())

    for i in range(len(config)):
        if (False == storeConfig(layout, config[i], data, i+1)):
           rmAry.append(config[i])

    for rmItem in rmAry:
        config.remove(rmItem)

def syncNfAddr(config, containers):
    containers['AMF']['Ip'] = config['NF_Address']['AMF_Address']
    containers['SMF']['Ip'] = config['NF_Address']['SMF_Address']
    containers['UPF']['Ip'] = config['NF_Address']['UPF_Address']
    containers['PCF']['Ip'] = config['NF_Address']['PCF_Address']
