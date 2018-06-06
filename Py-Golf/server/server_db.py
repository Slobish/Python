import sqlite3, base64

def all_scores(matriz):
    res = []
    for lista in matriz:
        res.append( ( decodificar( lista[1] ), lista[3] ) )
    return res

def codificar(text):    
    buff = text.encode()
    return base64.b64encode(buff)

def decodificar(text):
    buff = b''
    text = text[2:-1]
    for s in text:
        buff += s.encode() 
    buff = base64.b64decode(buff)
    return buff.decode()

class users_db():
    def __init__(self):
        self.create_table()
    
    def get_highscore(self):
        top10 = []
        self.open_db()
        sql_command =""" SELECT * FROM cuentas """
        self.cursor.execute(sql_command)
        result = self.cursor.fetchall()
        scores = all_scores( result )
        
        for i in range(10):
            buff = [0, 0]
            for user in scores:
                if user[1] >= buff[1]:
                    buff = ( user[0], user[1] )
            top10.append( buff )
            if buff != [0, 0]:
                scores.remove( buff )
        
        self.close_db()
        return top10
    
    def test(self, usuario):
        self.open_db()
        sql_command = """ SELECT * FROM cuentas WHERE usuario == "{}" """.format(codificar(usuario))
        self.cursor.execute(sql_command)
        res = self.cursor.fetchone()
        self.close_db()
        return res
    
    def user_connected(self, usuario):
        self.open_db()
        sql_command = """ SELECT * FROM cuentas WHERE usuario == "{}" """.format(codificar(usuario))
        self.cursor.execute(sql_command)
        res = self.cursor.fetchone()
        self.close_db()
        if res[4] == "t":
            return True
        else:
            return False
    
    def change_pw(self, usuario, old_pw, new_pw):
        if self.check_pw(usuario, old_pw):
            self.open_db()
            sql_command = """ UPDATE cuentas SET clave = "{}" WHERE usuario == "{}";""".format(codificar(new_pw), codificar(usuario))
            self.cursor.execute(sql_command)
            self.close_db()
            return True
        return False
            
    def status_online(self, usuario):
        self.open_db()
        sql_command = """ UPDATE cuentas SET status = "t" WHERE usuario == "{}";""".format(codificar(usuario))
        self.cursor.execute(sql_command)
        self.close_db()
    
    def status_offline(self, usuario):
        self.open_db()
        sql_command = """ UPDATE cuentas SET status = "f" WHERE usuario == "{}";""".format(codificar(usuario))
        self.cursor.execute(sql_command)
        self.close_db()
    
    def update_score(self, usuario, puntos):
        self.open_db()
        sql_command = """ UPDATE cuentas SET puntos = {} WHERE usuario == "{}";""".format(puntos, codificar(usuario))
        self.cursor.execute(sql_command)
        self.close_db()
    
    def disconnect_user(self, usuario):
        self.status_offline(usuario)
    
    def check_pw(self, usuario, clave):
        self.open_db()
        sql_command = """ SELECT * FROM cuentas WHERE usuario == "{}" """.format(codificar(usuario))
        self.cursor.execute(sql_command)
        res = self.cursor.fetchone()
        if len(res):
            if decodificar(res[2]) == clave:
                return True
            else:
                return False
        else:
            return False
        self.close_db()
        
    def log_user(self, usuario, clave):
        if self.user_exists(usuario):
            self.open_db()
            sql_command = """ SELECT * FROM cuentas WHERE usuario == "{}" """.format(codificar(usuario))
            self.cursor.execute(sql_command)
            res = self.cursor.fetchone()
            self.close_db()
            if res:
                if not self.user_connected(usuario):
                    if clave == decodificar(res[2]):
                        self.status_online(usuario)
                        return True, res[3]
        return False, None
    
    def new_user(self, usuario, clave):
        if not self.user_exists(usuario):
            self.open_db()
            sql_command = """ INSERT INTO cuentas (numero, usuario, clave, puntos, status)
            VALUES (NULL, "{}", "{}", 0, "f");""".format(codificar(usuario), codificar(clave))
            self.cursor.execute(sql_command)
            self.close_db()
            return True
        else:
            return False
    
    def user_exists(self, usuario):
        self.open_db()
        sql_command = """ SELECT * FROM cuentas WHERE usuario == "{}" """.format(codificar(usuario))
        self.cursor.execute(sql_command)
        res = self.cursor.fetchone()
        self.close_db()  
        if res:
            return True
        return False 
            
    def create_table(self):
        self.open_db()
        sql_command = """ CREATE TABLE IF NOT EXISTS cuentas (
        numero INTEGER PRIMARY KEY,
        usuario VARCHAR(20),
        clave VARCHAR(20),
        puntos INTEGER,
        status VARCHAR(2));"""
        self.cursor.execute(sql_command)
        self.close_db()
        
    def open_db(self):
        self.connection = sqlite3.connect('users.db')
        self.cursor = self.connection.cursor()
        
    def close_db(self):
        self.connection.commit()
        self.connection.close()

if __name__ == "__main__":
    
    database = users_db()