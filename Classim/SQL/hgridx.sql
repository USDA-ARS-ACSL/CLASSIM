BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "hgridx" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"gridx_id"	INTEGER NOT NULL,
	"x"	REAL NOT NULL
);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (16,2,0.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (17,2,0.5);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (18,2,1.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (19,2,2.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (20,2,3.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (21,2,4.5);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (22,2,6.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (23,2,8.5);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (24,2,11.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (25,2,14.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (26,2,19.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (27,2,23.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (28,2,27.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (29,2,33.0);
INSERT INTO "hgridx" ("id","gridx_id","x") VALUES (30,2,40.0);
COMMIT;
