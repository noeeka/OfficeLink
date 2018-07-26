#!/usr/bin/env python

import sys, os, os.path, time
import threading
import datetime
import re, binascii, struct
import cookielib, urllib2, urllib, json
import traceback

class R():
    logfile = None
    logstdout = True # false
    @staticmethod
    def logopen():
        directory = 'logs'
        if not os.path.isdir(directory):
            os.mkdir(directory)
        path = directory + "/log_" + re.sub("[:\-\\ ]", '_', str(datetime.datetime.now())) + '.txt'
        R.logfile = open(path, "w")
    @staticmethod
    def log(*msg):
        if R.logstdout:
            a0 = (str(datetime.datetime.now()),) + msg
            print(a0)
        if R.logfile:
            R.logfile.write(str(a0) + "\r\n")
            R.logfile.flush()
    @staticmethod
    def debug(*msg):
        a0 = (str(datetime.datetime.now()),) + msg
        print(a0)

class TestCase(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.timeout   = kwargs.get('timeout', 2)
        self.cookie    = kwargs.get('cookie', cookielib.CookieJar())
        self.case_name = kwargs.get('case_name', 'help')
        self.host      = kwargs.get('host', '192.168.1.157')
        self.user_name = kwargs.get('user_name', '6005')
        self.password  = kwargs.get('password', '6005')
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.case_list = {
            'extensions/status'             : self.extensions_status,
            'providers/status'              : self.providers_status,
            'parkings/status'               : self.parkings_status,
            'meetingrooms/status'           : self.meetingrooms_status,
            'system/info'                   : self.system_info,
            'extensions'                    : self.extensions,
            'extensions/del'                : self.extensions_delete,
            'extensions/add'                : self.extensions_add,
            'providers'                     : self.providers,
            'providers/del'                 : self.providers_delete,
            'providers/add'                 : self.providers_add,
            'ivrs'                          : self.ivrs,
            'ivrs/del'                      : self.ivrs_delete,
            'ivrs/add'                      : self.ivrs_add,
            'dialplans'                     : self.dialplans,
            'dialplans/del'                 : self.dialplans_delete,
            'dialplans/add'                 : self.dialplans_add,
            'dialrules/del'                 : self.dialrules_delete,
            'dialrules'                     : self.dialrules,
            'dialrules/add'                 : self.dialrules_add,
            'dialrules/meetingrooms/add'    : self.dialrules_meetingrooms_add,
            'ringgroups'                    : self.ringgroups,
            'ringgroups/del'                : self.ringgroups_delete,
            'ringgroups/add'                : self.ringgroups_add,
            'meetingrooms'                  : self.meetingrooms,
            'meetingrooms/del'              : self.meetingrooms_delete,
            'meetingrooms/add'              : self.meetingrooms_add,
            'voicemail'                     : self.voicemail,
            'voicemail/conf'                : self.voicemail_conf,
            'call/feature'                  : self.call_feature,
            'call/feature/conf'             : self.call_feature_conf,
            'mohs'                          : self.mohs,
            'mohs/del'                      : self.mohs_delete,
            'mohs/add'                      : self.mohs_add,
            'sip'                           : self.sip,
            'sip/conf'                      : self.sip_conf,
            'call/records'                  : self.call_records,
            'call/records/del'              : self.call_records_delete,
            'firewall/filters'              : self.firewall_filters,
            'firewall/filters/del'          : self.firewall_filters_del,
            'firewall/filters/add'          : self.firewall_filters_add,
            'users'                         : self.users,
            'users/del'                     : self.users_delete,
            'users/add'                     : self.users_add,
            'conf/reload'                   : self.conf_reload,
            'all'                           : self.all,
            'all/del'                       : self.all_delete,
            'all/add'                       : self.all_add,
        }

    def run(self):
        if 'help' == self.case_name:
            R.log(self.case_list.keys())
            return
        if not self.case_list.has_key(self.case_name):
            return
        try:
            self.handler()
        except Exception, e:
            traceback.print_exc()
            R.log(e)
            time.sleep(1)
        else:
            pass
        finally:
            pass
    
    def handler(self):
        self.case_list[self.case_name]()

    def request(self, **kwargs):
        host    = kwargs.get('host', '192.168.1.157')
        method  = kwargs.get('method', 'GET')
        api     = kwargs.get('api', '/api/extensions/status/1/20')
        data    = kwargs.get('data', '')
        url     = 'http://' + host + api
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json;charset=utf-8')

        result = {
            "host": host, "method": method, "api": api, "data": data, "code": 0, "result": None, "duration": 0,
        }
        time0 = time.time()
        if data:
            data = json.dumps(data)
            data = data.encode('unicode_escape')
        else:
            data = ''
        response = None
        try:
            if 'POST' == method:
                response = self.opener.open(req, data, self.timeout)
            else:
                response = self.opener.open(req, None, self.timeout)
            data = response.read()
            result["code"] = 200
            result["result"] = data
            #result["data"] = data.decode('unicode_escape').replace('\\/', '/')
        except urllib2.HTTPError, e:
            result["code"] = e.code
            result["result"] = e.read()
        except urllib2.URLError, e:
            result["result"] = repr(e)
        except Exception, e:
            result["result"] = repr(e)
            pass
        else:
            pass
        finally:
            pass
        result["duration"] = time.time() - time0
        return result

    def user_login(self):
        data = {'name': self.user_name, 'password': self.password}
        data = self.request(host=self.host, method='POST', api='/api/user/login', data=data)
        return data

    def user_logout(self):
        data = self.request(host=self.host, method='POST', api='/api/user/logout', data=None)
        return data

    def list_delete(self, module, key):
        data = self.user_login()
        R.log(data)

        while True:
            data = self.request(host=self.host, api='/api/'+module+'/1/20', data=None)
            R.log(data)
            data = json.loads(data['result'])
            if not data[module]:
                break
            data = [plan[key] for plan in data[module]]
            if not data:
                break
            data = self.request(host=self.host, method='POST', api='/api/'+module+'/delete', data=data)
            R.log(data)

        data = self.user_logout()
        R.log(data)

    def list_page(self, module, key):
        data = self.user_login()
        R.log(data)

        page = 1
        while True:
            data = self.request(host=self.host, api='/api/'+module+'/'+str(page)+'/20')
            R.log(data)
            page = page + 1
            data = json.loads(data['result'])
            if not data or not data.has_key(key) or not data[key] or page > 50:
                break

        data = self.user_logout()
        R.log(data)

    def extensions_status(self):
        self.list_page('extensions/status', 'extensions')

    def providers_status(self):
        self.list_page('providers/status', 'providers')

    def parkings_status(self):
        self.list_page('parkings/status', 'parkings')

    def meetingrooms_status(self):
        self.list_page('meetingrooms/status', 'meetingrooms')

    def system_info(self):
        data = self.user_login()
        R.log(data)

        data = self.request(host=self.host, api='/api/system/info', data=None)
        R.log(data)

        data = self.user_logout()
        R.log(data)

    def extensions(self):
        self.list_page('extensions', 'extensions')

    def extensions_delete(self):
        self.list_delete('extensions', 'extension')

    def extensions_add(self):
        data = self.user_login()
        R.log(data)

        for i in range(10):
            data_post = {
                'extension': str(6000+i), 
                'nickname': str(6000+i), 
                'photo': '/img/avatar130.png', 
                'dialplan': 'systec', 
                'password': str(6000+i), 
                'email': 'systec@systec.com', 
                'voicemail_pin': '1234', 
                'codecs': ['ulaw'], 
                'transfer_days': [1, 2, 3, 4, 5], 
                'transfer_time': ['09:00', '17:30'], 
                'transfer_style': 'busy', 
                'transfer_type': 'voicemail', 
                'transfer_target': str(6000+i), 
                'ring_timeout': 0, 
            }
            data = self.request(host=self.host, method='POST', api='/api/extensions/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/extensions/update', data=data_post)
                R.log(data)
        for i in range(10):
            data_post = {
                'extension': str(8000+i), 
                'nickname': str(8000+i), 
                'photo': '/img/avatar130.png', 
                'dialplan': 'systec', 
                'password': str(8000+i), 
                'email': 'systec@systec.com', 
                'voicemail_pin': '1234', 
                'codecs': ['ulaw'], 
                'transfer_days': [1, 2, 3, 4, 5], 
                'transfer_time': ['09:00', '17:30'], 
                'transfer_style': 'busy', 
                'transfer_type': 'voicemail', 
                'transfer_target': str(8000+i), 
                'ring_timeout': 0, 
            }
            data = self.request(host=self.host, method='POST', api='/api/extensions/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/extensions/update', data=data_post)
                R.log(data)

        data = self.user_logout()
        R.log(data)

    def providers(self):
        self.list_page('providers', 'providers')

    def providers_delete(self):
        self.list_delete('providers', 'name')

    def providers_add(self):
        data = self.user_login()
        R.log(data)

        data_post = {
            'name': 'SIP', 
            'user': str(80007), 
            'password': str(80007), 
            'address': 'www.systec-pbx.net', 
            'port': 5060, 
            'dialplan': 'systec', 
            'entry': '7000',
        }
        data = self.request(host=self.host, method='POST', api='/api/providers/add', data=data_post)
        R.log(data)
        data = json.loads(data['result'])
        if 0 != data['state']:
            data = self.request(host=self.host, method='POST', api='/api/providers/update', data=data_post)
            R.log(data)

        data_post = {
            'name': 'PSTN', 
            'user': '', 
            'password': '', 
            'address': '192.168.1.211', 
            'port': 5060, 
            'dialplan': 'systec', 
            'entry': '7000',
        }
        data = self.request(host=self.host, method='POST', api='/api/providers/add', data=data_post)
        R.log(data)
        data = json.loads(data['result'])
        if 0 != data['state']:
            data = self.request(host=self.host, method='POST', api='/api/providers/update', data=data_post)
            R.log(data)
       
        data = self.user_logout()
        R.log(data)

    def ivrs(self):
        self.list_page('ivrs', 'ivrs')

    def ivrs_delete(self):
        self.list_delete('ivrs', 'name')

    def ivrs_add(self):
        data = self.user_login()
        R.log(data)

        for i in range(5):
            rule = {
                'rule': str(7000 + i), 
                'application': 'Dial', 
                'args': ['SIP/${EXTEN}', 'm'], 
            }

            rules = [rule]
            data_post = {
                'name': 'ivr' + str(i), 
                'extension': str(7000+i), 
                'rules': rules, 
            }
            data = self.request(host=self.host, method='POST', api='/api/ivrs/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/ivrs/update', data=data_post)
                R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def dialplans(self):
        self.list_page('dialplans', 'dialplans')

    def dialplans_delete(self):
        self.list_delete('dialplans', 'name')

    def dialplans_add(self):
        data = self.user_login()
        R.log(data)

        rules = ['rule' + str(i) for i in range(1)]
        data = {'name': 'systec', 'rules': rules}
        data = self.request(host=self.host, method='POST', api='/api/dialplans/add', data=data)
        R.log(data)
        for i in range(5):
            rules = ['rule1', 'rule2', 'rule3']
            data_post = {'name': 'plan' + str(i), 'rules': rules}
            data = self.request(host=self.host, method='POST', api='/api/dialplans/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/dialplans/update', data=data_post)
                R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def dialrules(self):
        self.list_page('dialrules', 'dialrules')

    def dialrules_delete(self):
        self.list_delete('dialrules', 'name')

    def dialrules_meetingrooms_add(self):
        data = self.user_login()
        R.log(data)

        page = 1
        while True:
            data = self.request(host=self.host, api='/api/meetingrooms/'+str(page)+'/20')
            R.log(data)
            page = page + 1
            data = json.loads(data['result'])
            if not data or not data.has_key('meetingrooms') or not data['meetingrooms'] or page > 50:
                break
            conferences = data['meetingrooms']
            for item in conferences:
                rule = {
                    'rule': item['extension'], 
                    'application': 'MeetMe', 
                    'args': ['${EXTEN}', 'MsI'], 
                    'strip': 0, 
                    'prepend': '', 
                    'filters': '',
                }
                rules = [rule]
                data_post = {'name': 'conf_' + rule['rule'], 'rules': rules}
                data = self.request(host=self.host, method='POST', api='/api/dialrules/add', data=data_post)
                R.log(data)
                data = json.loads(data['result'])
                if 0 != data['state']:
                    data = self.request(host=self.host, method='POST', api='/api/dialrules/update', data=data_post)
                    R.log(data)
 
        data = self.user_logout()
        R.log(data)

    def dialrules_add(self):
        data = self.user_login()
        R.log(data)

        for i in range(5):
            rule = {
                'rule': str(6000 + i), 
                'application': 'Dial', 
                'args': ['SIP/${EXTEN}', 20, 'm'], 
                'strip': 0, 
                'prepend': '', 
                'filters': '',
            }
            rules = [rule]
            data_post = {'name': 'rule' + str(i), 'rules': rules}
            data = self.request(host=self.host, method='POST', api='/api/dialrules/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/dialrules/update', data=data_post)
                R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def ringgroups(self):
        self.list_page('ringgroups', 'ringgroups')

    def ringgroups_delete(self):
        self.list_delete('ringgroups', 'name')

    def ringgroups_add(self):
        data = self.user_login()
        R.log(data)

        for i in range(5):
            data_post = {
                'name': 'group' + str(i), 
                'extension': str(7300+i), 
                'ring_style': 'all', 
                'timeout': 20, 
                'members': [str(m) for m in range(6000, 6020)],
            }
            data = self.request(host=self.host, method='POST', api='/api/ringgroups/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/ringgroups/update', data=data_post)
                R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def meetingrooms(self):
        self.list_page('meetingrooms', 'meetingrooms')

    def meetingrooms_delete(self):
        self.list_delete('meetingrooms', 'extension')

    def meetingrooms_add(self):
        data = self.user_login()
        R.log(data)

        for i in range(5):
            data_post = {
                'extension': str(6300 + i), 
                'user_pin': '1234', 
                'admin_pin': '123456', 
            }
            data = self.request(host=self.host, method='POST', api='/api/meetingrooms/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/meetingrooms/update', data=data_post)
                R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def voicemail(self):
        data = self.user_login()
        R.log(data)

        data = self.request(host=self.host, api='/api/voicemail/conf')
        R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def voicemail_conf(self):
        data = self.user_login()
        R.log(data)

        data = {
            'extension': '10000', 
            'dial_voicemail': False, 
            'maxmessage': 20, 
            'maxsec': 60, 
            'minsec': 3, 
            'greating': False, 
        }
        data = self.request(host=self.host, method='POST', api='/api/voicemail/conf/update', data=data)
        R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def call_feature(self):
        data = self.user_login()
        R.log(data)
        data = self.request(host=self.host, api='/api/call/feature/conf')
        R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def call_feature_conf(self):
        data = self.user_login()
        R.log(data)

        parking = {
            'extension': '700',
            'space': ['701', '710'],
            'timeout': 20,
        }
        feature_map = {
            'blind': '#1',
            'hungup': '*0',
            'transfer': '*2',
            'parking': '#72',
        }
        app_map = [
            {'name': 'office1', 'digit': '#66', 'channel': 'self', 'application': 'Dial', 'args': ['SIP/6002']},
            {'name': 'office2', 'digit': '#67', 'channel': 'self', 'application': 'Dial', 'args': ['SIP/6002']},
        ]

        data = {
            'digit_timeout': 200,
            'parking': parking,
            'feature_map': feature_map,
            'app_map': app_map,
        }

        data = self.request(host=self.host, method='POST', api='/api/call/feature/conf/update', data=data)
        R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def mohs(self):
        self.list_page('mohs', 'mohs')

    def mohs_delete(self):
        self.list_delete('mohs', 'name')

    def mohs_add(self):
        data = self.user_login()
        R.log(data)

        for i in range(5):
            data_post = {
                'name': 'class' + str(i), 
                'mode': 'files', 
                'sort': 'random', 
                'directory': '/var/www/html/mohs/' + 'class' + str(i), 
                'files': [], 
            }
            data = self.request(host=self.host, method='POST', api='/api/mohs/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/mohs/update', data=data_post)
                R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def sip(self):
        data = self.user_login()
        R.log(data)
        data = self.request(host=self.host, api='/api/sip/conf')
        R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def sip_conf(self):
        data = self.user_login()
        R.log(data)

        data = {
            'sip_port': 5060,
            'rtp_port_range': [10000, 20000],
            'user_exten': [6000, 6299],
            'conference_exten': [6300, 6399],
            'ivr_exten': [7000, 7099],
            'ringgroup_exten': [7300, 7399],
        }

        data = self.request(host=self.host, method='POST', api='/api/sip/conf/update', data=data)
        R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def call_records(self):
        self.list_page('call/records', 'records')

    def call_records_delete(self):
        data = self.user_login()
        R.log(data)

        while True:
            data = self.request(host=self.host, api='/api/call/records/1/20', data=None)
            R.log(data)
            data = json.loads(data['result'])
            if not data['records']:
                break
            data = [plan['id'] for plan in data['records']]
            if not data:
                break
            data = self.request(host=self.host, method='POST', api='/api/call/records/delete', data=data)
            R.log(data)

        data = self.user_logout()
        R.log(data)

    def firewall_filters(self):
        self.list_page('firewall/filters', 'filters')

    def firewall_filters_del(self):
        data = self.user_login()
        R.log(data)

        while True:
            data = self.request(host=self.host, api='/api/firewall/filters/1/20', data=None)
            R.log(data)
            data = json.loads(data['result'])
            if not data["filters"]:
                break
            data = [plan['name'] for plan in data['filters']]
            if not data:
                break
            data = self.request(host=self.host, method='POST', api='/api/firewall/filters/delete', data=data)
            R.log(data)

        data = self.user_logout()
        R.log(data)

    def firewall_filters_add(self):
        data = self.user_login()
        R.log(data)

        for i in range(5):
            data_post = {'name': 'filter' + str(i) , 'ip': '192.168.1.225', 'port': 10086, 'proto': 'tcp', 'action': 'DROP'}
            data = self.request(host=self.host, method='POST', api='/api/firewall/filters/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/firewall/filters/update', data=data_post)
                R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def users(self):
        self.list_page('users', 'users')

    def users_delete(self):
        self.list_delete('users', 'name')

    def users_add(self):
        data = self.user_login()
        R.log(data)

        for i in range(5):
            data_post = {'name': 'user' + str(i) , 'password': '1314', 'permits': ['api']}
            data = self.request(host=self.host, method='POST', api='/api/users/add', data=data_post)
            R.log(data)
            data = json.loads(data['result'])
            if 0 != data['state']:
                data = self.request(host=self.host, method='POST', api='/api/users/update', data=data_post)
                R.log(data)
        
        data = self.user_logout()
        R.log(data)

    def conf_reload(self):
        data = self.user_login()
        R.log(data)

        data = self.request(host=self.host, api='/api/conf/reload')
        R.log(data)
        
        data = self.user_logout()
        R.log(data)


    def all(self):
        self.extensions_status()
        self.providers_status()
        self.parkings_status()
        self.meetingrooms_status()
        self.system_info()
        self.extensions()
        self.providers()
        self.ivrs()
        self.dialplans()
        self.dialrules()
        self.ringgroups()
        self.meetingrooms()
        self.voicemail()
        self.call_feature()
        self.mohs()
        self.sip()
        self.call_records()
        self.users()

    def all_delete(self):
        self.extensions_delete()
        self.providers_delete()
        self.ivrs_delete()
        self.dialplans_delete()
        self.dialrules_delete()
        self.ringgroups_delete()
        self.meetingrooms_delete()
        self.mohs_delete()
        self.call_records_delete()
        self.firewall_filters_del()
        self.users_delete()
        self.conf_reload()

    def all_add(self):
        self.extensions_add()
        self.providers_add()
        self.ivrs_add()
        self.dialrules_add()
        self.dialplans_add()
        self.ringgroups_add()
        self.meetingrooms_add()
        #self.dialrules_meetingrooms_add()
        self.voicemail_conf()
        self.call_feature_conf()
        self.mohs_add()
        self.sip_conf()
        self.firewall_filters_add()
        self.users_add()
        self.add_dialrule0()
        self.add_ivr0()
        self.conf_reload()

    def add_ivr0(self):
        data = self.user_login()
        R.log(data)

        rules = []
        rule = {
            'rule': 's', 
            'application': 'NoOp', 
            'args': ['ivr0'], 
        }

        rules.append(rule)

        rule = {
            'rule': 's', 
            'application': 'Background', 
            'args': ['basic-pbx-ivr-main'], 
        }

        rules.append(rule)

        rule = {
            'rule': 's', 
            'application': 'WaitExten', 
            'args': [5], 
        }

        rules.append(rule)

        rule = {
            'rule': '_[568]XXX', 
            'application': 'Goto', 
            'args': ['DLPN_systec' , '${EXTEN}' , '1'], 
        }

        rules.append(rule)

        data_post = {'name': 'ivr0', 'rules': rules}
        data = self.request(host=self.host, method='POST', api='/api/ivrs/add', data=data_post)
        R.log(data)
        data = json.loads(data['result'])
        if 0 != data['state']:
            data = self.request(host=self.host, method='POST', api='/api/ivrs/update', data=data_post)
            R.log(data)
 
        data = self.user_logout()
        R.log(data)

    def add_dialrule0(self):
        data = self.user_login()
        R.log(data)

        rules = []
        rule = {
            'rule': 's', 
            'application': 'Goto', 
            'args': ['DLPN_systec', '${SIP_HEADER(X-OfficeLink)}', '1'], 
            'strip': 0, 
            'prepend': '', 
            'filters': '',
        }

        rules.append(rule)

        rule = {
            'rule': '_8XXXXXX', 
            'application': 'Dial', 
            'args': ['SIP/80007/${EXTEN}'], 
            'strip': 0, 
            'prepend': '', 
            'filters': '',
        }

        rules.append(rule)

        rule = {
            'rule': '_8XXXXXX', 
            'application': 'Hangup', 
            'args': [], 
            'strip': 0, 
            'prepend': '', 
            'filters': '',
        }

        rules.append(rule)

        rule = {
            'rule': '_9.', 
            'application': 'Dial', 
            'args': ['SIP/PSTN/${EXTEN:1}'], 
            'strip': 0, 
            'prepend': '', 
            'filters': '',
        }

        rules.append(rule)

        rule = {
            'rule': '_9.', 
            'application': 'Hangup', 
            'args': [], 
            'strip': 0, 
            'prepend': '', 
            'filters': '',
        }

        rules.append(rule)

        rule = {
            'rule': '10000', 
            'application': 'VoiceMailMain', 
            'args': ['${CALLERID(num)}@default'], 
            'strip': 0, 
            'prepend': '', 
            'filters': '',
        }

        rules.append(rule)

        rule = {
            'rule': '10000', 
            'application': 'Hangup', 
            'args': [], 
            'strip': 0, 
            'prepend': '', 
            'filters': '',
        }

        rules.append(rule)

        rule = {
            'rule': '_8XX', 
            'application': 'Dial', 
            'args': ['SIP/80007/${EXTEN}7000'], 
            'strip': 0, 
            'prepend': '', 
            'filters': '',
        }

        rules.append(rule)

        data_post = {'name': 'rule0', 'rules': rules}
        data = self.request(host=self.host, method='POST', api='/api/dialrules/add', data=data_post)
        R.log(data)
        data = json.loads(data['result'])
        if 0 != data['state']:
            data = self.request(host=self.host, method='POST', api='/api/dialrules/update', data=data_post)
            R.log(data)
        
        data = self.user_logout()
        R.log(data)

def main(argv):
    case_list = ['help']
    host = '192.168.1.227'
    cookie = cookielib.CookieJar()
    user_name = 'admin'
    password = 'admin'
    reUser = re.compile('(\w+:\w+@){0,1}(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d{1,5}){0,1}')
    n = len(argv)
    if n > 1:
        case_list = argv[1:]
        for item in case_list:
            matchUser = reUser.match(item)
            if matchUser:
                if matchUser.group(1):
                    user_name, password = matchUser.group(1)[:-1].split(':')
                if matchUser.group(2):
                    host = matchUser.group(2)
                if matchUser.group(3):
                    host += matchUser.group(3)
                R.log('user_name: ' + user_name, 'password: ' + password, 'host: ' + host)
    if 'noprint' in case_list:
        R.logstdout = False
    if 'logfile' in case_list:
        R.logopen()
    for case_name in case_list:
        test = TestCase(
                case_name=case_name,
                host=host, 
                cookie=cookie,
                user_name=user_name,
                password=password,
            )
        test.run()

if __name__ == "__main__":
    main(sys.argv)

