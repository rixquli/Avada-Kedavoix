from client.gameManager import GameManager
class Path:
    def __init__(self, pos: tuple[int, int], dest: tuple[int, int]):
        self.pos = pos
        self.dest = dest
        self.obstacles = GameManager().client_manager.game_state.walls
        self.path = list()

path = Path((0, 0), (0, 0))