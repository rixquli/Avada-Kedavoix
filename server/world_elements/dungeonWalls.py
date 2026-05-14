import random
from dataclasses import dataclass


class Room:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other):
        return not (
            self.x + self.w < other.x
            or self.x > other.x + other.w
            or self.y + self.h < other.y
            or self.y > other.y + other.h
        )


@dataclass
class DungeonLevel:
    walls: list
    teleport_pos: tuple
    is_boss_room: bool = False  # Flag pour indiquer si c'est une salle sans sortie


class DungeonGenerator:

    def __init__(
        self,
        width=1000,
        height=1000,
        room_min=250,
        room_max=600,
        room_count=50,
        corridor_width=60,
        wall_thickness=10,
        door_width=80,
    ):

        self.width = width
        self.height = height
        self.room_min = room_min
        self.room_max = room_max
        self.room_count = room_count

        self.corridor_width = corridor_width
        self.wall_thickness = wall_thickness
        self.door_width = door_width

    def _generate_room_partition(self):
        rectangles = [(-self.width, -self.height, self.width * 2, self.height * 2)]

        def find_splittable_index():
            splittable = [
                (i, r[2] * r[3])
                for i, r in enumerate(rectangles)
                if r[2] >= self.room_min * 2 or r[3] >= self.room_min * 2
            ]
            if not splittable:
                return None
            return max(splittable, key=lambda item: item[1])[0]

        while len(rectangles) < self.room_count:
            index = find_splittable_index()
            if index is None:
                break

            x, y, w, h = rectangles[index]
            can_split_vertical = w >= self.room_min * 2
            can_split_horizontal = h >= self.room_min * 2

            if not can_split_vertical and not can_split_horizontal:
                break

            if can_split_vertical and can_split_horizontal:
                split_vertical = w >= h
            else:
                split_vertical = can_split_vertical

            if split_vertical:
                cut = random.randint(self.room_min, w - self.room_min)
                left = (x, y, cut, h)
                right = (x + cut, y, w - cut, h)
                rectangles[index : index + 1] = [left, right]
            else:
                cut = random.randint(self.room_min, h - self.room_min)
                top = (x, y, w, cut)
                bottom = (x, y + cut, w, h - cut)
                rectangles[index : index + 1] = [top, bottom]

        return [Room(x, y, w, h) for x, y, w, h in rectangles]

    def _is_point_in_safe_room_area(self, room, point, size):
        x, y = point

        return (
            room.x + self.wall_thickness <= x - size[0]
            and x + size[0] <= room.x + room.w - self.wall_thickness
            and room.y + self.wall_thickness <= y - size[1]
            and y + size[1] <= room.y + room.h - self.wall_thickness
        )

    def generate_rooms(self, required_point=None, max_attempts=40):
        rooms = []

        for _ in range(max_attempts):
            rooms = self._generate_room_partition()

            if required_point is None:
                return rooms

            if any(
                self._is_point_in_safe_room_area(room, required_point, (50, 50))
                for room in rooms
            ):
                return rooms

        return rooms

    def merge_intervals(self, intervals):

        if not intervals:
            return []

        intervals = sorted(intervals)
        merged = [intervals[0]]

        for start, end in intervals[1:]:
            last_start, last_end = merged[-1]

            if start <= last_end:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))

        return merged

    def add_wall_line_with_openings(
        self, walls, horizontal, fixed, start, end, openings
    ):

        if end <= start:
            return

        gap_half = self.door_width // 2
        blocked = []

        for opening in openings:
            gap_start = max(start, opening - gap_half)
            gap_end = min(end, opening + gap_half)

            if gap_end > gap_start:
                blocked.append((gap_start, gap_end))

        blocked = self.merge_intervals(blocked)
        cursor = start

        for gap_start, gap_end in blocked:

            if gap_start > cursor:

                if horizontal:
                    walls.append(
                        (cursor, fixed, gap_start - cursor, self.wall_thickness)
                    )
                else:
                    walls.append(
                        (fixed, cursor, self.wall_thickness, gap_start - cursor)
                    )

            cursor = max(cursor, gap_end)

        if cursor < end:

            if horizontal:
                walls.append((cursor, fixed, end - cursor, self.wall_thickness))
            else:
                walls.append((fixed, cursor, self.wall_thickness, end - cursor))

    def find_room_adjacencies(self, rooms):

        edges = []

        for i, a in enumerate(rooms):
            for j in range(i + 1, len(rooms)):
                b = rooms[j]

                if a.x + a.w == b.x or b.x + b.w == a.x:
                    overlap_start = max(a.y, b.y)
                    overlap_end = min(a.y + a.h, b.y + b.h)

                    if overlap_end - overlap_start >= self.door_width:
                        if a.x + a.w == b.x:
                            edges.append(
                                {
                                    "a": i,
                                    "b": j,
                                    "a_side": "right",
                                    "b_side": "left",
                                    "start": overlap_start,
                                    "end": overlap_end,
                                }
                            )
                        else:
                            edges.append(
                                {
                                    "a": i,
                                    "b": j,
                                    "a_side": "left",
                                    "b_side": "right",
                                    "start": overlap_start,
                                    "end": overlap_end,
                                }
                            )

                if a.y + a.h == b.y or b.y + b.h == a.y:
                    overlap_start = max(a.x, b.x)
                    overlap_end = min(a.x + a.w, b.x + b.w)

                    if overlap_end - overlap_start >= self.door_width:
                        if a.y + a.h == b.y:
                            edges.append(
                                {
                                    "a": i,
                                    "b": j,
                                    "a_side": "bottom",
                                    "b_side": "top",
                                    "start": overlap_start,
                                    "end": overlap_end,
                                }
                            )
                        else:
                            edges.append(
                                {
                                    "a": i,
                                    "b": j,
                                    "a_side": "top",
                                    "b_side": "bottom",
                                    "start": overlap_start,
                                    "end": overlap_end,
                                }
                            )

        return edges

    def create_openings(self, rooms):

        openings = {
            i: {"top": [], "bottom": [], "left": [], "right": []}
            for i in range(len(rooms))
        }
        edges = self.find_room_adjacencies(rooms)

        def add_opening(edge):
            margin = self.door_width // 2
            pos_min = edge["start"] + margin
            pos_max = edge["end"] - margin
            if pos_max < pos_min:
                return False
            door_pos = random.randint(pos_min, pos_max)
            openings[edge["a"]][edge["a_side"]].append(door_pos)
            openings[edge["b"]][edge["b_side"]].append(door_pos)
            return True

        # Union-Find to track connected components
        parent = list(range(len(rooms)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            px, py = find(x), find(y)
            if px == py:
                return False
            parent[px] = py
            return True

        # Build a random spanning tree to guarantee every room is reachable
        shuffled = list(enumerate(edges))
        random.shuffle(shuffled)
        used_edges = set()

        for edge_id, edge in shuffled:
            if find(edge["a"]) != find(edge["b"]):
                if add_opening(edge):
                    union(edge["a"], edge["b"])
                    used_edges.add(edge_id)

        # Add extra random openings (~25% of remaining edges) for variety
        for edge_id, edge in enumerate(edges):
            if edge_id not in used_edges and random.random() < 0.25:
                add_opening(edge)

        return openings

    def build_walls(self, rooms, openings):

        walls = []

        for i, r in enumerate(rooms):

            self.add_wall_line_with_openings(
                walls, True, r.y, r.x, r.x + r.w, openings[i]["top"]
            )

            self.add_wall_line_with_openings(
                walls, True, r.y + r.h, r.x, r.x + r.w, openings[i]["bottom"]
            )

            self.add_wall_line_with_openings(
                walls, False, r.x, r.y, r.y + r.h, openings[i]["left"]
            )

            self.add_wall_line_with_openings(
                walls, False, r.x + r.w, r.y, r.y + r.h, openings[i]["right"]
            )

        return walls

    def generate_boss_room(self):
        """Genere la salle du boss sans teleporteur de sortie"""
        # Create one giant room
        room = Room(
            -self.width * 2 // 2, -self.height * 2 // 2, self.width * 2, self.height * 2
        )

        # Build just the outer walls with no openings
        walls = []

        # Top wall
        walls.append((room.x, room.y, room.w, self.wall_thickness))

        # Bottom wall
        walls.append(
            (room.x, room.y + room.h - self.wall_thickness, room.w, self.wall_thickness)
        )

        # Left wall
        walls.append((room.x, room.y, self.wall_thickness, room.h))

        # Right wall
        walls.append(
            (room.x + room.w - self.wall_thickness, room.y, self.wall_thickness, room.h)
        )

        # Teleport position at center (utilisé pour l'apparition du boss, pas pour les portails)
        teleport_pos = (room.x + room.w // 2, room.y + room.h // 2)

        return DungeonLevel(
            walls=walls,
            teleport_pos=teleport_pos,
            is_boss_room=True,  # Pas de portail de sortie dans cette salle
        )

    def generate_level(self, required_point=None, is_last=False):

        rooms = self.generate_rooms(required_point=required_point)

        openings = self.create_openings(rooms)

        walls = self.build_walls(rooms, openings)

        teleport_room = (
            random.choice(rooms[1:] if len(rooms) > 1 else rooms)
            if rooms
            else Room(0, 0, 1, 1)
        )

        return DungeonLevel(
            walls=walls,
            teleport_pos=teleport_room.center(),
        )


class Dungeon:
    def __init__(self, nb_level: int = 10):
        self.generator = DungeonGenerator(wall_thickness=25, room_min=350, room_max=750)

        self.dungeonWalls: list[DungeonLevel | None] = [None] * nb_level
        self.required_point: list[tuple[int, int] | None] = [None] * (nb_level + 1)
        self.required_point[0] = (250, 0)
        self.nb_level = nb_level

    def generate_all_layer(self):
        for i in range(self.nb_level):
            is_last = i == self.nb_level - 1

            # Genere la boss room
            if is_last:
                level = self.generator.generate_boss_room()
            else:
                level = self.generator.generate_level(
                    required_point=self.required_point[i], is_last=is_last
                )

            self.dungeonWalls[i] = DungeonLevel(
                level.walls, level.teleport_pos, getattr(level, "is_boss_room", False)
            )
            if not is_last:
                self.required_point[i + 1] = level.teleport_pos

    def generate_layer(self, level_value: int):
        if level_value > 0 and self.dungeonWalls[level_value - 1] == None:
            print(
                f"impossible to generate layer: {level_value} (precedent does not exist)"
            )
            return 1
        if self.dungeonWalls[level_value] != None:
            print(f"layer: {level_value} already generated")
            return 2
        if level_value >= self.nb_level or level_value < 0:
            print(
                f"impossible to generate layer: {level_value} (layer to big or to small)"
            )
            return 3

        level = self.generator.generate_level(
            required_point=self.required_point[level_value]
        )
        self.dungeonWalls[level_value] = level
        self.required_point[level_value + 1] = level.teleport_pos
        return 0
