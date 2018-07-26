PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS cdr (
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
DELETE FROM cdr;
COMMIT;
