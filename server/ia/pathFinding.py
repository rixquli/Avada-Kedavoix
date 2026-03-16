from pygame.examples import grid

from client.classes.hitbox import HitBox
import time


class Pix:
    """
    pour stocker les donnes d'un pixel et y acceder plus vite
    (position/ distance/ chemin pour y arriver)
    """
    def __init__(self, pos: tuple[float, float], dist_e: float=0):
        self.x = int(pos[0])
        self.y = int(pos[1])
        self.dist = 0           # distance a parcourir entre la position de depart et le pixel
        self.dist_e = dist_e    # distance a vol d'oiseau entre le pixel et l'arrivee
        self.origin = None
        self.len_path = 0

    def __str__(self) -> str:
        return str(self.get_tuple())

    def in_list(self, list_pix: list) -> bool:
        for pix in list_pix:
            if pix.get_tuple() == self.get_tuple():
                return True
        return False

    def get_tuple(self) -> tuple[float, float]:
        """renvois la position"""
        return self.x, self.y

    def add_origin(self, pix, dist):
        """ajoute un pixel a l'origine et calcule la distance"""
        self.origin = pix
        self.dist += pix.dist + dist
        self.len_path = pix.len_path + 1

    def get_path(self)  -> list[tuple[int, int]]:
        """renvois le chemin j'usqua la position de depart"""
        if self.origin is None:
            return []
        path = self.origin.get_path()
        path.append((self.x, self.y))
        return path


class Path:
    """
    pour calculer et stocker le chemin (precision representes le saut entre chaque pixel du chemin et
    la distance minimale pour considerer l'arrivee)
    """
    def __init__(self, pos: tuple[float, float], dest: tuple[float, float], hitbox: HitBox, precision: int = 1, porte: int = 1000):
        self.pos = tuple((int(pos[0]//precision*precision),int(pos[1]//precision*precision)))
        self.dest = tuple((int(dest[0]//precision*precision),int(dest[1]//precision*precision)))
        self.hitbox = HitBox(hitbox.x, hitbox.y, hitbox.w, hitbox.h)
        self.path = list()
        self.precision = precision
        self.porte = porte

    def update_pos(self, x: int, y: int):
        self.pos = tuple((int(x//self.precision*self.precision),int(y//self.precision*self.precision)))

    def update_dest(self, x: int, y: int):
        self.dest = tuple((int(x//self.precision*self.precision),int(y//self.precision*self.precision)))

    def dist_euclide(self, x: int, y: int, x_target: int = None, y_target: int = None) -> float:
        """renvois la distance a vol d'oiseau (si x_target et y_target non remplis ils sont mis a l'arrivee)"""
        if x_target is None:
            x_target = self.dest[0]
        if y_target is None:
            y_target = self.dest[1]
        return ((x_target-x)**2 + (y_target-y)**2)**0.5

    @staticmethod
    def distance(pix: Pix) -> float:
        return pix.dist + pix.dist_e

    def adj(self, pos: tuple[int, int]) -> list[tuple[tuple[int, int], float]]:
        """
        renvois les voisins d'une position et leurs distance a la position
        voisins = [(position(voisin), distance(voisin))]
        """
        adj_list: list[tuple[tuple[int, int], float]] = list()
        x,y = pos
        for dx in (-self.precision, 0, self.precision):
            for dy in (-self.precision, 0, self.precision):
                if dx != 0 or dy != 0:
                    adj_list.append(((x+dx, y+dy), (dx**2+dy**2)**0.5)) # x, y, dist
        return adj_list

    def search(self, nb_frame: int) -> list[tuple[int, int]]|None:
        """
        renvois les nb_frame positions du chemin vers la destination
        (si nb_frame = 5 renvois 5 positions)
        a reexecuter lorsque le chemin est vide
        UTILISES A*
        """
        visited = list()
        to_visit = list()
        to_visit.append(Pix(self.pos,0))
        nb = 0

        while len(to_visit)>0 and nb < self.porte:
            #str_to_visit = list()
            #for pix in to_visit:
            #    str_to_visit.append(pix.get_tuple())

            nb += 1
            current_pix = to_visit[0]

            for pix in to_visit:
                # prendre le pixel avec la distance la plus courte
                # (distance pour aller au pixel + distance euclidienne arrive)
                if self.distance(pix) < self.distance(current_pix) or (
                        self.distance(pix) == self.distance(current_pix) and
                        pix.dist_e < current_pix.dist_e):
                    current_pix = pix

            visited.append(current_pix.get_tuple())
            to_visit.remove(current_pix)

            for (pos,dist) in self.adj(current_pix.get_tuple()):
                pix = Pix(pos, self.dist_euclide(pos[0],pos[1]))
                pix.add_origin(current_pix, dist)
                self.hitbox.update(pos[0], pos[1])

                if self.dist_euclide(pix.x, pix.y) <= self.precision or nb_frame < pix.len_path:
                    # test si il est arrive ou si il a calcule asse d'image
                    return pix.get_path()

                elif pix.get_tuple() not in visited and not pix.in_list(to_visit) and not self.hitbox.get_collided():
                    # ajoutes que les pixels non trouve et particable a la liste
                    to_visit.append(pix)

        return []

    def find_path(self, nb_frame: int = 5):
        """met a jour le chemin en en calculant un nouveau"""
        #t1 = time.time()
        self.path = self.search(nb_frame)
        #print(time.time()-t1)

    def follow_path(self):
        """renvois la direction de la prochaine position"""
        if len(self.path) == 0:
            print(self.path)
            return 0,0
        x = self.path[0][0] - self.pos[0]
        y = self.path[0][1] - self.pos[1]
        print(self.path)
        self.path.pop(0)
        return x, y