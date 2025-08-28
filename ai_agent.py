# ai_agent.py
from typing import Optional, Tuple, List
from wumpus import WumpusWorld, neighbors

class SimpleAgent:
    """
    Very simple heuristic agent:
    - Prefer unvisited SAFE neighbors (inferred when no breeze/stench at current cell).
    - If gold is here, grab.
    - If at start with gold, climb.
    - Otherwise, cautiously explore unvisited neighbors; if none, backtrack to start.
    """
    def __init__(self):
        self.path_stack: List[Tuple[int, int]] = []

    def next_action(self, world: WumpusWorld) -> dict:
        if world.game_over:
            return {"type": "noop"}

        # If on gold, grab
        if world.agent == world.gold and not world.has_gold:
            return {"type": "grab"}

        # If back at start with gold, climb
        if world.agent == (world.size - 1, 0) and world.has_gold:
            return {"type": "climb"}

        # Explore: prefer safe & unvisited neighbors
        nbs = neighbors(world.agent, world.size)
        safe_unvisited = [n for n in nbs if n in world.safe and n not in world.visited]

        # fallback: unvisited (not marked unsafe anywhere in this simple agent)
        if not safe_unvisited:
            fallback = [n for n in nbs if n not in world.visited]
        else:
            fallback = []

        target = None
        if safe_unvisited:
            target = safe_unvisited[0]
        elif fallback:
            target = fallback[0]
        else:
            # no good options; try moving toward start to exit if gold collected
            sx, sy = world.size - 1, 0
            ax, ay = world.agent
            if world.has_gold:
                # Greedy step toward start
                if ax < sx:
                    return {"type": "move", "dir": "down"}
                if ay > sy:
                    return {"type": "move", "dir": "left"}
                if ax > sx:
                    return {"type": "move", "dir": "up"}
                if ay < sy:
                    return {"type": "move", "dir": "right"}
                return {"type": "climb"}
            # else just pick a visited neighbor to wander
            for n in nbs:
                if n in world.visited:
                    target = n
                    break

        if target:
            ax, ay = world.agent
            tx, ty = target
            if tx < ax: return {"type": "move", "dir": "up"}
            if tx > ax: return {"type": "move", "dir": "down"}
            if ty < ay: return {"type": "move", "dir": "left"}
            if ty > ay: return {"type": "move", "dir": "right"}

        return {"type": "noop"}
