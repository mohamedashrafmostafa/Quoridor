# src/engine/pathfinding.py
from .board import Board, Position, GOAL_ROW, P1, P2
from collections import deque
from typing import List, Optional

# Core BFS
def _bfs(board: Board, start: Position, goal_row: int) -> Optional[List[Position]]:
   
    # Edge case: pawn already on goal row
    if start[0] == goal_row:
        return [start]

    # parent[pos] = which cell we came from (used to reconstruct path)
    parent: dict = {start: None}
    queue: deque = deque([start])

    while queue:
        r, c = queue.popleft()

        # Try all 4 directions: up, down, left, right
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc

            # Skip if out of bounds
            if not board.is_inside(nr, nc):
                continue

            # Skip if already visited
            if (nr, nc) in parent:
                continue

            # Skip if there is a wall between current cell and neighbor
            if board.has_wall_between(r, c, nr, nc):
                continue

            # Mark as visited with parent pointer
            parent[(nr, nc)] = (r, c)

            # Goal check
            if nr == goal_row:
                return _reconstruct_path(parent, start, (nr, nc))

            queue.append((nr, nc))

    # Queue exhausted — no path exists
    return None


def _reconstruct_path(
    parent: dict,
    start: Position,
    end: Position,
) -> List[Position]:
   
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def has_path(board: Board, player: int) -> bool:
    start    = board.get_position(player)
    goal_row = GOAL_ROW[player]
    return _bfs(board, start, goal_row) is not None


def both_players_have_path(board: Board) -> bool:
    return has_path(board, P1) and has_path(board, P2)


def shortest_path_length(board: Board, player: int) -> Optional[int]:
    start    = board.get_position(player)
    goal_row = GOAL_ROW[player]
    path = _bfs(board, start, goal_row)
    if path is None:
        return None
    return len(path) - 1   # nodes - 1 = steps


def get_full_path(board: Board, player: int) -> Optional[List[Position]]:
    start    = board.get_position(player)
    goal_row = GOAL_ROW[player]
    return _bfs(board, start, goal_row)