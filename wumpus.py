# wumpus.py
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Set, Optional, Dict

Coord = Tuple[int, int]

DIRECTIONS: Dict[str, Coord] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

def in_bounds(pos: Coord, size: int) -> bool:
    x, y = pos
    return 0 <= x < size and 0 <= y < size

def neighbors(pos: Coord, size: int) -> List[Coord]:
    x, y = pos
    nbs = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
    return [p for p in nbs if in_bounds(p, size)]

@dataclass
class WumpusWorld:
    size: int = 4
    pits_count: int = 3
    agent: Coord = (0, 0)
    wumpus: Coord = (0, 0)
    gold: Coord = (0, 0)
    pits: Set[Coord] = field(default_factory=set)
    visited: Set[Coord] = field(default_factory=set)
    safe: Set[Coord] = field(default_factory=set)
    has_gold: bool = False
    wumpus_alive: bool = True
    arrow_available: bool = True
    scream_heard: bool = False
    game_over: bool = False
    status: str = "Welcome to Wumpus World!"
    score: int = 0
    discovered: Set[Coord] = field(default_factory=set)

    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.agent = (self.size - 1, 0)  # bottom-left start (classic)
        forbidden = {self.agent}
        self.pits = set()
        while len(self.pits) < self.pits_count:
            p = (random.randrange(self.size), random.randrange(self.size))
            if p not in forbidden:
                self.pits.add(p)
        # place wumpus
        while True:
            w = (random.randrange(self.size), random.randrange(self.size))
            if w not in forbidden and w not in self.pits:
                self.wumpus = w
                break
        # place gold
        while True:
            g = (random.randrange(self.size), random.randrange(self.size))
            if g not in forbidden and g not in self.pits and g != self.wumpus:
                self.gold = g
                break
        self.visited = {self.agent}
        self.safe = {self.agent}
        self.has_gold = False
        self.wumpus_alive = True
        self.arrow_available = True
        self.scream_heard = False
        self.game_over = False
        self.status = "Game reset. Navigate, grab gold, and return to start!"
        self.score = 0
        self.discovered = {self.agent}

    def percepts(self) -> Dict[str, bool]:
        # Classic percepts: breeze near pits, stench near Wumpus, glitter on gold
        pos = self.agent
        adj = neighbors(pos, self.size)
        breeze = any(a in self.pits for a in adj)
        stench = any(a == self.wumpus for a in adj) if self.wumpus_alive else False
        glitter = (pos == self.gold and not self.has_gold)
        bump = False  # handled on illegal move attempt; not stored persistently here
        return {
            "breeze": breeze,
            "stench": stench,
            "glitter": glitter,
            "scream": self.scream_heard,
            "bump": bump
        }

    def _die(self, reason: str):
        self.game_over = True
        self.status = reason + " Game over."
        self.score -= 100

    def _check_hazards(self):
        if self.agent in self.pits:
            self._die("You fell into a pit!")
        elif self.agent == self.wumpus and self.wumpus_alive:
            self._die("The Wumpus got you!")

    def move(self, direction: str) -> Dict:
        if self.game_over:
            return self.state()
        dx, dy = DIRECTIONS.get(direction, (0, 0))
        x, y = self.agent
        nx, ny = x + dx, y + dy
        if not in_bounds((nx, ny), self.size):
            self.status = "Bump! Can't move outside the cave."
            self.score -= 1
            return self.state()
        self.agent = (nx, ny)
        self.visited.add(self.agent)
        self.discovered.add(self.agent)
        self.score -= 1
        self._check_hazards()
        if not self.game_over:
            self.status = f"Moved {direction}."
        return self.state()

    def grab(self) -> Dict:
        if self.game_over:
            return self.state()
        if self.agent == self.gold and not self.has_gold:
            self.has_gold = True
            self.status = "You grabbed the gold! Now get back to start!"
            self.score += 50
        else:
            self.status = "Nothing to grab here."
            self.score -= 1
        return self.state()

    def shoot(self, direction: str) -> Dict:
        if self.game_over:
            return self.state()
        if not self.arrow_available:
            self.status = "No arrows left."
            self.score -= 1
            return self.state()
        self.arrow_available = False
        self.score -= 10
        # Arrow travels straight until wall; if along the path there's the Wumpus in that row/col and in direction, it dies.
        ax, ay = self.agent
        dx, dy = DIRECTIONS.get(direction, (0, 0))
        hit = False
        while True:
            ax += dx
            ay += dy
            if not in_bounds((ax, ay), self.size):
                break
            if (ax, ay) == self.wumpus and self.wumpus_alive:
                self.wumpus_alive = False
                hit = True
                self.scream_heard = True
                break
        self.status = "You hear a terrifying scream!" if hit else "Arrow whooshes into the darkness."
        return self.state()

    def climb(self) -> Dict:
        if self.game_over:
            return self.state()
        if self.agent == (self.size - 1, 0):
            # Exit with or without gold (classic scoring rewards gold)
            if self.has_gold:
                self.status = "You escaped with the gold! You win! 🎉"
                self.score += 100
            else:
                self.status = "You escaped. No gold this time."
            self.game_over = True
        else:
            self.status = "You can only climb at the start tile."
            self.score -= 1
        return self.state()

    def mark_safe_from_percepts(self):
        # very lightweight inference: if no breeze and no stench => all neighbors are safe
        p = self.percepts()
        if not p["breeze"] and not p["stench"]:
            for nb in neighbors(self.agent, self.size):
                self.safe.add(nb)

    def reveal(self) -> Dict:
        # developer/assist function: reveal map for debugging (not used by AI)
        self.discovered = {(x, y) for x in range(self.size) for y in range(self.size)}
        return self.state(reveal_all=True)

    def state(self, reveal_all: bool = False) -> Dict:
        p = self.percepts()
        self.mark_safe_from_percepts()
        # Build lightweight map for UI
        tiles = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                cell = {
                    "x": i, "y": j,
                    "visited": (i, j) in self.visited,
                    "discovered": reveal_all or (i, j) in self.discovered,
                    "agent": (i, j) == self.agent,
                    "gold": (i, j) == self.gold and (reveal_all or (i, j) in self.discovered) and not self.has_gold,
                    "wumpus": (i, j) == self.wumpus and (reveal_all or (i, j) in self.discovered) and self.wumpus_alive,
                    "pit": (i, j) in self.pits and (reveal_all or (i, j) in self.discovered),
                    "safe": (i, j) in self.safe
                }
                row.append(cell)
            tiles.append(row)
        return {
            "size": self.size,
            "tiles": tiles,
            "agent": self.agent,
            "has_gold": self.has_gold,
            "wumpus_alive": self.wumpus_alive,
            "arrow_available": self.arrow_available,
            "scream_heard": self.scream_heard,
            "game_over": self.game_over,
            "status": self.status,
            "score": self.score,
            "percepts": p
        }
