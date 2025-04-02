import psycopg2

# load host address
with open('host.txt', 'r') as file:
    lines = file.readlines()  # Returns a list of lines
    host_name = lines[0].strip()  # remove trailing white space
#connect database
conn = psycopg2.connect(database="crypto_db",
                        host=host_name,
                        user="daniel",
                        password="datascientest",
                        port=5432)

# next create a cursor
cur = conn.cursor()

print("---------------------------------")
print("-- Delete any previously existing table witht the same name")
print("---------------------------------")
cur.execute("""DROP TABLE IF EXISTS Crypto_ID, Interval_ID, Main_Tb;""")
conn.commit()

print("---------------------------------")
print("-- Create Crypto_ID table")
print("---------------------------------")
cur.execute("""CREATE TABLE IF NOT EXISTS Crypto_ID(
    Crypto_ID serial PRIMARY KEY,
    Crypto_name varchar(200) NOT NULL
);""")


print("---------------------------------")
print("-- Create Interval_ID table")
print("---------------------------------")
cur.execute("""CREATE TABLE IF NOT EXISTS Interval_ID(
    Interval_ID serial PRIMARY KEY,
    Interval_name varchar(200) NOT NULL
);""")



print("---------------------------------")
print("-- Create Main_Tb table")
print("---------------------------------")
cur.execute("""CREATE TABLE IF NOT EXISTS Main_Tb(
    Crypto_ID INTEGER REFERENCES Crypto_ID(Crypto_ID),
    Interval_ID INTEGER REFERENCES Interval_ID(Interval_ID),
    Currency_name varchar(200) NOT NULL,
    Open_time DATETIME,
    Open_price float NOT NULL,
    Close_price float NOT NULL,
    High_price float NOT NULL,
    Low_price float NOT NULL,
    Volume float NOT NULL,
    Close_time DATETIME,
    Nr_trades int NOT NULL,
    Quote_asset_volume float NOT NULL,
    TB_based_asset_volume float NOT NULL,
    TB_quote_asset_volume float NOT NULL
);""")


# Commit the changes
conn.commit()