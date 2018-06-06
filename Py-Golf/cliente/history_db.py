import sqlite3

def to_list(matriz, index):
    lista = []
    for item in matriz:
        lista.append(item[index])
    return lista

class hist_db():
    def __init__(self):
        self.open()
        self.create_table()
        self.close()
    
    def create_table(self):
        sql_command = """ CREATE TABLE IF NOT EXISTS history (
        numero INTEGER PRIMARY KEY,
        nombre VARCHAR(20),
        mapa VARCHAR(20),
        intentos INTEGER)
        """
        self.cursor.execute(sql_command)
        
    def highscore(self, maplist):
        h_score = []
        self.open()
        for map in maplist:
            sql_command = """ SELECT * FROM history where mapa == "%s" """ % (map)
            self.cursor.execute(sql_command)
            result = self.cursor.fetchall()
            if len(result):
                tries = to_list(result, 3)
                best = tries.index(min(tries))
                h_score.append(result[best])
        self.close()
        return h_score
        
    def update_tries(self, nombre, mapa, intentos):
        self.open()
        sql_command = """ UPDATE history SET intentos = "%d" WHERE nombre == "%s" and mapa == "%s" """ % (intentos, nombre, mapa)
        self.cursor.execute(sql_command)
        self.close()
    
    def get_tries(self, nombre, mapa):
        self.open()
        sql_command = """ SELECT * FROM history WHERE nombre == "%s" and mapa == "%s";""" % (nombre, mapa)
        self.cursor.execute(sql_command)
        try:
            res = self.cursor.fetchall()[0][-1]
        except:
            res = False
        self.close()
        return res
    
    def set_tries(self, nombre, mapa, intentos):
        self.open()
        sql_command = """ INSERT INTO history(numero, nombre, mapa, intentos)
        VALUES (NULL, "%s", "%s", %d);""" % (nombre, mapa, intentos)
        self.cursor.execute(sql_command)
        self.close()
    
    def open(self):
        self.connection = sqlite3.connect('score.db')
        self.cursor = self.connection.cursor()
    
    def close(self):
        self.connection.commit()
        self.connection.close()


score_db = hist_db()