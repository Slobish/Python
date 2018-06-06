import os

class map_database():
    def __init__(self):
        self.directory = os.getcwd()
        self.map_path = "maps"
        self.data_path = "data"
        self.list_filename = "maps_list.ini"
        self.file = None
        self.map_list = []
        self.map_filenames = {}
        self.map_creator = {}
    
    def downloaded_map(self, header, data):
        name = header[0]
        filename = header[1]
        creator = header[2]
        
        self.file = open( os.path.join(self.directory, self.map_path, self.data_path, filename) , "w")
        for lines in data:
            self.file.write( lines )        
        self.file.close()
        self.file = open( os.path.join(self.directory, self.map_path, self.list_filename) , "a")
        self.file.write( "{}*{}*{}".format(name, filename, creator) )
        self.file.close()
    
    def check_haveit(self, mapa):
        self.update_maplist()
        if mapa in self.map_list:
            return True
        return False
    
    def check_db(self):
        res = []
        if not os.path.exists(os.path.join(self.directory, self.map_path)):
            res.append("maps")
        elif not os.path.exists(os.path.join(self.directory, self.map_path, self.data_path)):
            res.append("data")
        elif not os.path.exists(os.path.join(self.directory, self.map_path, self.list_filename)):
            res.append("list")
        else:
            return True, None
        return False, res
    
    def create_database(self, res):
        if "maps" in res:  os.mkdir(self.map_path)
        if "maps" in res or "data" in res:    os.mkdir(os.path.join(self.map_path, self.data_path))
        if "maps" in res or "list" in res:    
            self.file = open(os.path.join(self.map_path, self.list_filename), "w")
            self.file.close()
    
    def update_maplist(self):
        self.map_list = []
        self.map_filenames = {}
        self.map_creator = {}
        self.file = open(os.path.join(self.map_path, self.list_filename))
        for lines in self.file:
            buffer = lines.split("*")
            self.map_list.append(buffer[0])
            if buffer[1][-1] == '\n':  buffer[1] = buffer[1][:-1]
            self.map_filenames[buffer[0]] = buffer[1]
            self.map_creator[buffer[0]] = buffer[2]
        self.map_list.sort()
        self.file.close()
    
    def check_map(self):
        self.update_maplist()
        for map_name in self.map_list:
            map_filename = self.map_filenames[map_name]
            if not os.path.exists(os.path.join(self.map_path, self.data_path, map_filename)):
                del self.map_filenames[map_name]
                self.map_list.remove(map_name)

    def create_map(self, nombre, creador, ladrillos, hoyos):
        self.update_maplist()
        if nombre in self.map_list:
            return False
        filename = nombre + '.txt'
        file = open(os.path.join(self.map_path, self.data_path, filename), 'w')
        file.write(nombre + '\n')
        for lad in ladrillos:
            file.write("ladrillo*{}*{}*{}*{}*{}*{}*{}\n".format(lad.x, lad.y, lad.ancho, lad.alto, lad.color[0], lad.color[1], lad.color[2]))
        for h in hoyos:
            file.write("hoyo*{}*{}*{}*{}*{}*{}\n".format(h.x, h.y, h.radio, h.color[0], h.color[1], h.color[2]))
        file.close()
        file = open(os.path.join(self.map_path, self.list_filename), 'a')
        file.write("{}*{}*{}\n".format(nombre, filename, creador))
        file.close()
        return True

map_db = map_database()
result = map_db.check_db()
if not result[0]:
    map_db.create_database(result[1])

map_db.update_maplist()
map_db.check_map()
