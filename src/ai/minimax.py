# src/ai/minimax.py
import time
from ..engine import *
from ..ai.evaluation import evaluate_board

_transposition_table: dict = {}


# Get Tactical Cells
def _build_hot_zone(p_path, opp_path, p_pos, opp_pos, radius: int = 2) -> set:
    
    zone = set()

    for path in (p_path, opp_path):
        if not path:
            continue
        for (r, c) in path:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    zone.add((r + dr, c + dc))

    for (pr, pc) in (p_pos, opp_pos):
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                zone.add((pr + dr, pc + dc))

    return zone


def _detour_delta(board, player: int, anchor, horizontal: bool) -> int:

    before = shortest_path_length(board, player)
    if before is None:
        return 0

    before = len(path) - 1
    sim = board.copy()
    if horizontal:
        sim.h_walls.add(anchor)
    else:
        sim.v_walls.add(anchor)

    after = shortest_path_length(sim, player)
    if after is None:
        return 99          # complete block — highest possible delta
    return max(0, after - before)


# Heuristic score for a wall placement — used for move ordering
def _score_wall(board, anchor, horizontal: bool, player: int, opp: int) -> float:
   
    opp_delta   = _detour_delta(board, opp,    anchor, horizontal)
    self_delta  = _detour_delta(board, player, anchor, horizontal)

    opp_pos  = board.get_position(opp)
    opp_goal = GOAL_ROW[opp]
    urgency  = 3 if abs(opp_pos[0] - opp_goal) <= 3 else 0

    r, c = anchor
    opp_r, opp_c = opp_pos
    proximity = 1 if abs(r - opp_r) + abs(c - opp_c) <= 3 else 0

    return opp_delta * 10 - self_delta * 5 + urgency + proximity



# Return a list of actions for the current player, ordered for α-β efficiency
def _get_strategic_actions(board):
    
    player = board.current_player
    opp    = 1 - player

    goal_row = GOAL_ROW[player]
    pawn_moves = get_valid_pawn_moves(board, player)

    def pawn_priority(pos):
        # Lower value = tried first. Moves that decrease distance to goal come first.
        return abs(pos[0] - goal_row)

    pawn_actions = sorted(
        [{"type": "move", "target": m} for m in pawn_moves],
        key=lambda a: pawn_priority(a["target"])
    )

    p_pos   = board.get_position(player)
    opp_pos = board.get_position(opp)
    p_path  = get_full_path(board, player)
    opp_path = get_full_path(board, opp)

    hot_zone = _build_hot_zone(p_path, opp_path, p_pos, opp_pos, radius=2)

    wall_candidates = []
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            anchor = (r, c)
            for horiz in (True, False):
                # 1. Hot zone relevance check first (extremely fast)
                if horiz:
                    relevant_cells = [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]
                else:
                    relevant_cells = [(r, c), (r + 1, c), (r, c + 1), (r + 1, c + 1)]

                if not any(cell in hot_zone for cell in relevant_cells):
                    continue

                # 2. Fast validity checks (overlaps, crossings)
                if horiz:
                    if anchor in board.h_walls:
                        continue
                    if (r, c - 1) in board.h_walls:
                        continue
                    if (r, c + 1) in board.h_walls:
                        continue
                    if anchor in board.v_walls:
                        continue
                else:
                    if anchor in board.v_walls:
                        continue
                    if (r - 1, c) in board.v_walls:
                        continue
                    if (r + 1, c) in board.v_walls:
                        continue
                    if anchor in board.h_walls:
                        continue

                # 3. Connectivity check (slower, but only done for hot-zone walls)
                test_board = board.copy()
                if horiz:
                    test_board.h_walls.add(anchor)
                else:
                    test_board.v_walls.add(anchor)

                if not both_players_have_path(test_board):
                    continue

                # 4. Score the valid wall candidate
                score = _score_wall(board, anchor, horiz, player, opp, p_path, opp_path)
                wall_candidates.append((score, anchor, horiz))

    # Sort walls: highest score first
    wall_candidates.sort(key=lambda x: -x[0])

    wall_actions = [
        {"type": "wall", "anchor": anchor, "horizontal": horiz}
        for _, anchor, horiz in wall_candidates
    ]

    return pawn_actions + wall_actions

# Iterative Deepening
def get_best_move_iterative(board, max_depth: int, ai_player: int,
                            use_adv: bool, time_limit: float, game_history: list = None):

    start_time  = time.time()
    best_action = None
    _transposition_table.clear()

    for depth in range(1, max_depth + 1):
        elapsed = time.time() - start_time
        if elapsed > time_limit:
            break
        # Don't start a depth we almost certainly cannot finish
        remaining = time_limit - elapsed
        if depth > 1 and remaining < time_limit * 0.10:
            break

        try:
            _, move = minimax(board, depth, float('-inf'), float('inf'),
                              True, ai_player, use_adv, start_time, time_limit, game_history)
            if move:
                best_action = move
        except TimeoutError:
            # An incomplete depth iteration was interrupted. Discard its results.
            break

    return best_action


# Minimax with α-β + Transposition-table (depth added)
def minimax(board, depth: int, alpha: float, beta: float,
            maximizing: bool, ai_player: int, use_adv: bool,
            start_t: float, limit: float, game_history: list):

    key = (board.positions[0], board.positions[1],
           frozenset(board.h_walls), frozenset(board.v_walls),
           board.walls_left[0], board.walls_left[1],
           board.current_player)

    if key in _transposition_table:
        stored_depth, stored_score, stored_move = _transposition_table[key]
        if stored_depth >= depth:          # only trust deeper/equal entries
            return stored_score, stored_move

    if time.time() - start_t > limit or depth == 0 or is_game_over(board):
        return evaluate_board(board, ai_player, use_adv, game_history), None

    actions = _get_strategic_actions(board)

    best_move = None
    if maximizing:
        max_eval = float('-inf')
        for action in actions:
            sim = board.copy()
            if action["type"] == "move":
                apply_pawn_move(sim, board.current_player, action["target"])
            else:
                apply_wall(sim, board.current_player,
                           action["anchor"], bool(action["horizontal"]))

            val, _ = minimax(sim, depth - 1, alpha, beta,
                             False, ai_player, use_adv, start_t, limit, game_history)
            if val > max_eval:
                max_eval, best_move = val, action
            alpha = max(alpha, val)
            if beta <= alpha:
                break   # β cut-off

        _transposition_table[key] = (depth, max_eval, best_move)
        return max_eval, best_move

    else:
        min_eval = float('inf')
        for action in actions:
            sim = board.copy()
            if action["type"] == "move":
                apply_pawn_move(sim, board.current_player, action["target"])
            else:
                apply_wall(sim, board.current_player,
                           action["anchor"], bool(action["horizontal"]))

            val, _ = minimax(sim, depth - 1, alpha, beta,
                             True, ai_player, use_adv, start_t, limit, game_history)
            if val < min_eval:
                min_eval, best_move = val, action
            beta = min(beta, val)
            if beta <= alpha:
                break   # α cut-off

        _transposition_table[key] = (depth, min_eval, best_move)
        return min_eval, best_move