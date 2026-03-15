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


class DungeonGenerator:

    def __init__(
        self,
        width=2500,
        height=2500,
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

    def generate_rooms(self):
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
        degree = [0] * len(rooms)

        def add_opening(edge):
            margin = self.door_width // 2
            pos_min = edge["start"] + margin
            pos_max = edge["end"] - margin
            if pos_max < pos_min:
                return False

            door_pos = random.randint(pos_min, pos_max)
            openings[edge["a"]][edge["a_side"]].append(door_pos)
            openings[edge["b"]][edge["b_side"]].append(door_pos)
            degree[edge["a"]] += 1
            degree[edge["b"]] += 1
            return True

        used_edges = set()

        for room_index in range(len(rooms)):
            if degree[room_index] > 0:
                continue

            candidates = [
                (edge_id, edge)
                for edge_id, edge in enumerate(edges)
                if edge["a"] == room_index or edge["b"] == room_index
            ]
            if not candidates:
                continue

            edge_id, edge = random.choice(candidates)
            if add_opening(edge):
                used_edges.add(edge_id)

        for edge_id, edge in enumerate(edges):
            if edge_id in used_edges:
                continue
            if random.random() < 0.25:
                add_opening(edge)

        if edges and all(d == 0 for d in degree):
            add_opening(edges[0])

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

    def generate_level(self):

        rooms = self.generate_rooms()

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


generator = DungeonGenerator()

level = generator.generate_level()

walls = level.walls
teleport = level.teleport_pos

dungeonWalls = [DungeonLevel(walls, teleport)]
