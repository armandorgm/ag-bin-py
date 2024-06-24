BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "reference_price" (
	"id"	INTEGER NOT NULL,
	"price"	FLOAT NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "pending_operation" (
	"id"	INTEGER NOT NULL,
	"exchangeId"	TEXT NOT NULL,
	"position_side"	VARCHAR NOT NULL,
	"amount"	FLOAT NOT NULL,
	"entry_price"	FLOAT NOT NULL,
	"open_fee"	TEXT NOT NULL,
	"closing_price"	FLOAT NOT NULL,
	"close_fee"	FLOAT,
	"status"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
INSERT INTO "pending_operation" VALUES (1,'11903857728','LONG',43.0,0.11658,'null',0.116684922,NULL,'open');
COMMIT;
