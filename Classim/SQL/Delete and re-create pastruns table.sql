Drop Table "pastruns";
CREATE TABLE "pastruns" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`field`	varchar(30) NOT NULL,
	`treatment`	varchar(50) NOT NULL,
	`weatherstationname`	TEXT,
	`weather`	varchar(50) NOT NULL,
	`soil`	varchar(50) NOT NULL,
	`weathername`	TEXT NOT NULL,
	`startyear`	INTEGER NOT NULL,
	`endyear`	INTEGER NOT NULL,
	`odate`	TEXT,
	`comment`	TEXT,
	`varyflag`	INTEGER DEFAULT 0
)