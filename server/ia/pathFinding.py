from client.classes.hitbox import HitBox



class Pix:
    def __init__(self, pos: tuple[float, float], dist_e: float=0):
        self.x = int(pos[0])
        self.y = int(pos[1])
        self.dist = 0
        self.dist_e = dist_e
        self.origin = None
        self.len_path = 0

    def __str__(self) -> str:
        return str(self.get_tuple())

    def in_list(self, list_pix: list) -> bool:
        for pix in list_pix:
            if pix.get_tuple() == self.get_tuple():
                return True
        return False

    def get_tuple(self):
        return self.x, self.y

    def add_origin(self, pix, dist):
        self.origin = pix
        self.dist += pix.dist + dist
        self.len_path = pix.len_path + 1

    def get_path(self)  -> list[tuple[int, int]]:
        if self.origin == None:
            return []
        path = self.origin.get_path()
        path.append((self.x, self.y))
        return path


class Path:
    def __init__(self, pos: tuple[float, float], dest: tuple[float, float], hitbox: HitBox, precision: int = 1):
        self.pos = tuple((int(pos[0]),int(pos[1])))
        self.dest = tuple((int(dest[0]),int(dest[1])))
        self.hitbox = HitBox(hitbox.x, hitbox.y, hitbox.w, hitbox.h)
        self.path = list()
        self.precision = precision

    def update_pos(self, x: int, y: int):
        self.pos = tuple((int(x),int(y)))

    def update_dest(self, x: int, y: int):
        self.dest = tuple((int(x),int(y)))

    def dist_euclide(self, x: int, y: int, x_target: int = None, y_target: int = None) -> float:
        if x_target is None:
            x_target = self.dest[0]
        if y_target is None:
            y_target = self.dest[1]
        return ((x_target-x)**2 + (y_target-y)**2)**0.5

    def dist(self, pix: Pix) -> float:
        return pix.dist + pix.dist_e

    def adj(self, pos: tuple[int, int]) -> list[tuple[tuple[int, int], float]]:
        adj_list: list[tuple[tuple[int, int], float]] = list()
        x,y = pos
        for dx in(-self.precision, 0, self.precision):
            for dy in (-self.precision, 0, self.precision):
                if dx != 0 or dy != 0:
                    adj_list.append(((x+dx, y+dy), (dx**2+dy**2)**0.5)) # x, y, dist
        return adj_list

    def search(self, nb_frame: int) -> list[tuple[int, int]]|None:
        visited = list()
        to_visit = list()
        to_visit.append(Pix(self.pos,self.dist_euclide(self.pos[0],self.pos[1])))
        nb = 0
        while len(to_visit)>0 and nb < 1000:
            #str_to_visit = list()
            #for pix in to_visit:
            #    str_to_visit.append(pix.get_tuple())
            nb += 1
            current_pix = to_visit[0]


            for pix in to_visit:
                if self.dist(pix) < self.dist(current_pix) or (
                        self.dist(pix) == self.dist(current_pix) and
                        pix.dist_e < current_pix.dist_e):
                    current_pix = pix

            visited.append(current_pix.get_tuple())
            to_visit.remove(current_pix)

            for (pos,dist) in self.adj(current_pix.get_tuple()):
                pix = Pix(pos, self.dist_euclide(pos[0],pos[1]))
                pix.add_origin(current_pix, dist)
                self.hitbox.update(pix.x, pix.y)

                if self.dist_euclide(pix.x, pix.y) <= self.precision or nb_frame < pix.len_path:
                    print(self.dist_euclide(pix.x, pix.y) <= self.precision)
                    return pix.get_path()

                elif pix.get_tuple() not in visited and not pix.in_list(to_visit) and not self.hitbox.get_collided():
                    to_visit.append(pix)

        return []

    def find_path(self, nb_frame: int = 5):
        self.path = self.search(nb_frame)

    def follow_path(self):
        if len(self.path) == 0:
            return 0,0
        dx = self.path[0][0] - self.pos[0]
        dy = self.path[0][1] - self.pos[1]
        self.path.remove(self.path[0])
        #if dx != 0 and dy != 0:
        #    return dx/(2**0.5), dy/(2**0.5)
        #else:
        return dx, dy