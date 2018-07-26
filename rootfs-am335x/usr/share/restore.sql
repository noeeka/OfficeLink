PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS sippeers (
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
CREATE TABLE IF NOT EXISTS providers (
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
CREATE TABLE IF NOT EXISTS outrouters (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                rule TEXT NOT NULL UNIQUE,
                provider TEXT NOT NULL,
                filter TEXT DEFAULT '0',
                append TEXT DEFAULT ''
            );
CREATE TABLE IF NOT EXISTS ivrs (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                extension TEXT NOT NULL,
                music TEXT,
                timeout TEXT DEFAULT '5'
            );
CREATE TABLE IF NOT EXISTS ringgroups (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                extension TEXT NOT NULL,
                ring_style TEXT NOT NULL,
                timeout TEXT NOT NULL,
                members TEXT NOT NULL
            );
CREATE TABLE IF NOT EXISTS meetme (
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
CREATE TABLE IF NOT EXISTS configs (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                config TEXT NOT NULL UNIQUE,
                items TEXT
            );
CREATE TABLE IF NOT EXISTS musiconhold (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                mode TEXT NOT NULL DEFAULT 'files',
                directory TEXT NOT NULL,
                application TEXT,
                digit TEXT,
                sort TEXT,
                format TEXT,
                stamp TEXT,
                files TEXT
            );
CREATE TABLE IF NOT EXISTS firewallfilters (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                ip TEXT NOT NULL,
                port TEXT NOT NULL,
                proto TEXT NOT NULL,
                action TEXT NOT NULL
            );
CREATE TABLE IF NOT EXISTS users (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                permits TEXT NOT NULL
            );

DELETE FROM sippeers;
DELETE FROM providers;
DELETE FROM outrouters;
DELETE FROM ivrs;
DELETE FROM ringgroups;
DELETE FROM meetme;
DELETE FROM configs;
DELETE FROM musiconhold;
DELETE FROM firewallfilters;
DELETE FROM users;

-- INSERT INTO "sippeers" VALUES(1,'6000','6000','/img/avatar130.png','systec','6000','[1,2,3,4,5]','["08:30","19:30"]','absent','voicemail',NULL,'0','["u-law","h264"]',NULL,'1234','0');
-- INSERT INTO "sippeers" VALUES(2,'6001','6001','/img/avatar130.png','systec','6001','[1,2,3,4,5]','["08:30","19:30"]','absent','voicemail',NULL,'0','["u-law","h264"]',NULL,'1234','0');
-- INSERT INTO "sippeers" VALUES(3,'6002','6002','/img/avatar130.png','systec','6002','[1,2,3,4,5]','["08:30","19:30"]','absent','voicemail',NULL,'0','["u-law","h264"]',NULL,'1234','0');
-- INSERT INTO "sippeers" VALUES(4,'6003','6003','/img/avatar130.png','systec','6003','[1,2,3,4,5]','["08:30","19:30"]','absent','voicemail',NULL,'0','["u-law","h264"]',NULL,'1234','0');

-- INSERT INTO "ivrs" VALUES(1,'ivr0','7000','basic-pbx-ivr-main','5');

-- INSERT INTO "ringgroups" VALUES(1,'group0','7300','all','20','["6000","6001","6002","6003"]');

-- INSERT INTO "meetme" VALUES(1,'6030',NULL,'6030',NULL,NULL,NULL,NULL,NULL,NULL,NULL);

INSERT INTO "configs" VALUES(1,'sip','{"sip_port": 5060, "rtp_port_range": [10000, 20000], "user_exten": [6000, 6299], "conference_exten": [6300, 6399], "ivr_exten": [7000, 7100], "ringgroup_exten": [6400, 6499]}');
INSERT INTO "configs" VALUES(2,'voicemail','{"extension": "10000", "dial_voicemail": false, "maxmessage": 10, "maxsec": 30, "minsec": 2, "greeting": false}');
INSERT INTO "configs" VALUES(3,'callfeature','{"digit_timeout": 500, "parking_res": {"extension": "700", "space": [701, 720], "timeout": 60}, "blind": "#1", "hungup": "*0", "transfer": "#2", "parking": "#3", "app_map": []}');

INSERT INTO "users" VALUES(1,'admin','admin','["gui"]');
INSERT INTO "users" VALUES(2,'client','client','["api"]');

DELETE FROM sqlite_sequence;
INSERT INTO "sqlite_sequence" VALUES('sippeers',4);
INSERT INTO "sqlite_sequence" VALUES('ivrs',1);
INSERT INTO "sqlite_sequence" VALUES('ringgroups',1);
INSERT INTO "sqlite_sequence" VALUES('meetme',1);
INSERT INTO "sqlite_sequence" VALUES('configs',3);
INSERT INTO "sqlite_sequence" VALUES('users',2);
COMMIT;
