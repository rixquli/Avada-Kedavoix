import json
import os

from server.gameState import GameState
from server.world_elements.dungeonWalls import DungeonLevel


class Saver:
    def __init__(self, network_manager):
        self.save_path = "./save.json"
        self.network_manager = network_manager

    def save(self):
        gs = self.network_manager.game_state.get_game_state(diff=False)

        dungeon = []
        for lvl in self.network_manager.Dungeon.dungeonWalls:
            if lvl is None:
                dungeon.append(None)
            else:
                dungeon.append(
                    {
                        "walls": lvl.walls,
                        "teleport_pos": list(lvl.teleport_pos),
                    }
                )

        data = {
            "game_state": gs,
            "dungeonWalls": dungeon,
            "required_point": self.network_manager.Dungeon.required_point,
        }

        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load_save(self):
        if not os.path.exists(self.save_path):
            return False

        with open(self.save_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        state = payload.get("game_state", {})

        self.network_manager.game_state.apply_state(state)

        raw_dungeon = payload.get("dungeonWalls", [])
        rebuilt = []
        for lvl in raw_dungeon:
            if lvl is None:
                rebuilt.append(None)
            else:
                rebuilt.append(
                    DungeonLevel(
                        walls=lvl["walls"],
                        teleport_pos=tuple(lvl["teleport_pos"]),
                    )
                )

        if rebuilt:
            self.network_manager.Dungeon.dungeonWalls = rebuilt

        req = payload.get("required_point")
        if req is not None:
            self.network_manager.Dungeon.required_point = [
                tuple(p) if isinstance(p, list) else p for p in req
            ]

        return True
