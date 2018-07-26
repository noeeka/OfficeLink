#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, os.path, time
import threading
import datetime
import re, binascii, struct
import cookielib, urllib2, urllib, json
import sqlite3
import traceback

'''
apt-get install python-pip
pip install virtualenv
virtualenv hello
source hello/bin/activate
pip install pymysql
'''

'''
CREATE DATABASE `officelink` /*!40100 DEFAULT CHARACTER SET utf8 */;

CREATE TABLE `api_test_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `section` varchar(45) NOT NULL,
  `host` varchar(45) NOT NULL,
  `method` varchar(45) NOT NULL,
  `api` varchar(45) NOT NULL,
  `data` mediumtext,
  `result` mediumtext,
  `time` datetime NOT NULL,
  `duration` float NOT NULL,
  `code` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='api测试记录';
'''

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

class Sqlite3Test(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.realtime  = kwargs.get('realtime', '/var/lib/asterisk/realtime.sqlite3')
        self.master    = kwargs.get('master', '/var/log/asterisk/master.db')
        self.dbrecords = kwargs.get('dbrecords', 'dbrecords.db')

    def run(self):
        self.create_sippeers();R.log('create_sippeers')
        self.create_providers();R.log('create_providers')
        self.create_outrouters();R.log('create_outrouters')
        self.create_ivrs();R.log('create_ivrs')
        #self.create_dialplans();R.log('create_dialplans')
        #self.create_dialrules();R.log('create_dialrules')
        self.create_ringgroups();R.log('create_ringgroups')
        self.create_meetme();R.log('create_meetme')
        self.create_configs();R.log('create_configs')
        self.create_musiconhold();R.log('create_musiconhold')
        self.create_cdr();R.log('create_cdr')
        self.create_firewallfilters();R.log('create_firewallfilters')
        self.create_users();R.log('create_users')
        #self.create_backups();R.log('create_backups')
        self.create_records();R.log('create_records')

    def create_sippeers(self): #3.1
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS sippeers;
            CREATE TABLE sippeers (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                extension TEXT NOT NULL UNIQUE,
                nickname TEXT,
                photo TEXT,
                dialplan TEXT DEFAULT 'systec',
                password TEXT,
                transfer_days TEXT,
                transfer_time TEXT,
                transfer_style TEXT,
                transfer_type TEXT,
                transfer_target TEXT,
                ring_timeout TEXT DEFAULT '0',
                codecs TEXT NOT NULL DEFAULT '["u-law","h264"]',
                email TEXT,
                voicemail_pin TEXT,
                video TEXT DEFAULT 0
            );
            INSERT INTO sippeers (extension, nickname, photo, password, transfer_days, transfer_time, transfer_style, transfer_type, ring_timeout, voicemail_pin) values ('6000', '6000', '/img/avatar130.png', '6000', '[1,2,3,4,5]', '["08:30","19:30"]', 'absent', 'voicemail', '0', '1234');
            INSERT INTO sippeers (extension, nickname, photo, password, transfer_days, transfer_time, transfer_style, transfer_type, ring_timeout, voicemail_pin) values ('6001', '6001', '/img/avatar130.png', '6001', '[1,2,3,4,5]', '["08:30","19:30"]', 'absent', 'voicemail', '0', '1234');
            INSERT INTO sippeers (extension, nickname, photo, password, transfer_days, transfer_time, transfer_style, transfer_type, ring_timeout, voicemail_pin) values ('6002', '6002', '/img/avatar130.png', '6002', '[1,2,3,4,5]', '["08:30","19:30"]', 'absent', 'voicemail', '0', '1234');
            INSERT INTO sippeers (extension, nickname, photo, password, transfer_days, transfer_time, transfer_style, transfer_type, ring_timeout, voicemail_pin) values ('6003', '6003', '/img/avatar130.png', '6003', '[1,2,3,4,5]', '["08:30","19:30"]', 'absent', 'voicemail', '0', '1234');
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_providers(self): #3.2
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS providers;
            CREATE TABLE providers (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                user TEXT,
                password TEXT,
                address TEXT NOT NULL,
                port TEXT,
                dialplan TEXT,
                entry TEXT,
                type TEXT DEFAULT 'pstn'
            );
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_outrouters(self): #3.3
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS outrouters;
            CREATE TABLE outrouters (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                rule TEXT NOT NULL UNIQUE,
                provider TEXT NOT NULL,
                filter TEXT DEFAULT '0',
                append TEXT DEFAULT ''
            );
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_ivrs(self): # Interactive Voice Response #3.3
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS ivrs;
            CREATE TABLE ivrs (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                extension TEXT NOT NULL,
                music TEXT,
                timeout TEXT DEFAULT '5'
            );
            INSERT INTO ivrs (name, extension, music) values ('ivr0', '7000', 'basic-pbx-ivr-main');
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_dialplans(self): #3.4
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS dialplans;
            CREATE TABLE dialplans (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                rules TEXT NOT NULL
            );
            INSERT INTO dialplans (name, rules) values ('systec', '["rule0"]');
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_dialrules(self): #3.5
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS dialrules;
            CREATE TABLE dialrules (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                rules TEXT NOT NULL
            );
            INSERT INTO dialrules (name, rules) values ('rule0', '[{"rule":"s","application":"Goto","args":"DLPN_systec,${SIP_HEADER(X-OfficeLink)},1","strip":"0","prepend":"","filters":""},{"rule":"_8XXXXXX","application":"Dial","args":"SIP\/80003\/${EXTEN}","strip":"0","prepend":"","filters":""},{"rule":"_8XXXXXX","application":"Hangup","args":"","strip":"0","prepend":"","filters":""},{"rule":"_9.","application":"Dial","args":"SIP\/PSTN\/${EXTEN:1}","strip":"0","prepend":"","filters":""},{"rule":"_9.","application":"Hangup","args":"","strip":"0","prepend":"","filters":""},{"rule":"10000","application":"VoiceMailMain","args":"${CALLERID(num)}@default","strip":"0","prepend":"","filters":""},{"rule":"10000","application":"Hangup","args":"","strip":"0","prepend":"","filters":""}]');
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_ringgroups(self): #3.6
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS ringgroups;
            CREATE TABLE ringgroups (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                extension TEXT NOT NULL,
                ring_style TEXT NOT NULL,
                timeout TEXT NOT NULL,
                members TEXT NOT NULL
            );
            INSERT INTO ringgroups (name, extension, ring_style, timeout, members) values ('group0', '7300', 'all', '20', '["6000","6001","6002","6003"]');
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_meetme(self): #3.7
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS meetme;
            CREATE TABLE meetme (
                bookid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                confno TEXT NOT NULL UNIQUE,
                starttime TEXT,
                pin TEXT NOT NULL,
                adminpin TEXT,
                opts TEXT,
                adminopts TEXT,
                recordingfilename TEXT,
                recordingformat TEXT,
                maxusers TEXT,
                members TEXT
            );
            INSERT INTO meetme (confno, pin) values ('6030', '6030');
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_configs(self): #3.8
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS configs;
            CREATE TABLE configs (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                config TEXT NOT NULL UNIQUE,
                items TEXT
            );
            INSERT INTO configs (config, items) values ('sip', '{"sip_port": 5060, "rtp_port_range": [10000, 20000], "user_exten": [6000, 6299], "conference_exten": [6300, 6399], "ivr_exten": [7000, 7100], "ringgroup_exten": [6400, 6499]}');
            INSERT INTO configs (config, items) values ('voicemail', '{"extension": "10000", "dial_voicemail": false, "maxmessage": 20, "maxsec": 60, "minsec": 3, "greeting": false}');
            INSERT INTO configs (config, items) values ('callfeature', '{"digit_timeout": 500, "parking_res": {"extension": "700", "space": [701, 720], "timeout", 20}, "blind": "#1", "hungup": "*0", "transfer": "*2", "parking": "#72", "app_map": []}');
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_musiconhold(self): #3.9
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS musiconhold;
            CREATE TABLE musiconhold (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                mode TEXT NOT NULL,
                directory TEXT NOT NULL,
                application TEXT,
                digit TEXT,
                sort TEXT,
                format TEXT,
                stamp TEXT,
                files TEXT
            );
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_cdr(self): # Call Detial Record #3.10
        db = sqlite3.connect(self.master)
        sql = '''
            DROP TABLE IF EXISTS cdr;
            CREATE TABLE cdr (
                AcctId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                calldate TEXT,
                clid TEXT,
                cldid TEXT,
                dcontext TEXT,
                channel TEXT,
                dstchannel TEXT,
                lastapp TEXT,
                lastdata TEXT,
                duration TEXT,
                billsec TEXT,
                disposition TEXT,
                amaflags TEXT,
                accountcode TEXT,
                uniqueid TEXT,
                userfield TEXT,
                test TEXT
            );
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_firewallfilters(self): #3.11
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS firewallfilters;
            CREATE TABLE firewallfilters (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                ip TEXT NOT NULL,
                port TEXT NOT NULL,
                proto TEXT NOT NULL,
                action TEXT NOT NULL
            );
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_users(self): #3.12
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS users;
            CREATE TABLE users (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                permits TEXT NOT NULL
            );
            INSERT INTO users (name, password, permits) values ('admin', 'admin', '["gui"]');
            INSERT INTO users (name, password, permits) values ('client', 'client', '["api"]');
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_backups(self): #3.13
        db = sqlite3.connect(self.realtime)
        sql = '''
            DROP TABLE IF EXISTS backups;
            CREATE TABLE backups (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                remark TEXT,
                file TEXT NOT NULL,
                time TEXT NOT NULL
            );
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

    def create_records(self): #
        db = sqlite3.connect(self.dbrecords)
        sql = '''
            DROP TABLE IF EXISTS api_test_records;
            CREATE TABLE api_test_records (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                section TEXT NOT NULL,
                host TEXT NOT NULL,
                method TEXT NOT NULL,
                api TEXT NOT NULL,
                data TEXT,
                result TEXT,
                time TEXT NOT NULL,
                duration TEXT NOT NULL,
                code TEXT NOT NULL
            );
        '''
        c = db.cursor()
        c.executescript(sql)
        db.close()

class TestCase(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.case_name = kwargs.get('case_name', None)
        self.timeout   = kwargs.get('timeout', 2)
        self.cookie    = kwargs.get('cookie', cookielib.CookieJar())
        self.loops     = kwargs.get('loops', 1)
        self.case_name = kwargs.get('case_name', 'case')
        self.host      = kwargs.get('host', '192.168.1.157')
        self.user_name = kwargs.get('user_name', '6005')
        self.password  = kwargs.get('password', '6005')
        self.dbrecords = kwargs.get('dbrecords', 'dbrecords.db')
        self.dbconfig  = kwargs.get('dbconfig', {
            'host':'192.168.1.222',
            'port':3306,
            'user':'systec',
            'password':'123456',
            'db':'officelink',
            'charset': 'utf8',
        })
        self.dbconn = None
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.case_list = {
            'user_login'              : self.user_login_test,
            'user_logout'             : self.user_logout_test,

            'extensions_status_all'   : self.extensions_status_all_test,
            'extensions_status_page'  : self.extensions_status_page_test,

            'providers_status_all'    : self.providers_status_all_test,
            'providers_status_page'   : self.providers_status_page_test,

            'parkings_status_all'     : self.parkings_status_all_test,
            'parkings_status_page'    : self.parkings_status_page_test,

            'meetingrooms_status_all'   : self.meetingrooms_status_all_test,
            'meetingrooms_status_page'  : self.meetingrooms_status_page_test,

            'system_info'               : self.system_info_test,

            'extensions_all'          : self.extensions_all_test,
            'extensions_page'         : self.extensions_page_test,
            'contacts_page'           : self.contacts_page_test,
            'contacts_all'            : self.contacts_all_test,
            'extensions_add'          : self.extensions_add_test,
            'extensions_update'       : self.extensions_update_test,
            'extensions_delete'       : self.extensions_delete_test,

            'providers_all'          : self.providers_all_test,
            'providers_page'         : self.providers_page_test,
            'providers_add'          : self.providers_add_test,
            'providers_update'       : self.providers_update_test,
            'providers_delete'       : self.providers_delete_test,

            'ivrs_all'          : self.ivrs_all_test,
            'ivrs_page'         : self.ivrs_page_test,
            'ivrs_add'          : self.ivrs_add_test,
            'ivrs_update'       : self.ivrs_update_test,
            'ivrs_delete'       : self.ivrs_delete_test,

            'dialplans_all'          : self.dialplans_all_test,
            'dialplans_page'         : self.dialplans_page_test,
            'dialplans_add'          : self.dialplans_add_test,
            'dialplans_update'       : self.dialplans_update_test,
            'dialplans_delete'       : self.dialplans_delete_test,

            'dialrules_all'          : self.dialrules_all_test,
            'dialrules_page'         : self.dialrules_page_test,
            'dialrules_add'          : self.dialrules_add_test,
            'dialrules_update'       : self.dialrules_update_test,
            'dialrules_delete'       : self.dialrules_delete_test,

            'ringgroups_all'          : self.ringgroups_all_test,
            'ringgroups_page'         : self.ringgroups_page_test,
            'ringgroups_add'          : self.ringgroups_add_test,
            'ringgroups_update'       : self.ringgroups_update_test,
            'ringgroups_delete'       : self.ringgroups_delete_test,

            'meetingrooms_all'          : self.meetingrooms_all_test,
            'meetingrooms_page'         : self.meetingrooms_page_test,
            'meetingrooms_add'          : self.meetingrooms_add_test,
            'meetingrooms_update'       : self.meetingrooms_update_test,
            'meetingrooms_delete'       : self.meetingrooms_delete_test,

            'voicemail_conf'            : self.voicemail_conf_test,

            'call_feature_conf'         : self.call_feature_conf_test,

            'mohs_all'          : self.mohs_all_test,
            'mohs_page'         : self.mohs_page_test,
            'mohs_add'          : self.mohs_add_test,
            'mohs_update'       : self.mohs_update_test,
            'mohs_delete'       : self.mohs_delete_test,

            'sip_conf'            : self.sip_conf_test,

            'call_records_all'          : self.call_records_all_test,
            'call_records_page'         : self.call_records_page_test,
            'call_records_delete'       : self.call_records_delete_test,

            'language_conf'             : self.language_conf_test,

            'network_conf'              : self.network_conf_test,

            'datetime_conf'              : self.datetime_conf_test,

            'system_update'              : self.system_update_test,

            'factory_reset'              : self.factory_reset_test,
            'system_reboot'              : self.system_reboot_test,

            'backups_all'          : self.backups_all_test,
            'backups_page'         : self.backups_page_test,
            'backups_create'          : self.backups_create_test,
            'backups_restore'       : self.backups_restore_test,
            'backups_delete'       : self.backups_delete_test,

            'firewall_filters_all'          : self.firewall_filters_all_test,
            'firewall_filters_page'         : self.firewall_filters_page_test,
            'firewall_filters_add'          : self.firewall_filters_add_test,
            'firewall_filters_update'       : self.firewall_filters_update_test,
            'firewall_filters_delete'       : self.firewall_filters_delete_test,

            'logs'              : self.logs_test,

            'users_all'          : self.users_all_test,
            'users_page'         : self.users_page_test,
            'users_add'          : self.users_add_test,
            'users_update'       : self.users_update_test,
            'users_delete'       : self.users_delete_test,

            'create_database'      : self.create_database,
        }

    def run(self):
        if not self.case_list.has_key(self.case_name):
            # R.log(self.case_list.keys())
            return
        for i in range(0, self.loops):
            try:
                self.handler_sqlite3()
            except Exception, e:
                traceback.print_exc()
                R.log(e)
                time.sleep(1)
            else:
                pass
            finally:
                pass

    def handler(self):
        import pymysql
        self.dbconn = pymysql.connect(**self.dbconfig)
        cursor_record = self.dbconn.cursor(pymysql.cursors.DictCursor)
        items = self.case_list[self.case_name]
        for item in items():
            R.log(item)
            result = self.request(item['host'], item['method'], item['api'], item['data'])
            sql_record = "INSERT INTO `api_test_records` (`name`, `section`, `host`, `method`, `api`, `data`, `result`, `time`, `duration`, `code`) VALUES (%s, %s, %s, %s, %s, %s, %s, now(), %s, %s)"
            values = (item['name'], item['section'], item['host'], item['method'], item['api'], item['data'], result['data'], result['duration'], result['code'])
            R.log(values)
            cursor_record.execute(sql_record, values)
            self.dbconn.commit()
        self.dbconn.close()

    def handler_sqlite3(self):
        db = sqlite3.connect(self.dbrecords)
        cursor_record = db.cursor()
        items = self.case_list[self.case_name]
        for item in items():
            R.log(item)
            result = self.request(item['host'], item['method'], item['api'], item['data'])
            sql_record = "INSERT INTO api_test_records (name, section, host, method, api, data, result, time, duration, code) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'), ?, ?)"
            values = (item['name'], item['section'], item['host'], item['method'], item['api'], item['data'].decode('unicode_escape'), result['data'], result['duration'], result['code'])
            R.log(values)
            cursor_record.execute(sql_record, values)
        db.commit()
        db.close()

    def request(self, host, method, api, data):
        url = 'http://' + host + api
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json;charset=utf-8')

        result = {
            "code": 0, "data": None, "duration": 0,
        }
        time0 = time.time()
        if data:
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
            result["data"] = data.decode('unicode_escape').replace('\\/', '/')
        except urllib2.HTTPError, e:
            result["code"] = e.code
            result["data"] = e.read()
        except urllib2.URLError, e:
            result["data"] = repr(e)
        except Exception, e:
            result["data"] = repr(e)
            pass
        else:
            pass
        finally:
            pass
        result["duration"] = time.time() - time0
        return result

    def user_login(self):
        data = {'name': self.user_name, 'password': self.password}
        return {
            'name': self.case_name, 
            'section': '4.2.1', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/user/login', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def user_logout(self):
        return {
            'name': self.case_name, 
            'section': '4.2.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/user/logout', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def extensions_status(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/extensions/status'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.3', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def providers_status(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/providers/status'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.4', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def parkings_status(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/parkings/status'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.5', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def meetingrooms_status(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/meetingrooms/status'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.6', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def system_info(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.7', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/system/info', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def extensions(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/extensions'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.8.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def contacts(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/contacts'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.8.2', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def extensions_add(self, **kwargs):
        data = kwargs.get('data', {
                "extension": '6001', 
                "nickname": "Charles", 
                "photo": "/photos/6001.png", 
                "dialplan": "systec", 
                "password": "123456", 
                "email": "Charles@www.systec-pbx.net", 
                "voicemail_pin": "123456", 
                "codecs": ["u-law", "h264"], 
                "transfer_days": [1, 2, 3], 
                "transfer_time": ["08:30", "17:30"], 
                "transfer_style": "absent", 
                "transfer_type": "voicemail", 
                "transfer_target": "6002", 
                "ring_timeout": 30
            }
        )
        data['extension'] = kwargs.get('extension', data['extension'])
        data['photo'] = "/photos/" + data['extension'] + ".png"
        return {
            'name': self.case_name, 
            'section': '4.8.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/extensions/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def extensions_update(self, **kwargs):
        data = kwargs.get('data', {
                "extension": '6001', 
                "nickname": "Danae", 
                "photo": "/photos/6001.png", 
                "dialplan": "systec", 
                "password": "123456", 
                "email": "Charles@www.systec-pbx.net", 
                "voicemail_pin": "123456", 
                "codecs": ["u-law", "h264"], 
                "transfer_days": [1, 2, 3], 
                "transfer_time": ["08:30", "17:30"], 
                "transfer_style": "absent", 
                "transfer_type": "voicemail", 
                "transfer_target": "6002", 
                "ring_timeout": 30
            }
        )
        data['extension'] = kwargs.get('extension', data['extension'])
        data['photo'] = "/photos/" + data['extension'] + ".png"
        return {
            'name': self.case_name, 
            'section': '4.8.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/extensions/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def extensions_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.8.5', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/extensions/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def providers(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/providers'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.9.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def providers_add(self, **kwargs):
        data = kwargs.get('data', {
                "name": '6001', 
                "user": "80001", 
                "password": "80001", 
                "address": "www.systec-pbx.net", 
                "port": "5060", 
                "dialplan": "systec", 
                "entry": "7000",
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        data['user'] = data['name']
        data['password'] = data['name']
        return {
            'name': self.case_name, 
            'section': '4.9.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/providers/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def providers_update(self, **kwargs):
        data = kwargs.get('data', {
                "name": '6001', 
                "user": "80002", 
                "password": "80002", 
                "address": "www.systec-pbx.net", 
                "port": "5060", 
                "dialplan": "systec", 
                "entry": "7000",
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        data['user'] = data['name']
        data['password'] = data['name']
        return {
            'name': self.case_name, 
            'section': '4.9.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/providers/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def providers_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.9.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/providers/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def ivrs(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/ivrs'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.10.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def ivrs_add(self, **kwargs):
        rules = [
            {"rule": "6001", "application": "Dial", "args": ["SIP/6001", "m"]},
            {"rule": "6002", "application": "Dial", "args": ["SIP/6001", "m"]},
            {"rule": "6003", "application": "Dial", "args": ["SIP/6001", "m"]},
        ]
        data = kwargs.get('data', {
                "name": '6001', 
                "extension": "6001", 
                "rules": rules,
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        data['extension'] = data['name']
        return {
            'name': self.case_name, 
            'section': '4.10.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/ivrs/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def ivrs_update(self, **kwargs):
        rules = [
            {"rule": "6001", "application": "Dial", "args": ["SIP/6002", "m"]},
            {"rule": "6002", "application": "Dial", "args": ["SIP/6002", "m"]},
            {"rule": "6003", "application": "Dial", "args": ["SIP/6002", "m"]},
        ]
        data = kwargs.get('data', {
                "name": '6001', 
                "extension": "6001", 
                "rules": rules,
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        data['extension'] = data['name']
        return {
            'name': self.case_name, 
            'section': '4.10.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/ivrs/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def ivrs_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.10.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/ivrs/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def dialplans(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/dialplans'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.11.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def dialplans_add(self, **kwargs):
        rules = [
            'rule1', 'rule2', 'rule3'
        ]
        data = kwargs.get('data', {
                "name": '6001', 
                "rules": rules,
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.11.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/dialplans/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def dialplans_update(self, **kwargs):
        rules = [
            'rule1', 'rule2', 'rule3', 'rule4', 'rule5', 'rule6'
        ]
        data = kwargs.get('data', {
                "name": '6001', 
                "rules": rules,
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.11.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/dialplans/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def dialplans_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.11.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/dialplans/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def dialrules(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/dialrules'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.12.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def dialrules_add(self, **kwargs):
        rules = [
            {"rule": "6001", "application": "Dial", "args": ["SIP/6001", "m"], "strip": 2, "prepend": "022", "filters": "356"},
            {"rule": "6002", "application": "Dial", "args": ["SIP/6001", "m"], "strip": 2, "prepend": "022", "filters": "356"},
            {"rule": "6003", "application": "Dial", "args": ["SIP/6001", "m"], "strip": 2, "prepend": "022", "filters": "356"},
        ]
        data = kwargs.get('data', {
                "name": '6001', 
                "rules": rules,
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.12.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/dialrules/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def dialrules_update(self, **kwargs):
        rules = [
            {"rule": "6001", "application": "Dial", "args": ["SIP/6002", "m"], "strip": 2, "prepend": "022", "filters": "356"},
            {"rule": "6002", "application": "Dial", "args": ["SIP/6002", "m"], "strip": 2, "prepend": "022", "filters": "356"},
            {"rule": "6003", "application": "Dial", "args": ["SIP/6002", "m"], "strip": 2, "prepend": "022", "filters": "356"},
        ]
        data = kwargs.get('data', {
                "name": '6001', 
                "rules": rules,
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.12.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/dialrules/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def dialrules_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.12.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/dialrules/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def ringgroups(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/ringgroups'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.13.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def ringgroups_add(self, **kwargs):
        members = ['6001', '6002', '6003', '6004']
        data = kwargs.get('data', {
                "name": '6001', 
                "extension": '6001',
                'ring_style': 'all',
                'timeout': 10,
                'members': members,
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        data['extension'] = data['name']
        return {
            'name': self.case_name, 
            'section': '4.13.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/ringgroups/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def ringgroups_update(self, **kwargs):
        members = ['6001', '6002', '6003', '6004', '6005', '6006', '6007', '6008']
        data = kwargs.get('data', {
                "name": '6001', 
                "extension": '6001',
                'ring_style': 'all',
                'timeout': 10,
                'members': members,
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        data['extension'] = data['name']
        return {
            'name': self.case_name, 
            'section': '4.13.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/ringgroups/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def ringgroups_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.13.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/ringgroups/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def meetingrooms(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/meetingrooms'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.14.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def meetingrooms_add(self, **kwargs):
        data = kwargs.get('data', {
                "extension": '6001',
                'user_pin': '1111',
                'admin_pin': '11111',
            }
        )
        data['extension'] = kwargs.get('extension', data['extension'])
        return {
            'name': self.case_name, 
            'section': '4.14.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/meetingrooms/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def meetingrooms_update(self, **kwargs):
        data = kwargs.get('data', {
                "extension": '6001',
                'user_pin': '2222',
                'admin_pin': '22222',
            }
        )
        data['extension'] = kwargs.get('extension', data['extension'])
        return {
            'name': self.case_name, 
            'section': '4.14.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/meetingrooms/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def meetingrooms_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.14.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/meetingrooms/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def voicemail_conf(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.15.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/voicemail/conf', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def voicemail_conf_update(self, **kwargs):
        data = kwargs.get('data', {
                "extension": '10000',
                'dial_viocemail': True,
                'maxmessage': 20,
                'maxsec': 60,
                'minsec': 20,
                'greating': True,
            }
        )
        return {
            'name': self.case_name, 
            'section': '4.15.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/voicemail/conf/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def call_feature_conf(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.16.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/call/feature/conf', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def call_feature_conf_update(self, **kwargs):
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
        data = kwargs.get('data', {
                "digit_timeout": 1000,
                'parking': parking,
                'feature_map': feature_map,
                'app_map': app_map,
            }
        )
        return {
            'name': self.case_name, 
            'section': '4.16.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/voicemail/conf/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def mohs(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/mohs'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.17.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def mohs_add(self, **kwargs):
        data = kwargs.get('data', {
                "name": '6001',
                'mode': 'files',
                'sort': 'random',
                'directory': '/var/lib/asterisk/mohs',
                'files': [],
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.17.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/mohs/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def mohs_update(self, **kwargs):
        data = kwargs.get('data', {
                "name": '6001',
                'mode': 'files',
                'sort': 'random',
                'directory': '/var/lib/asterisk/mohs2',
                'files': [],
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.17.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/mohs/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def mohs_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.17.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/mohs/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def sip_conf(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.18.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/sip/conf', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def sip_conf_update(self, **kwargs):
        data = kwargs.get('data', {
                "sip_port": 5060,
                'rtp_port_range': [10000, 20000],
                'user_exten': [6300, 6500],
                'conference_exten': [6501, 6600],
                'ivr_exten': [6601, 6700],
                'ringgroup_exten': [6701, 6800],
            }
        )
        return {
            'name': self.case_name, 
            'section': '4.18.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/sip/conf/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def call_records(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/call/records'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.19.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def call_records_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.19.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/call/records/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def language_conf(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.20.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/language', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def language_conf_update(self, **kwargs):
        data = kwargs.get('data', {'language': 'en'})
        return {
            'name': self.case_name, 
            'section': '4.20.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/language/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def network_conf(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.21.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/network', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def network_conf_update(self, **kwargs):
        data = kwargs.get('data', {
                'hostname': 'officelink',
                'ip': '192.168.1.159',
                'gateway': '192.168.1.1',
                'netmask': '255.255.255.0',
                'dns': ['192.168.1.1', '8.8.8.8'],
                'dhcp': False,
            }
        )
        return {
            'name': self.case_name, 
            'section': '4.21.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/network/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def datetime_conf(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.22.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/datetime', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def datetime_conf_update(self, **kwargs):
        data = kwargs.get('data', {
                'timezone': 'Shanghai',
                'date': '2016.10.10',
                'time': '21:0:21',
                'ntp': False,
                'ntpserver': 's1b.time.edu.cn',
            }
        )
        return {
            'name': self.case_name, 
            'section': '4.22.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/datetime/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def system_update(self, **kwargs):
        data = kwargs.get('data', {
                'file': '',
            }
        )
        return {
            'name': self.case_name, 
            'section': '4.23.1', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/system/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def factory_reset(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.24', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/factory/reset', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def system_reboot(self, **kwargs):
        return {
            'name': self.case_name, 
            'section': '4.25', 
            'host': self.host, 
            'method': 'GET', 
            'api': '/api/system/reboot', 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def backups(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/backups'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.26.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def backups_create(self, **kwargs):
        data = kwargs.get('data', {
                "name": '6001',
                'remark': 'office',
                'time': '2016-10-10 21:10:20',
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.26.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/backups/create', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def backups_restore(self, **kwargs):
        data = kwargs.get('data', {
                "name": '6001',
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.26.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/backups/restore', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def backups_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.26.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/backups/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def firewall_filters(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/firewall/filters'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.27.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def firewall_filters_add(self, **kwargs):
        data = kwargs.get('data', {
                "name": '6001',
                'ip': '192.168.1.225',
                'port': 5060,
                'proto': 'tcp',
                'action': 'DROP',
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.27.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/firewall/filters/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def firewall_filters_update(self, **kwargs):
        data = kwargs.get('data', {
                "name": '6001',
                'ip': '192.168.1.225',
                'port': 5060,
                'proto': 'udp',
                'action': 'ACCEPT',
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.27.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/firewall/filters/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def firewall_filters_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.27.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/firewall/filters/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def logs(self, **kwargs):
        year = kwargs.get('year', 2016)
        month = kwargs.get('month', 10)
        day = kwargs.get('day', 10)
        api = '/api/logs/' + str(year) + '/' + str(month) + '/' + str(day)
        return {
            'name': self.case_name, 
            'section': '4.28.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def users(self, **kwargs):
        page = kwargs.get('page')
        page_size = kwargs.get('page_size')
        api = '/api/users'
        if page and page_size:
            api += '/' + str(page) + '/' + str(page_size)
        return {
            'name': self.case_name, 
            'section': '4.29.1', 
            'host': self.host, 
            'method': 'GET', 
            'api': api, 
            'data': '', 
            'reuslt': '', 
            'duration': 0.1,
        }

    def users_add(self, **kwargs):
        data = kwargs.get('data', {
                "name": 'admin',
                'password': 'admin',
                'permits': ['gui'],
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.29.2', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/users/add', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def users_update(self, **kwargs):
        data = kwargs.get('data', {
                "name": 'admin',
                'password': 'admin',
                'permits': ['api'],
            }
        )
        data['name'] = kwargs.get('name', data['name'])
        return {
            'name': self.case_name, 
            'section': '4.29.3', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/users/update', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def users_delete(self, **kwargs):
        data = kwargs.get('data', [""])
        return {
            'name': self.case_name, 
            'section': '4.29.4', 
            'host': self.host, 
            'method': 'POST', 
            'api': '/api/users/delete', 
            'data': json.dumps(data), 
            'reuslt': '', 
            'duration': 0.1,
        }

    def user_login_test(self):
        yield self.user_login()

    def user_logout_test(self):
        yield self.user_logout()

    def extensions_status_all_test(self):
        yield self.extensions_status()

    def extensions_status_page_test(self):
        for i in range(1, 30):
            yield self.extensions_status(page=i, page_size=20)

    def providers_status_all_test(self):
        yield self.providers_status()

    def providers_status_page_test(self):
        for i in range(1, 30):
            yield self.providers_status(page=i, page_size=20)

    def parkings_status_all_test(self):
        yield self.parkings_status()

    def parkings_status_page_test(self):
        for i in range(1, 30):
            yield self.parkings_status(page=i, page_size=20)

    def meetingrooms_status_all_test(self):
        yield self.parkings_status()

    def meetingrooms_status_page_test(self):
        for i in range(1, 30):
            yield self.parkings_status(page=i, page_size=20)

    def system_info_test(self):
        yield self.system_info()

    def extensions_all_test(self):
        yield self.extensions()

    def extensions_page_test(self):
        for i in range(1, 30):
            yield self.extensions(page=i, page_size=20)

    def contacts_all_test(self):
        yield self.contacts()

    def contacts_page_test(self):
        for i in range(1, 30):
            yield self.contacts(page=i, page_size=20)

    def extensions_add_test(self):
        for i in range(6000, 6030):
            yield self.extensions_add(extension=str(i))

    def extensions_update_test(self):
        for i in range(6000, 6030):
            yield self.extensions_update(extension=str(i))

    def extensions_delete_test(self):
        yield self.extensions_delete()
        for i in  range(6000, 6030):
            yield self.extensions_delete(data=[str(i+x) for x in range(10)])

    def providers_all_test(self):
        yield self.providers()

    def providers_page_test(self):
        for i in range(1, 30):
            yield self.providers(page=i, page_size=20)

    def providers_add_test(self):
        for i in range(0, 30):
            yield self.providers_add(name='provider_'+str(i))

    def providers_update_test(self):
        for i in range(0, 30):
            yield self.providers_update(name='provider_'+str(i))

    def providers_delete_test(self):
        yield self.providers_delete()
        for i in  range(0, 30):
            yield self.providers_delete(data=['provider_' + str(i+x) for x in range(10)])

    def ivrs_all_test(self):
        yield self.ivrs()

    def ivrs_page_test(self):
        for i in range(1, 30):
            yield self.ivrs(page=i, page_size=20)

    def ivrs_add_test(self):
        for i in range(0, 30):
            yield self.ivrs_add(name='ivr_' + str(i))

    def ivrs_update_test(self):
        for i in range(0, 30):
            yield self.ivrs_update(name='ivr_' + str(i))

    def ivrs_delete_test(self):
        yield self.ivrs_delete()
        for i in  range(0, 30):
            yield self.ivrs_delete(data=['ivr_' + str(i+x) for x in range(10)])

    def dialplans_all_test(self):
        yield self.dialplans()

    def dialplans_page_test(self):
        for i in range(1, 30):
            yield self.dialplans(page=i, page_size=20)

    def dialplans_add_test(self):
        for i in range(0, 30):
            yield self.dialplans_add(name='dialplan_' + str(i))

    def dialplans_update_test(self):
        for i in range(0, 30):
            yield self.dialplans_update(name='dialplan_' + str(i))

    def dialplans_delete_test(self):
        yield self.dialplans_delete()
        for i in  range(0, 30):
            yield self.dialplans_delete(data=['dialplan_' + str(i+x) for x in range(10)])

    def dialrules_all_test(self):
        yield self.dialrules()

    def dialrules_page_test(self):
        for i in range(1, 30):
            yield self.dialrules(page=i, page_size=20)

    def dialrules_add_test(self):
        for i in range(0, 30):
            yield self.dialrules_add(name='dialrule_' + str(i))

    def dialrules_update_test(self):
        for i in range(6000, 6051):
            yield self.dialrules_update(name='dialrule_' + str(i))

    def dialrules_delete_test(self):
        yield self.dialrules_delete()
        for i in  range(0, 30):
            yield self.dialrules_delete(data=['dialrule_' + str(i+x) for x in range(10)])

    def ringgroups_all_test(self):
        yield self.ringgroups()

    def ringgroups_page_test(self):
        for i in range(1, 30):
            yield self.ringgroups(page=i, page_size=20)

    def ringgroups_add_test(self):
        for i in range(0, 30):
            yield self.ringgroups_add(name='ringgroup_' + str(i))

    def ringgroups_update_test(self):
        for i in range(0, 30):
            yield self.ringgroups_update(name='ringgroup_' + str(i))

    def ringgroups_delete_test(self):
        yield self.ringgroups_delete()
        for i in  range(0, 100):
            yield self.ringgroups_delete(data=['ringgroup_' + str(i+x) for x in range(10)])

    def meetingrooms_all_test(self):
        yield self.meetingrooms()

    def meetingrooms_page_test(self):
        for i in range(1, 30):
            yield self.meetingrooms(page=i, page_size=20)

    def meetingrooms_add_test(self):
        for i in range(6300, 6330):
            yield self.meetingrooms_add(extension=str(i))

    def meetingrooms_update_test(self):
        for i in range(6300, 6330):
            yield self.meetingrooms_update(extension=str(i))

    def meetingrooms_delete_test(self):
        yield self.meetingrooms_delete()
        for i in  range(6300, 6330):
            yield self.meetingrooms_delete(data=[str(i+x) for x in range(10)])

    def voicemail_conf_test(self):
        yield self.voicemail_conf_update()
        yield self.voicemail_conf()

    def call_feature_conf_test(self):
        yield self.call_feature_conf_update()
        yield self.call_feature_conf()

    def mohs_all_test(self):
        yield self.mohs()

    def mohs_page_test(self):
        for i in range(1, 30):
            yield self.mohs(page=i, page_size=20)

    def mohs_add_test(self):
        for i in range(0, 30):
            yield self.mohs_add(name='moh_' + str(i))

    def mohs_update_test(self):
        for i in range(0, 30):
            yield self.mohs_update(name='moh_' + str(i))

    def mohs_delete_test(self):
        yield self.mohs_delete()
        for i in  range(0, 30):
            yield self.mohs_delete(data=['moh_' + str(i+x) for x in range(10)])

    def sip_conf_test(self):
        yield self.sip_conf_update()
        yield self.sip_conf()

    def call_records_all_test(self):
        yield self.call_records()

    def call_records_page_test(self):
        for i in range(1, 30):
            yield self.call_records(page=i, page_size=20)

    def call_records_delete_test(self):
        yield self.call_records_delete()
        for i in  range(0, 30):
            yield self.call_records_delete(data=[str(i+x) for x in range(10)])

    def language_conf_test(self):
        yield self.language_conf_update()
        yield self.language_conf()

    def network_conf_test(self):
        yield self.network_conf_update()
        yield self.network_conf()

    def datetime_conf_test(self):
        yield self.datetime_conf_update()
        yield self.datetime_conf()

    def system_update_test(self):
        yield self.system_update()

    def factory_reset_test(self):
        yield self.factory_reset()

    def system_reboot_test(self):
        yield self.system_reboot()

    def backups_all_test(self):
        yield self.backups()

    def backups_page_test(self):
        for i in range(1, 30):
            yield self.backups(page=i, page_size=20)

    def backups_create_test(self):
        for i in range(0, 5):
            yield self.backups_create(name='backup_' + str(i))

    def backups_restore_test(self):
        yield self.backups_restore(name='backup_' + str(0))

    def backups_delete_test(self):
        yield self.backups_delete()
        for i in  range(0, 5):
            yield self.backups_delete(data=['backup_' + str(i+x) for x in range(10)])

    def firewall_filters_all_test(self):
        yield self.firewall_filters()

    def firewall_filters_page_test(self):
        for i in range(1, 30):
            yield self.firewall_filters(page=i, page_size=20)

    def firewall_filters_add_test(self):
        for i in range(0, 30):
            yield self.firewall_filters_add(name='filter_' + str(i))

    def firewall_filters_update_test(self):
        for i in range(0, 30):
            yield self.firewall_filters_update(name='filter_' + str(i))

    def firewall_filters_delete_test(self):
        yield self.firewall_filters_delete()
        for i in  range(0, 30):
            yield self.firewall_filters_delete(data=['filter_' + str(i+x) for x in range(10)])

    def logs_test(self):
        yield self.logs()

    def users_all_test(self):
        yield self.users()

    def users_page_test(self):
        for i in range(1, 30):
            yield self.users(page=i, page_size=20)

    def users_add_test(self):
        for i in range(0, 30):
            yield self.users_add(name='user_' + str(i))

    def users_update_test(self):
        for i in range(0, 30):
            yield self.users_update(name='user_' + str(i))

    def users_delete_test(self):
        yield self.users_delete()
        for i in  range(0, 30):
            yield self.users_delete(data=['user_' + str(i+x) for x in range(10)])

    def create_database(self):
        test = Sqlite3Test(realtime='realtime.sqlite3', master='master.db')
        test.run()
        return []

class TestCaseGroup(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.group_name  = kwargs.get('group_name', 'help')
        self.host        = kwargs.get('host', '192.168.1.157')
        self.user_name   = kwargs.get('user_name', '6005')
        self.password    = kwargs.get('password', '6005')
        self.cookie      = kwargs.get('cookie', cookielib.CookieJar())
        self.group_list  = {
            'install': ['create_database'],
            'all': [
                'user_login', 

                'extensions_status_all',
                'extensions_status_page',

                'providers_status_all',
                'providers_status_page',

                'parkings_status_all',
                'parkings_status_page',

                'meetingrooms_status_all',
                'meetingrooms_status_page',

                'system_info',

                'extensions_delete',
                'extensions_add',
                'extensions_update',
                'extensions_all',
                'extensions_page',
                'contacts_page',
                'contacts_all',

                'providers_delete',
                'providers_add',
                'providers_update',
                'providers_all',
                'providers_page',

                'ivrs_delete',
                'ivrs_add',
                'ivrs_update',
                'ivrs_all',
                'ivrs_page',

                'dialplans_delete',
                'dialplans_add',
                'dialplans_update',
                'dialplans_all',
                'dialplans_page',

                'dialrules_delete',
                'dialrules_add',
                'dialrules_update',
                'dialrules_all',
                'dialrules_page',

                'ringgroups_delete',
                'ringgroups_add',
                'ringgroups_update',
                'ringgroups_all',
                'ringgroups_page',

                'meetingrooms_delete',
                'meetingrooms_add',
                'meetingrooms_update',
                'meetingrooms_all',
                'meetingrooms_page',

                'voicemail_conf',

                'call_feature_conf',

                'mohs_delete',
                'mohs_add',
                'mohs_update',
                'mohs_all',
                'mohs_page',

                'sip_conf',

                'call_records_all',
                'call_records_page',
                'call_records_delete',

                'language_conf',

                'network_conf',

                'datetime_conf',

                'system_update',

                'factory_reset',
                # 'system_reboot',

                'backups_all',
                'backups_page',
                'backups_create',
                'backups_restore',
                'backups_delete',

                'firewall_filters_delete',
                'firewall_filters_add',
                'firewall_filters_update',
                'firewall_filters_all',
                'firewall_filters_page',

                'logs',

                'users_delete',
                'users_add',
                'users_update',
                'users_all',
                'users_page',

                'user_logout',
            ],
            'all-notlogin': [
                'extensions_status_all',
                'extensions_status_page',

                'providers_status_all',
                'providers_status_page',

                'parkings_status_all',
                'parkings_status_page',

                'meetingrooms_status_all',
                'meetingrooms_status_page',

                'system_info',

                'extensions_delete',
                'extensions_add',
                'extensions_update',
                'extensions_all',
                'extensions_page',
                'contacts_page',
                'contacts_all',

                'providers_delete',
                'providers_add',
                'providers_update',
                'providers_all',
                'providers_page',

                'ivrs_delete',
                'ivrs_add',
                'ivrs_update',
                'ivrs_all',
                'ivrs_page',

                'dialplans_delete',
                'dialplans_add',
                'dialplans_update',
                'dialplans_all',
                'dialplans_page',

                'dialrules_delete',
                'dialrules_add',
                'dialrules_update',
                'dialrules_all',
                'dialrules_page',

                'ringgroups_delete',
                'ringgroups_add',
                'ringgroups_update',
                'ringgroups_all',
                'ringgroups_page',

                'meetingrooms_delete',
                'meetingrooms_add',
                'meetingrooms_update',
                'meetingrooms_all',
                'meetingrooms_page',

                'voicemail_conf',

                'call_feature_conf',

                'mohs_delete',
                'mohs_add',
                'mohs_update',
                'mohs_all',
                'mohs_page',

                'sip_conf',

                'call_records_all',
                'call_records_page',
                'call_records_delete',

                'language_conf',

                'network_conf',

                'datetime_conf',

                'system_update',

                'factory_reset',
                # 'system_reboot',

                'backups_all',
                'backups_page',
                'backups_create',
                'backups_restore',
                'backups_delete',

                'firewall_filters_delete',
                'firewall_filters_add',
                'firewall_filters_update',
                'firewall_filters_all',
                'firewall_filters_page',

                'logs',

                'users_delete',
                'users_add',
                'users_update',
                'users_all',
                'users_page',
            ],
            'test': [
                'user_login',
                'dialplans_page',
                'dialrules_page',
                'user_logout',
            ],
        }

    def run(self):
        if 'help' == self.group_name:
            for key, value in self.group_list.items():
                R.log(key, value)
        if not self.group_list.has_key(self.group_name):
            return
        for case_name in self.group_list[self.group_name]:
            test_case = TestCase(
                    case_name=case_name, 
                    host=self.host, 
                    cookie=self.cookie,
                    user_name=self.user_name,
                    password=self.password,
                    timeout=5,
                )
            test_case.run()

def main(argv):
    group_list = ['help']
    host = '192.168.1.157'
    cookie = cookielib.CookieJar()
    user_name = 'admin'
    password = 'admin'
    reUser = re.compile('(\w+:\w+@){0,1}(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d{1,5}){0,1}')
    n = len(argv)
    if n > 1:
        group_list = argv[1:]
        for item in group_list:
            matchUser = reUser.match(item)
            if matchUser:
                if matchUser.group(1):
                    user_name, password = matchUser.group(1)[:-1].split(':')
                if matchUser.group(2):
                    host = matchUser.group(2)
                if matchUser.group(3):
                    host += matchUser.group(3)
                R.log('user_name: ' + user_name, 'password: ' + password, 'host: ' + host)
    if 'noprint' in group_list:
        R.logstdout = False
    if 'logfile' in group_list:
        R.logopen()
    for group_name in group_list:
        test_group = TestCaseGroup(
                group_name=group_name,
                host=host, 
                cookie=cookie,
                user_name=user_name,
                password=password,
            )
        test_group.run()

if __name__ == "__main__":
    main(sys.argv)
