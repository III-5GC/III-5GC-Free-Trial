import os
import io, libconf
import copy

def writeConfig(data, filePath):
    with io.open(filePath, 'w') as f:
        libconf.dump(data, f)

def genNfConf(config, containers):
    genAmfConf(config)
    genSmfConf(config)
    genPcfConf(config)
    genUpfConf(config)
    genP4UpfConf(config)
    genNrfConf(config)
    syncNfAddr(config, containers)
    writeConfig(containers, 'conf/component.conf')

def genNrfConf(config):
    nrfConfig = {}

    nrfConfig['NRF_SBI_Address'] = config['CN_Info']['NRF_Info']['NRF_SBI_Address']
    nrfConfig['NRF_SBI_Port'] = config['CN_Info']['NRF_Info']['NRF_SBI_Port']
    nrfConfig['Heart_Beat_interval'] = config['CN_Info']['NRF_Info']['Heart_Beat_interval']
    nrfConfig['NF_IP_Checking'] = config['CN_Info']['NRF_Info']['NF_IP_Checking']
    nrfConfig['AllowedNFList'] = config['CN_Info']['NRF_Info']['AllowedNFList']

    writeConfig(nrfConfig, 'conf/nrf.conf')

def genP4UpfConf(config):
    p4upfConfig = {}

    p4upfConfig['SMF_N4_Address'] = config['CN_Info']['SMF_Info']['SMF_N4_Address']
    p4upfConfig['UPF_N3_Address'] = config['CN_Info']['P4UPF_Info']['UPF_N3_Address']
    p4upfConfig['UPF_N4_Address'] = config['CN_Info']['P4UPF_Info']['UPF_N4_Address']
    p4upfConfig['UPF_N6_Address'] = config['CN_Info']['P4UPF_Info']['UPF_N6_Address']

    p4upfConfig['p4rteIp'] = config['CN_Info']['P4UPF_Info']['p4rteIp']
    p4upfConfig['p4rtePort'] = config['CN_Info']['P4UPF_Info']['p4rtePort']
    p4upfConfig['p4dlbufVf'] = config['CN_Info']['P4UPF_Info']['p4dlbufVf']
    p4upfConfig['p4N6GwIp'] = config['CN_Info']['P4UPF_Info']['p4N6GwIp']
    p4upfConfig['p4N6GwMac'] = config['CN_Info']['P4UPF_Info']['p4N6GwMac']
    p4upfConfig['p4gtpuRuleDecap'] = config['CN_Info']['P4UPF_Info']['p4gtpuRuleDecap']
    p4upfConfig['p4gtpuRuleEncapIngress'] = config['CN_Info']['P4UPF_Info']['p4gtpuRuleEncapIngress']
    p4upfConfig['p4gtpuRuleEncapBuffIn'] = config['CN_Info']['P4UPF_Info']['p4gtpuRuleEncapBuffIn']
    p4upfConfig['p4ueIpPool'] = config['CN_Info']['P4UPF_Info']['p4ueIpPool']
    p4upfConfig['p4ueRuleArp'] = config['CN_Info']['P4UPF_Info']['p4ueRuleArp']
    p4upfConfig['p4UpfN6RuleArp'] = config['CN_Info']['P4UPF_Info']['p4UpfN6RuleArp']
    p4upfConfig['p4UpfN3RuleArp'] = config['CN_Info']['P4UPF_Info']['p4UpfN3RuleArp']
    p4upfConfig['p4nicPortN3'] = config['CN_Info']['P4UPF_Info']['p4nicPortN3']
    p4upfConfig['p4nicPortN6'] = config['CN_Info']['P4UPF_Info']['p4nicPortN6']
    p4upfConfig['p4nicPortBuffer'] = config['CN_Info']['P4UPF_Info']['p4nicPortBuffer']

    p4upfConfig['Mqtt_On'] = config['CN_Info']['P4UPF_Info']['Mqtt_On']
    p4upfConfig['Mqtt_Period'] = config['CN_Info']['P4UPF_Info']['Mqtt_Period']
    p4upfConfig['Mqtt_Hostname'] = config['CN_Info']['P4UPF_Info']['Mqtt_Hostname']
    p4upfConfig['Mqtt_Port'] = config['CN_Info']['P4UPF_Info']['Mqtt_Port']
    p4upfConfig['Mqtt_KaPeriod'] = config['CN_Info']['P4UPF_Info']['Mqtt_KaPeriod']
    p4upfConfig['Mqtt_Username'] = config['CN_Info']['P4UPF_Info']['Mqtt_Username']
    p4upfConfig['Mqtt_Password'] = config['CN_Info']['P4UPF_Info']['Mqtt_Password']
    p4upfConfig['Mqtt_TopicPrefix'] = config['CN_Info']['P4UPF_Info']['Mqtt_TopicPrefix']

    writeConfig(p4upfConfig, 'conf/p4upf.conf')

def genUpfConf(config):
    upfConfig = {}

    upfConfig['SMF_N4_Address'] = config['CN_Info']['SMF_Info']['SMF_N4_Address']
    upfConfig['UPF_N3_Address'] = config['CN_Info']['P4UPF_Info']['UPF_N3_Address']
    upfConfig['UPF_N4_Address'] = config['CN_Info']['P4UPF_Info']['UPF_N4_Address']
    upfConfig['UPF_N6_Address'] = config['CN_Info']['P4UPF_Info']['UPF_N6_Address']

    upfConfig['UPF_N6_NIC_NAME'] = "eth1"

    upfConfig['Mqtt_On'] = config['CN_Info']['UPF_Info']['Mqtt_On']
    upfConfig['Mqtt_Period'] = config['CN_Info']['UPF_Info']['Mqtt_Period']
    upfConfig['Mqtt_Hostname'] = config['CN_Info']['UPF_Info']['Mqtt_Hostname']
    upfConfig['Mqtt_Port'] = config['CN_Info']['UPF_Info']['Mqtt_Port']
    upfConfig['Mqtt_KaPeriod'] = config['CN_Info']['UPF_Info']['Mqtt_KaPeriod']
    upfConfig['Mqtt_Username'] = config['CN_Info']['UPF_Info']['Mqtt_Username']
    upfConfig['Mqtt_Password'] = config['CN_Info']['UPF_Info']['Mqtt_Password']
    upfConfig['Mqtt_TopicPrefix'] = config['CN_Info']['UPF_Info']['Mqtt_TopicPrefix']

    writeConfig(upfConfig, 'conf/upf.conf')

def genPcfConf(config):
    pcfConfig = {}

    pcfConfig['PLMN'] = config['CN_Info']['PLMN']

    pcfConfig['PCF_SBI_Address'] = config['CN_Info']['PCF_Info']['PCF_SBI_Address']
    pcfConfig['FiveQI'] = config['CN_Info']['PCF_Info']['FiveQI']

    pcfConfig['NRF_SBI_Address'] = config['CN_Info']['PCF_Info']['NRF_SBI_Address']
    pcfConfig['NRF_SBI_Port'] = config['CN_Info']['PCF_Info']['NRF_SBI_Port']

    pcfConfig['QosDataList'] = config['CN_Info']['PCF_Info']['QosDataList']

    pcfConfig['UeList'] = list()
    for ue in config['UE_INFO']:
        pcfConfig['UeList'].append({'imsi':ue['imsi']})
    pcfConfig['UeList'] = tuple(pcfConfig['UeList'])

    writeConfig(pcfConfig, 'conf/pcf.conf')

def genSmfConf(config):
    smfConfig = {}

    smfConfig['PLMN'] = config['CN_Info']['PLMN']
    smfConfig['DNN'] = config['CN_Info']['DataNetwork']['DNN']

    smfConfig['AMF_SBI_Address'] = config['CN_Info']['AMF_Info']['AMF_SBI_Address']
    smfConfig['SMF_SBI_Address'] = config['CN_Info']['SMF_Info']['SMF_SBI_Address']
    smfConfig['SMF_N4_Address'] = config['CN_Info']['SMF_Info']['SMF_N4_Address']
    smfConfig['PCF_SBI_Address'] = config['CN_Info']['PCF_Info']['PCF_SBI_Address']
    smfConfig['UPF_N3_Address'] = config['CN_Info']['P4UPF_Info']['UPF_N3_Address']
    smfConfig['UPF_N4_Address'] = config['CN_Info']['P4UPF_Info']['UPF_N4_Address']

    #smfConfig['IUPF_N3_Address'] = config['CN_Info']['P4UPF_Info']['IUPF_N3_Address']
    #smfConfig['IUPF_N4_Address'] = config['CN_Info']['P4UPF_Info']['IUPF_N4_Address']
    #smfConfig['IUPF_N9_Address'] = config['CN_Info']['P4UPF_Info']['IUPF_N9_Address']

    smfConfig['dhcp'] = config['CN_Info']['SMF_Info']['dhcp']

    smfConfig['N1N2_NEED_NGAP_SECURITYINDICATION'] = config['CN_Info']['SMF_Info']['N1N2_NEED_NGAP_SECURITYINDICATION']
    smfConfig['N1N2_NGAP_SECURITYINDICATION_INTEGRITY_PI'] = config['CN_Info']['SMF_Info']['N1N2_NGAP_SECURITYINDICATION_INTEGRITY_PI']
    smfConfig['N1N2_NGAP_SECURITYINDICATION_CONFIDENTIALITY_PI'] = config['CN_Info']['SMF_Info']['N1N2_NGAP_SECURITYINDICATION_CONFIDENTIALITY_PI']
    smfConfig['N1N2_NGAP_SECURITYINDICATION_UL'] = config['CN_Info']['SMF_Info']['N1N2_NGAP_SECURITYINDICATION_UL']
    smfConfig['N1N2_NGAP_SECURITYINDICATION_DL'] = config['CN_Info']['SMF_Info']['N1N2_NGAP_SECURITYINDICATION_DL']

    smfConfig['Mqtt_On'] = config['CN_Info']['SMF_Info']['Mqtt_On']
    smfConfig['Mqtt_Period'] = config['CN_Info']['SMF_Info']['Mqtt_Period']
    smfConfig['Mqtt_Hostname'] = config['CN_Info']['SMF_Info']['Mqtt_Hostname']
    smfConfig['Mqtt_Port'] = config['CN_Info']['SMF_Info']['Mqtt_Port']
    smfConfig['Mqtt_KaPeriod'] = config['CN_Info']['SMF_Info']['Mqtt_KaPeriod']
    smfConfig['Mqtt_Username'] = config['CN_Info']['SMF_Info']['Mqtt_Username']
    smfConfig['Mqtt_Password'] = config['CN_Info']['SMF_Info']['Mqtt_Password']
    smfConfig['Mqtt_TopicPrefix'] = config['CN_Info']['SMF_Info']['Mqtt_TopicPrefix']

    smfConfig['Test_Paging'] = config['CN_Info']['SMF_Info']['Test_Paging']

    smfConfig['Check_Allowed_AMF'] = config['CN_Info']['SMF_Info']['Check_Allowed_AMF']
    smfConfig['AllowedAmfList'] = config['CN_Info']['SMF_Info']['AllowedAmfList']

    smfConfig['UpfList'] = config['CN_Info']['SMF_Info']['UpfList']

    smfConfig['NRF_SBI_Address'] = config['CN_Info']['SMF_Info']['NRF_SBI_Address']
    smfConfig['NRF_SBI_Port'] = config['CN_Info']['SMF_Info']['NRF_SBI_Port']
    smfConfig['Discover_Interval'] = config['CN_Info']['SMF_Info']['Discover_Interval']
    smfConfig['First_Discover_Delay'] = config['CN_Info']['SMF_Info']['First_Discover_Delay']
    smfConfig['NF_Discover_Method'] = config['CN_Info']['SMF_Info']['NF_Discover_Method']

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

    amfConfig['AMF_Region_ID'] = config['CN_Info']['AMF_Info']['AMF_Region_ID']
    amfConfig['AMF_Set_ID'] = config['CN_Info']['AMF_Info']['AMF_Set_ID']
    amfConfig['AMF_Pointer'] = config['CN_Info']['AMF_Info']['AMF_Pointer']

    amfConfig['AMF_NGAP_Address'] = config['CN_Info']['AMF_Info']['AMF_NGAP_Address']
    amfConfig['AMF_SBI_Address'] = config['CN_Info']['AMF_Info']['AMF_SBI_Address']
    amfConfig['AMF_N2HO_Address'] = config['CN_Info']['AMF_Info']['AMF_N2HO_Address']

    amfConfig['SMF_SBI_Address'] = config['CN_Info']['SMF_Info']['SMF_SBI_Address']

    amfConfig['Core_NEA1_Support'] = config['CN_Info']['AMF_Info']['Core_NEA1_Support']
    amfConfig['Core_NEA2_Support'] = config['CN_Info']['AMF_Info']['Core_NEA2_Support']
    amfConfig['Core_NEA3_Support'] = config['CN_Info']['AMF_Info']['Core_NEA3_Support']

    amfConfig['Core_NIA1_Support'] = config['CN_Info']['AMF_Info']['Core_NIA1_Support']
    amfConfig['Core_NIA2_Support'] = config['CN_Info']['AMF_Info']['Core_NIA2_Support']
    amfConfig['Core_NIA3_Support'] = config['CN_Info']['AMF_Info']['Core_NIA3_Support']

    amfConfig['UE_AMBR_DL'] = config['CN_Info']['AMF_Info']['UE_AMBR_DL']
    amfConfig['UE_AMBR_UL'] = config['CN_Info']['AMF_Info']['UE_AMBR_UL']

    amfConfig['gNB_Check_On'] = config['CN_Info']['AMF_Info']['gNB_Check_On']

    amfConfig['GnbIpList'] = config['CN_Info']['AMF_Info']['GnbIpList']

    amfConfig['Mqtt_On'] = config['CN_Info']['AMF_Info']['Mqtt_On']
    amfConfig['Mqtt_Period'] = config['CN_Info']['AMF_Info']['Mqtt_Period']
    amfConfig['Mqtt_Hostname'] = config['CN_Info']['AMF_Info']['Mqtt_Hostname']
    amfConfig['Mqtt_Port'] = config['CN_Info']['AMF_Info']['Mqtt_Port']
    amfConfig['Mqtt_KaPeriod'] = config['CN_Info']['AMF_Info']['Mqtt_KaPeriod']
    amfConfig['Mqtt_Username'] = config['CN_Info']['AMF_Info']['Mqtt_Username']
    amfConfig['Mqtt_Password'] = config['CN_Info']['AMF_Info']['Mqtt_Password']
    amfConfig['Mqtt_TopicPrefix'] = config['CN_Info']['AMF_Info']['Mqtt_TopicPrefix']

    amfConfig['T3502_On'] = config['CN_Info']['AMF_Info']['T3502_On']
    amfConfig['T3502_Unit'] = config['CN_Info']['AMF_Info']['T3502_Unit']
    amfConfig['T3502_Value'] = config['CN_Info']['AMF_Info']['T3502_Value']
    amfConfig['T3512_On'] = config['CN_Info']['AMF_Info']['T3512_On']
    amfConfig['T3512_Unit'] = config['CN_Info']['AMF_Info']['T3512_Unit']
    amfConfig['T3512_Value'] = config['CN_Info']['AMF_Info']['T3512_Value']

    amfConfig['Change_GUTI'] = config['CN_Info']['AMF_Info']['Change_GUTI']

    amfConfig['UeKeyList'] = config['UE_INFO']

    amfConfig['NRF_SBI_Address'] = config['CN_Info']['AMF_Info']['NRF_SBI_Address']
    amfConfig['NRF_SBI_Port'] = config['CN_Info']['AMF_Info']['NRF_SBI_Port']
    amfConfig['Discover_Interval'] = config['CN_Info']['AMF_Info']['Discover_Interval']

    amfConfig['Overload_Check'] = config['CN_Info']['AMF_Info']['Overload_Check']
    amfConfig['Overload_Check_Interval'] = config['CN_Info']['AMF_Info']['Overload_Check_Interval']
    amfConfig['NF_Discover_Method'] = config['CN_Info']['AMF_Info']['NF_Discover_Method']

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
    newAry = []
    length = len(config)

    for i in range(length, int(data[key + 'MaxLen'])):
        config.append(copy.deepcopy(config[0]))

    for i in range(len(config)):
        if (True == storeConfig(layout, config[i], data, i+1)):
            newAry.append(copy.deepcopy(config[i]))
    config.clear()
    for ele in newAry:
        config.append(ele)

def syncNfAddr(config, containers):
    containers['AMF']['Ip'] = config['CN_Info']['AMF_Info']['AMF_NGAP_Address']
    containers['SMF']['Ip'] = config['CN_Info']['SMF_Info']['SMF_SBI_Address']
    containers['UPF']['Ip'] = config['CN_Info']['P4UPF_Info']['UPF_N4_Address']
    containers['PCF']['Ip'] = config['CN_Info']['PCF_Info']['PCF_SBI_Address']
    containers['NRF']['Ip'] = config['CN_Info']['NRF_Info']['NRF_SBI_Address']
