import sqlite3
import os
import base64
import string

class usersDatabase():

    def __init__(self, path, filename):
        # Initializes instance attributes
        self.path = path
        self.filename = filename
        self.file_path = os.path.join(path, filename)
        # Database instances
        self.database = ''
        self.cursor = ''

        if not self.db_exists():
            self.db_init()

    def open_db(self):
        # Opens database
        self.database = sqlite3.connect( self.file_path )
        self.cursor = self.database.cursor()

    def close_db(self):
        # Closes database
        self.database.commit()
        self.database.close()

    def db_execute(self, sql_command):
        # Executes a sql command
        self.open_db()
        self.cursor.execute( sql_command )
        self.close_db()

    def db_return(self, sql_command):
        # Executes a sql command and returns data
        self.open_db()
        self.cursor.execute(sql_command)
        res = self.cursor.fetchone()
        self.close_db()
        return res

    def db_exists(self):
        # Checks if database file already exists
        if os.path.exists( self.file_path ):
            return True
        return False

    def db_init(self):
        # Initializes database structure and tables
        sql_command = """
        CREATE TABLE users (
            id integer primary key autoincrement,
            username varchar(255),
            password varchar(255),
            logged boolean
        )
        """
        self.db_execute( sql_command )

    def check_username(self, username):
        # Verifies if the username is valid
        if len(username) > 8 and len(username) < 255:
            for s in username:
                if s not in string.digits and s not in string.ascii_letters:
                    return False
            return True
        return False

    def check_password(self, password):
        # Verifies if the password is valid
        if len(password) > 8 and len(password) < 255:
            for s in password:
                if s not in string.digits and s not in string.ascii_letters:
                    return False
            return True
        return False

    def user_exists(self, username):
        # Checks if username already exists
        sql_command = """
        SELECT * FROM users WHERE users.username = "{}"
        """.format(username)
        if self.db_return( sql_command ):
            return True
        return False

    def user_logged(self, username):
        # Checks if user has logged
        sql_command = """
        SELECT users.logged FROM users WHERE users.username = "{}"
        """.format(username)
        res = self.db_return( sql_command )[0]
        if res == "TRUE":
            return True
        return False

    def new_user(self, username, password):
        # Creates new user
        if not self.user_exists( username ):
            if not self.check_username( username ):
                return False
            if not self.check_password( password ):
                return False
            pw = base64.b64encode( password.encode() ).decode()
            sql_command = """
            INSERT INTO users (username, password)
            VALUES ("{}", "{}")
            """.format(username, pw)
            self.db_execute( sql_command )
            return True
        return False

    def delete_user(self, username, password):
        # Deletes an existing user
        if self.user_exists( username ):
            if self.password_validation( username, password ):
                sql_command = """
                DELETE FROM users
                WHERE users.username = "{}"
                """.format(username)
                self.db_execute( sql_command )
                return True
        return False

    def user_login(self, username, password):
        # Authorize an user connection
        if self.password_validation(username, password):
            sql_command = """
            UPDATE users
            SET logged = "TRUE"
            WHERE users.username = "{}"
            """.format(username)
            self.db_execute( sql_command )
            return True
        return False

    def user_logout(self, username, password):
        # User desconnection
        if self.password_validation(username, password):
            sql_command = """
            UPDATE users
            SET logged = "FALSE"
            WHERE users.username = "{}"
            """.format(username)
            self.db_execute( sql_command )
            return True
        return False

    def password_validation(self, username, password):
        # Verifies if passwords are OK
        sql_command = """
        SELECT users.password FROM users WHERE users.username = "{}"
        """.format(username)
        res = self.db_return( sql_command )[0]
        res = base64.b64decode( res ).decode()
        if res == password:
            return True
        return False

if __name__ == "__main__":
    test = usersDatabase("", "prueba.db")
    menu = ["Crear nuevo usuario", "Borrar un usuario", "Conectarse con usuario", "Desconectar usuario", "Chequear conexion de usuario", "Cerrar"]
    while True:
        print("\n\nQue desea hacer?")
        for index, option in enumerate(menu):
            print("%d. %s" % (index, option))
        eleccion = int(input("\n\nRespuesta: "))

        if eleccion == 0:
            username = input("Username: ")
            password = input("Password: ")
            if test.new_user(username, password):
                print("Nuevo usuario creado exitosamente!")
            else:
                print("Hubo un problema")
        elif eleccion == 1:
            username = input("Username: ")
            password = input("Password: ")
            if test.delete_user(username, password):
                print("Usuario borrado exitosamente!")
            else:
                print("Hubo un problema")
        elif eleccion == 2:
            username = input("Username: ")
            password = input("Password: ")
            if test.user_login(username, password):
                print("Usuario conectado exitosamente!")
            else:
                print("Hubo un problema")
        elif eleccion == 3:
            username = input("Username: ")
            password = input("Password: ")
            if test.user_logout(username, password):
                print("Usuario desconectado exitosamente!")
            else:
                print("Hubo un problema")
        elif eleccion == 4:
            username = input("Username: ")
            if test.user_logged(username):
                print("Usuario conectado")
            else:
                print("Usuario desconectado")
        elif eleccion == 5:
            break
