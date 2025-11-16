from client.gameManager import GameManager
from client.classes.hitbox import HitBox
from _thread import start_new_thread


class Pix:
    def __init__(self, pos: tuple[float, float]):
        self.x = int(pos[0])
        self.y = int(pos[1])
        self.dist = 0
        self.origin = None
        self.path = []

    def __str__(self) -> str:
        return str(self.get_tuple())

    def in_list(self, list_pix: list) -> bool:
        for pix in list_pix:
            if pix.get_tuple() == self.get_tuple():
                return True
        return False

    def get_tuple(self):
        return self.x, self.y

    def adj(self, precision: int) -> list[tuple[int, int]]:
        adj_list = list()
        for i in range(-1*precision,1*precision+1,precision):
            for j in range(-1*precision,1*precision+1,precision):
                adj_list.append((self.x+i, self.y+j))
        return adj_list

    def add_origin(self, pix):
        self.origin = pix
        self.dist = pix.dist + ((pix.x-self.x)**2 + (pix.y-self.y)**2)**0.5
        self.path = pix.path.copy()
        self.path.append((pix.x,pix.y))
        #print(self.path)

    def get_path(self)  -> list[tuple[int, int]]:
        return self.path


class Path:
    def __init__(self, pos: tuple[float, float], dest: tuple[float, float], hitbox: HitBox):
        self.pos = tuple((int(pos[0]),int(pos[1])))
        self.dest = tuple((int(dest[0]),int(dest[1])))
        self.game_state = GameManager().client_manager.game_state
        self.hitbox = HitBox(hitbox.x, hitbox.y, hitbox.w, hitbox.h)
        self.path = list()


    def dist_euclide(self, x: int, y: int, x_target: int = None, y_target: int = None) -> float:
        if x_target is None:
            x_target = self.dest[0]
        if y_target is None:
            y_target = self.dest[1]
        return ((x_target-x)**2 + (y_target-y)**2)**0.5

    def dist(self, pix: Pix) -> float:
        return pix.dist + self.dist_euclide(pix.x, pix.y)

    def search(self, precision: int) -> list[tuple[int, int]]|None:
        visited = list()
        to_visit = list()
        to_visit.append(Pix(self.pos))
        nb = 0
        while len(to_visit)>0 and nb < 1000:
            str_to_visit = list()
            for pix in to_visit:
                str_to_visit.append(pix.get_tuple())
            #print(str_to_visit, visited)
            nb += 1
            current_pix = to_visit[0]
            for pix in to_visit:
                if self.dist(pix) < self.dist(current_pix) or (
                        self.dist(pix) == self.dist(current_pix) and
                        self.dist_euclide(pix.x, pix.y) < self.dist_euclide(current_pix.x,current_pix.y)):
                    current_pix = pix

            visited.append(current_pix.get_tuple())
            #print(nb)
            #print(current_pix.adj(), self.dest)
            for pos in current_pix.adj(precision):
                self.hitbox.update(pos[0], pos[1])
                pix = Pix(pos)
                pix.add_origin(current_pix)
                path = pix.get_path()
                if self.dist_euclide(pos[0], pos[1]) <= precision:
                    #print(len(path))
                    #print(pos == self.dest)
                    print(nb)
                    return path
                elif pix.get_tuple() not in visited and not pix.in_list(to_visit) and not self.hitbox.get_collided():
                    print(self.hitbox.get_collided())
                    to_visit.append(pix)

            to_visit.remove(current_pix)
        return []

    def find_path(self, precision: int = 1):
        self.path = self.search(precision)

    def follow_path(self, precision: int = 1):
        if len(self.path) <= 1:
            return 0,0
        dx = self.path[1][0] - self.pos[0]
        dy = self.path[1][1] - self.pos[1]
        dist = (dx**2 + dy**2)
        if dist == 0:
            self.path.remove(self.path[0])
            return 0, 0
        return dx/precision, dy/precision