import aiopg
import asyncio
import aiosqlite3

DB_HOST = "localhost"
DB_USER = "postgres"
DB_PASS = ""
DB_DATABASE = "skordobot"

async def main():
	conn = await aiopg.connect(database=DB_DATABASE,user=DB_USER,
	password=DB_PASS,host=DB_HOST,port=5432)
	db = await conn.cursor()
	await db.execute("""
	CREATE TABLE IF NOT EXISTS recipes (
	title	TEXT,
	ingredients	TEXT,
	execution	TEXT,
	author	TEXT,
    image     TEXT
    );
    """)
	sconn = await aiosqlite3.connect(database="skordobot.db")
	sdb = await sconn.cursor()
	print("Migrating servers")
	await sdb.execute("SELECT * FROM recipes WHERE 1")
	res = await sdb.fetchall()
	for i in res:
		phld = ""
		for ii in i:
			phld+="%s,"
		await db.execute("INSERT INTO recipes values({})".format(phld[:-1]),i)
	print("All done. Exiting...")
    
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
