import socket, threading
import atexit, datetime
from map_data import map_db, os
import server_db

database = server_db.users_db()

threadLock = threading.Lock()

PIN = 'PGLK1410'
MAXIMO_JUGADORES = 10
ESPERAS = 10

class online_game():
    def __init__(self, name, mapa, max_tries, players, creator):
        self.name = name
        self.map = mapa
        self.max = int(max_tries)
        self.players = players.copy()
        self.expecting_answer = players.copy()
        self.creator = creator
        
        self.ok = 0
        self.users = []
        self.cantidad = 0
        self.current = 0
        self.jugados = 0
        self.winner = None
        
        self.alive = True
        
    def send_invitations(self):
        for user in sv.list_users:
            if user.username in self.expecting_answer:
                user.current_game = self.name
                user.invited = True
                user.socket.send("GAME-REQUEST-{}-{}-{}-{}".format(self.name, self.map, self.max, self.creator).encode())
    
    def check(self):
        if len( self.expecting_answer ) == 0:
            if len( self.players ) > 0:
                self.start()
                return False
            else:
                for user in sv.list_users:
                    if user.username == self.creator:
                        user.socket.send("GAME-NADIE".encode())
                return True
        return False
    
    def start(self):
        self.game_init()
        for user in self.users:
            user.socket.send("GAME-START-{}-{}".format(user.order, self.cantidad).encode())
    
    def game_init(self):
        self.cantidad = len(self.players) + 1 
        for i, p in enumerate(self.players):
            for user in sv.list_users:
                if p == user.username:
                    self.users.append(user)
                    user.playing = True
                    user.invited = False
                    user.order = i
                    user.intentos = 0
                    
        for user in sv.list_users:
            if self.creator == user.username:
                self.users.append(user)
                user.playing = True
                user.invited = False
                user.order = len(self.players)
                user.intentos = 0
                
    def send_hit(self, ang, speed):
        for user in self.users:
            if user.order != ( self.current - 1 ):
                user.socket.send("GAME-PLAYER-{}-{}-{}".format(self.current - 1, ang, speed).encode())                   
    
    def ready(self):
        self.ok += 1
        if self.ok == self.cantidad:
            self.current = 0
            self.next_turn()
    
    def next_turn(self):
        if self.jugados == self.cantidad:
            self.jugados = 0
        if self.jugados == 0 and self.users[0].intentos == self.max:
            self.game_end(end = True)
        else:
            if self.current > self.cantidad - 1:
                self.current = 0
            for user in self.users:
                if user.order == self.current:
                    user.intentos += 1
                    user.socket.send("GAME-PLAY".encode())
                    self.jugados += 1
                    break
            self.current += 1
    
    def game_end(self, winner=None, end=False):
        if end:
            for user in self.users:
                user.playing = False
                user.invited = False
                user.socket.send("GAME-END-NADIE".encode())
        else:
            winner.gano = False
            winner.playing = False
            winner.invited = False
            for user in self.users:
                if user.username != winner.username:
                    user.playing = False
                    user.invited = False
                    user.socket.send("GAME-END-{}".format(winner.username).encode())
            self.winner = winner
        self.alive = False
                
        
class user(threading.Thread):
    def __init__(self, connection, address, server):
        threading.Thread.__init__(self)
        self.server = server
        self.socket = connection
        self.socket.settimeout( 0.1 )
        self.ip = address[0]
        self.port = address[1]
        self.alive = True
        self.validation = False
        self.playing = False
        self.invited = False   
        self.logged = False
        self.username = ""
        self.score = 0
        
        self.order = 0
        self.color = None
        self.intentos = 0
        self.gano = False
        
        self.current_game = None
        
        self.chat = []
        
        self.start()
    
    def run(self):
        while self.alive:
            if not self.validation:
                self.validate_protocol()
            else:
                try:
                    data = self.socket.recv(512).decode().split('-')
                    if data[0] == "REGISTER" and not self.logged and not self.playing:
                        self.register(data)
                    elif data[0] == "LOGIN" and not self.logged and not self.playing:
                        self.login(data)
                    elif data[0] == "USERS":
                        self.send_userlist()
                    elif data[0] == "LOGOUT" and self.logged:
                        self.logout(data[1])
                    elif data[0] == "CHATIN" and self.logged and not self.playing:
                        self.chat_in(data)
                    elif data[0] == "TOP10" and self.logged and not self.playing:
                        self.send_top10()
                    elif data[0] == "CLOSE":
                        self.stop()
                    elif data[0] == "CHANGE" and self.logged and not self.playing:
                        self.change_pw(data[1:])
                    elif data[0] == "MAPLIST" and self.logged and not self.playing:
                        self.send_maplist()
                    elif data[0] == "CHATOUT" and self.logged and not self.playing:
                        self.chat_out()
                    elif data[0] == "GAME" and self.logged:
                        if data[1] == "INVITE" and not self.playing and not self.invited:
                            self.create_game(data[2:])
                            self.server.console("{} ha creado una partida".format(self.username))
                        elif data[1] == "ANSWER":
                            self.answer_game(data[2])
                            self.server.console("{} ha respondido a la invitacion: {}".format(self.username, data[2]))
                        elif data[1] == "DOWNLOAD":
                            self.download_map(data[2])
                        elif data[1] == "WAITING":
                            sv.console("{} esta preparado.".format(self.username))
                            self.server.games[self.current_game].ready()
                        elif data[1] == "STOP":
                            self.server.games[self.current_game].next_turn()
                        elif data[1] == "HIT":
                            if len(data) == 4:
                                self.server.games[self.current_game].send_hit(data[2], data[3])
                            else:
                                self.server.games[self.current_game].send_hit(-float(data[3]), data[4])
                        elif data[1] == "WIN":
                            self.gano = True
                            self.score += 100
                            self.server.games[self.current_game].game_end(winner=self)   
                        
                except socket.timeout:
                    pass
                
                except ConnectionResetError:
                    self.logout(self.username)
                    self.alive = False
    
    def send_top10(self):
        top10 = database.get_highscore()
        for i, user in enumerate(top10):
            self.socket.send("TOP10-{}-{}-{}".format(i + 1, user[0], user[1]).encode())
            if not self.socket.recv(512).decode().split('-')[1] == "OK":
                break
        self.socket.send("TOP10-END".encode())
    
    def download_map(self, mapa):
        path = os.path.join( map_db.directory, map_db.map_path, map_db.data_path )
        filename = map_db.map_filenames[ mapa ]
        mapa_data = open( os.path.join(path, filename) )
        self.socket.send("GAME-DOWNLOAD-HEAD-{}-{}-{}".format(mapa, filename, map_db.map_creator[ mapa ]).encode())
        if self.socket.recv(512).decode().split('-')[2] == "OK":
            for lines in mapa_data:
                self.socket.send("GAME-DOWNLOAD-DATA-{}".format(lines).encode())
                if self.socket.recv(512).decode().split('-')[2] != "OK":
                    break
        mapa_data.close()
        self.socket.send("GAME-DOWNLOAD-DATA-END".encode())
    
    def answer_game(self, data):
        aux = self.current_game
        self.server.games[ self.current_game ].expecting_answer.remove( self.username )
        if data == "NO":
            print(self.invited, self.playing, self.logged)
            self.server.games[ self.current_game ].players.remove( self.username )
            self.current_game = None
            self.invited = False
        if self.server.games[ aux ].check():
            del self.server.games[ aux ] 
            
    def create_game(self, data):
        sv.games[ data[0] ] = online_game(data[0], data[1], data[2], data[3:], self.username)
        self.current_game = data[0]
        for user in self.server.list_users:
            if user.username in self.server.games[ data[0] ].players and ( user.invited or user.playing ):
                self.server.games[ data[0] ].players.remove( user.username )
                self.server.games[ data[0] ].expecting_answer.remove( user.username )
        self.server.games[ data[0] ].send_invitations()
        
    def send_maplist(self):
        map_db.update_maplist()
        text = "MAPLIST"
        for mapa in map_db.map_list:
            text = text + '-' + mapa
        self.socket.send(text.encode()) 
    
    def change_pw(self, data):
        if database.change_pw(self.username, data[0], data[1]):
            self.socket.send("CHANGE-TRUE".encode())
        else:
            self.socket.send("CHANGE-FALSE".encode())
    
    def send_userlist(self):
        text = "USERS"
        for user in self.server.list_users:
            if user.username != self.username and user.logged:
                text += '-' + user.username
        if text == "USERS": text += '-'
        self.socket.send(text.encode())
    
    def chat_out(self):
        for m in self.chat:
            self.socket.send("CHATOUT-{}-{}".format(m[0], m[1]).encode())
            try:
                if not self.socket.recv(512).decode() == "CHATOUT-OK":
                    break
            except:
                break
        self.socket.send("CHATOUT-END".encode())
        self.chat = []
        
    def chat_in(self, data):
        threadLock.acquire()
        for c in self.server.list_users:
            c.chat.append( (self.username, data[1]) )
        self.socket.send("CHATIN-TRUE".encode())
        self.server.console("El usuario {} ha mandado un mensaje".format(self.username))
        threadLock.release()
        
    def logout(self, data):
        self.logged = False
        database.disconnect_user(data)
        self.server.console("El usuario {} se ha desconectado".format(self.username))
        self.socket.send("LOGOUT-OK".encode())
        
    def register(self, data):
        if database.new_user(data[1], data[2]):
            self.socket.send("REGISTER-TRUE".encode())
        else:
            self.socket.send("REGISTER-FALSE".encode())
            
    def login(self, data):
        check, score = database.log_user(data[1], data[2])
        if check:
            self.logged = True
            self.username = data[1]
            self.score = score
            self.socket.send(( "LOGIN-TRUE-" + str(score) ).encode())
            self.server.console("El usuario {} se ha conectado".format(self.username))
        else:
            self.socket.send("LOGIN-FALSE-0".encode())
    
    def validate_protocol(self):
        self.socket.send("VALIDATE-".encode())
        try:
            data = self.socket.recv(512).decode()
            try:   
                data = data.split('-')[1]
                if data == PIN:
                    self.validation = True
                    self.socket.send("VALIDATE-TRUE-{}".format(self.server.server_name).encode())
                else:
                    self.stop()
            except:
                self.stop()
        except socket.timeout:
            self.stop()
    
    def stop(self):
        self.alive = False
        
class server():
    
    def __init__(self, ip, port, sv_name):
        self.server_name = sv_name
        self.ip = ip
        self.port = port
        self.list_users = []
        self.num_users = 0
        self.games = {}
        self.file = None
        self.filename = "history.txt"
    
    def write_file(self, text):
        self.open_file()
        self.file.write(text)
        self.close_file()
    
    def open_file(self):
        self.file = open(self.filename, "a")
    
    def close_file(self):
        self.file.close()
    
    def check_games(self):
        claves = self.games.keys()
        try:
            for k in claves:
                if not self.games[k].alive:
                    database.update_score( self.games[k].winner.username, self.games[k].winner.score)
                    self.games.pop(k)
        except:
            pass
    
    def open_server(self):
        self.socket = socket.socket()
        self.socket.bind( (self.ip, self.port) )
        self.socket.listen(5)
        self.socket.settimeout(1)
    
    def console(self, text):
        date = datetime.datetime.now()
        event =  "[PyGolf SERVER] {}".format(text)
        event_f =  "[PyGolf SERVER {}/{}/{} {}:{}:{}] {}".format(date.day, date.month, date.year, date.hour, date.minute, date.second, text)
        print(event)
        self.write_file( event_f + '\n' )
    
    def check_connections(self):
        for user in self.list_users:
            if not user.alive:
                self.console("Conexion saliente " + user.ip)
                self.list_users.remove(user)
                self.num_users -= 1
    
    def turn_on(self):
        self.open_server()
        self.console("Servidor ONLINE")
        while self.num_users < MAXIMO_JUGADORES:
            try:
                c, addr = self.socket.accept()
                self.console("Conexion entrante " + addr[0])
                self.list_users.append( user(c, addr, self) )
                self.num_users += 1
            except KeyboardInterrupt:
                break
            except socket.timeout:
                self.check_connections()
                self.check_games()
        self.close_server()
    
    def close_server(self):
        for c in self.list_users:
            c.alive = False
        self.socket.close()
        self.console("Servidor OFFLINE")

def exit_handler():
    global sv
    sv.close_server()

name = input("Nombre del servidor: ")
ip = socket.gethostbyname(socket.gethostname())
print("Direccion ip:", ip)
port = int(input("Puerto del servidor: "))
print("-" * 30 + "\n")

sv = server(ip, port, name)
sv.turn_on()

atexit.register(exit_handler)
