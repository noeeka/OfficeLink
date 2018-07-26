-- Adminer 4.2.4 SQLite 3 dump

DROP TABLE IF EXISTS "musiconhold";
CREATE TABLE "musiconhold" (
  "name" text NOT NULL,
  "mode" text NOT NULL DEFAULT 'files',
  "directory" text NOT NULL,
  "application" text NULL,
  "digit" text NULL,
  "sort" text NULL,
  "format" text NULL,
  "stamp" text NULL
);

CREATE UNIQUE INDEX "musiconhold_name" ON "musiconhold" ("name");

INSERT INTO "musiconhold" ("name", "mode", "directory", "application", "digit", "sort", "format", "stamp") VALUES ('systec',	'files',	'/home/ygz/systec',	NULL,	NULL,	NULL,	NULL,	NULL);

DROP TABLE IF EXISTS "sippeers";
CREATE TABLE "sippeers" (
  "name" text NOT NULL,
  "ipaddr" text NULL,
  "port" integer NULL,
  "regseconds" integer NULL,
  "defaultuser" text NULL,
  "fullcontact" text NULL,
  "regserver" text NULL,
  "useragent" text NULL,
  "lastms" integer NULL,
  "host" text NOT NULL DEFAULT 'dynamic',
  "type" text NOT NULL DEFAULT 'peer',
  "context" text NOT NULL DEFAULT 'DLPN_systec',
  "secret" text NULL,
  "nat" text NULL DEFAULT 'force_rport,comedia',
  "disallow" text NULL,
  "allow" text NULL DEFAULT 'ulaw,h264',
  "callerid" text NULL,
  "mailbox" text NULL,
  "vmexten" text NULL
);

CREATE UNIQUE INDEX "sippeers_name" ON "sippeers" ("name");

INSERT INTO "sippeers" ("name", "ipaddr", "port", "regseconds", "defaultuser", "fullcontact", "regserver", "useragent", "lastms", "host", "type", "context", "secret", "nat", "disallow", "allow", "callerid", "mailbox", "vmexten") VALUES ('5001',	'192.168.43.1',	5061,	1475574972,	'5001',	'sip:5001@192.168.43.1:5061;ob',	'',	'PJSUA v2.5.5 Darwin-15.6/x86_64',	'0',	'dynamic',	'peer',	'DLPN_systec',	'1234',	'force_rport,comedia',	NULL,	'ulaw,h264',	NULL,	'5001',	'10000');
INSERT INTO "sippeers" ("name", "ipaddr", "port", "regseconds", "defaultuser", "fullcontact", "regserver", "useragent", "lastms", "host", "type", "context", "secret", "nat", "disallow", "allow", "callerid", "mailbox", "vmexten") VALUES ('5002',	'192.168.43.1',	5062,	1475503995,	'5002',	'sip:5002@192.168.43.1:5062;ob',	'',	'PJSUA v2.5.5 Darwin-15.6/x86_64',	'0',	'dynamic',	'peer',	'DLPN_systec',	'1234',	'force_rport,comedia',	NULL,	'ulaw,h264',	NULL,	'5002',	'10000');

DROP TABLE IF EXISTS "voicemail";
CREATE TABLE "voicemail" (
  "uniqueid" integer NULL PRIMARY KEY AUTOINCREMENT,
  "mailbox" text NOT NULL,
  "password" text NOT NULL,
  "context" text NOT NULL DEFAULT 'default',
  "fullname" text NULL
);

CREATE UNIQUE INDEX "voicemail_mailbox" ON "voicemail" ("mailbox");

INSERT INTO "voicemail" ("uniqueid", "mailbox", "password", "context", "fullname") VALUES (1,	'5001',	'1234',	'default',	NULL);
INSERT INTO "voicemail" ("uniqueid", "mailbox", "password", "context", "fullname") VALUES (2,	'5002',	'1234',	'default',	NULL);

-- 

