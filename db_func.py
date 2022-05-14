import sqlite3

DB = "./scores.db"

class database():
    def __init__(self):
        self.connection = sqlite3.connect(DB)
        self.cur = self.connection.cursor()
    
    def create_table(self, name):
        table = f""" CREATE TABLE {name} (
            name varchar(255) not null,
            score varchar(255) not null
        ); """

        self.cur.execute(table)
    
    def get_top3(self):
        
        entries = []

        for i in range(3):
            if i == 0:
                entrie = "SELECT name, MAX(score) from top3"
                self.cur.execute(entrie)
            else:
                if i==2: e = entries[1][0]
                else: e = " "
                entrie = f"SELECT name, MAX(score) from top3 WHERE name NOT IN ('{entries[0][0]}', '{e}')"
                self.cur.execute(entrie)
            
            entrie = self.cur.fetchone()
            entries.append(entrie)

        names = []
        for x in range(3):
            names.append(entries[x][0])

        delete = f"DELETE from top3 WHERE name NOT IN ('{names[0]}', '{names[1]}', '{names[2]}')"
        
        self.cur.execute(delete)
        self.connection.commit()

        return entries
    
    def add_score(self, u_name, u_score):
        insert = "INSERT INTO 'top3' VALUES (?, ?)"
        self.cur.execute(insert, (u_name, u_score))
        self.connection.commit()
    
if __name__ == "__main__":
    db = database()
    entries = db.get_top3()

    print(f"1.Platz mit {entries[0][1]} Punkten: {entries[0][0]}")
    print(f"2.Platz mit {entries[1][1]} Punkten: {entries[1][0]}")
    print(f"3.Platz mit {entries[2][1]} Punkten: {entries[2][0]}")