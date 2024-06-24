BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "order_status" (
	"id"	INTEGER NOT NULL UNIQUE,
	"status"	TEXT NOT NULL,
	"operation_id"	INTEGER NOT NULL,
	"type"	TEXT NOT NULL,
	"reduce_only"	INTEGER NOT NULL,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "profit_operations" (
	"id"	INTEGER UNIQUE,
	"open_order_id"	INTEGER UNIQUE,
	"take_profit_order_id"	INTEGER,
	"bot_operation_id"	INTEGER NOT NULL,
	"slot_price"	INTEGER NOT NULL,
	FOREIGN KEY("bot_operation_id") REFERENCES "bot_operations"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "strategies" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "symbols" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "bot_operations" (
	"id"	INTEGER UNIQUE,
	"entry_price"	REAL NOT NULL,
	"symbol"	TEXT NOT NULL,
	"active"	INTEGER,
	"threshold"	INTEGER,
	"name"	TEXT,
	"strategyOpId"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "strategy_config" (
	"id"	INTEGER NOT NULL UNIQUE,
	"strategy_id"	INTEGER NOT NULL,
	"data"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "pending_operation" (
	"id"	INTEGER NOT NULL,
	"bot_id"	INTEGER NOT NULL,
	"exchangeId"	NUMERIC NOT NULL,
	"position_side"	VARCHAR NOT NULL,
	"amount"	INTEGER NOT NULL,
	"entry_price"	FLOAT NOT NULL,
	"open_fee"	INTEGER NOT NULL,
	"closing_price"	FLOAT NOT NULL,
	"close_fee"	FLOAT,
	"status"	TEXT NOT NULL,
	PRIMARY KEY("id")
);
INSERT INTO "strategies" VALUES (1,'EstrategiaLong');
INSERT INTO "strategies" VALUES (2,'EstrategiaA');
INSERT INTO "symbols" VALUES (1,'TRX/USDT');
INSERT INTO "bot_operations" VALUES (1,0.11645,'TRX/USDT',1,0.001,'TestBotOperationName',2);
COMMIT;
