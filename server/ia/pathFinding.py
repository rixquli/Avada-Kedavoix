from client.gameManager import GameManager
from client.classes.hitbox import HitBox

class Pix:
    def __init__(self, pos: tuple[float, float]):
        self.x = int(pos[0])
        self.y = int(pos[1])
        self.dist = 0
        self.origin = None

    def get_tuple(self):
        return self.x, self.y

    def adj(self) -> list[tuple[int, int]]:
        adj_list = list()
        for i in range(-1,2):
            for j in range(-1,2):
                adj_list.append((self.x+i, self.y+j))
        return adj_list

    def add_origin(self, pix):
        self.origin = pix
        self.dist = pix.dist + ((pix.x-self.x)**2 + (pix.y-self.y)**2)**0.5

    def get_path(self)  -> list[tuple[int, int]]:
        if self.origin is None:
            return list()
        print(self.origin.get_path())
        return self.origin.get_path().append((self.x, self.y))


class Path:
    def __init__(self, pos: tuple[float, float], dest: tuple[float, float], hitbox: HitBox):
        self.pos = tuple((int(pos[0]),int(pos[1])))
        self.dest = tuple((int(dest[0]),int(dest[1])))
        self.game_state = GameManager().client_manager.game_state
        self.hitbox = hitbox
        self.path = list()


    def dist_euclide(self, x: int, y: int, x_target: int = None, y_target: int = None) -> float:
        if x_target is None:
            x_target = self.dest[0]
        if y_target is None:
            y_target = self.dest[1]
        return ((x_target-x)**2 + (y_target-y)**2)**0.5

    def dist(self, pix: Pix) -> float:
        return pix.dist + self.dist_euclide(pix.x, pix.y)

    def search(self) -> list[tuple[int, int]]|None:
        visited = list()
        to_visit = list()
        to_visit.append(Pix(self.pos))
        nb = 0
        while len(to_visit)>0 and nb < 1000:
            nb += 1
            current_pix = to_visit[0]
            for pix in to_visit:
                print(self.dist(pix))
                if self.dist(pix) < self.dist(current_pix) or (
                        self.dist(pix) == self.dist(current_pix) and
                        self.dist_euclide(pix.x, pix.y) < self.dist_euclide(current_pix.x,current_pix.y)):
                    current_pix = pix

            visited.append(current_pix)
            to_visit.remove(current_pix)

            for pos in current_pix.adj():
                self.hitbox.update(pos[0], pos[1])
                pix = Pix(pos)
                pix.add_origin(current_pix)
                if pos == self.dest or pix.get_path() is not None and len(pix.get_path()) > 100:
                    return pix.get_path()
                elif pix not in visited and not self.hitbox.get_collided():
                    to_visit.append(pix)
        return None

    def find_path(self):
        self.path = self.search()

    def follow_path(self,):
        self.find_path()
        if self.path is None:
            return 0,0
        dx = self.path[1][0] - self.pos[0]
        dy = self.path[1][1] - self.pos[1]
        dist = (dx**2 + dy**2)
        return dx/dist, dy/dist