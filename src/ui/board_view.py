"""
src/ui/board_view.py  —  Grandmaster Edition
============================================
Rendering engine for the 9×9 Quoridor board.
"""
from __future__ import annotations
import math
import pygame

from src.engine.board import BOARD_SIZE, P1, P2
_BG_GUTTER      = (156, 102,  51)  # Tawny/Warm Brown (Board base/gutter)
_CELL_IDLE      = ( 98,  43,  20)  # Dark Earth Brown (Standard tile)
_CELL_HIGHLIGHT = (135,  85,  38)  # Mid-Tone Tawny (Valid-move tile)
_CELL_BORDER    = (137, 131, 104)  # Olive Green (Tile outline & outer frame)
_WALL_COLOR     = (234, 222, 191)  # Pale Cream (Placed walls)
_WALL_PREVIEW   = (234, 222, 191)  # Pale Cream (Preview walls)
_P1_COLOR       = (210,  40,  40)  # Red  – Player 1
_P2_COLOR       = ( 40,  80, 210)  # Blue – Player 2 / AI
_SPEC_WHITE     = (255, 255, 255)  # Specular highlight


def _build_aura_surf(radius: int, color: tuple[int, int, int], rings: int = 6) -> pygame.Surface:
    size = (radius + 6) * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    for i in range(rings, 0, -1):
        r     = int((radius + 4) * i / rings)
        alpha = int(160 * (1 - i / rings) ** 1.2)
        width = max(1, (radius + 4) // rings)
        pygame.draw.circle(surf, (*color, alpha), (cx, cy), r, width=width)
    return surf


class BoardView:
    def __init__(self, play_rect: pygame.Rect) -> None:
        self.cell_size = 56
        self.wall_width = 14

        self._board_px = (BOARD_SIZE * self.cell_size + (BOARD_SIZE - 1) * self.wall_width)
        self.margin_x = play_rect.x + (play_rect.width - self._board_px) // 2
        self.margin_y = play_rect.y + (play_rect.height - self._board_px) // 2

        aura_r = self.cell_size // 2 + 10
        self._aura_p1 = _build_aura_surf(aura_r, _P1_COLOR)
        self._aura_p2 = _build_aura_surf(aura_r, _P2_COLOR)
        self._aura_ai = _build_aura_surf(aura_r + 6, _P2_COLOR, rings=8)

        self._ghost_r = max(6, self.cell_size // 2 - 6)

    def cell_center(self, pos: tuple[int, int]) -> tuple[int, int]:
        r, c = pos
        step = self.cell_size + self.wall_width
        x    = self.margin_x + c * step + self.cell_size // 2
        y    = self.margin_y + r * step + self.cell_size // 2
        return x, y

    def _cell_rect(self, r: int, c: int) -> pygame.Rect:
        step = self.cell_size + self.wall_width
        return pygame.Rect(
            self.margin_x + c * step,
            self.margin_y + r * step,
            self.cell_size,
            self.cell_size,
        )

    def draw(
        self,
        screen:      pygame.Surface,
        board,
        anim_t:      float = 0.0,
        valid_moves: list[tuple[int, int]] | None = None,
        ai_thinking: bool = False,
        wall_preview: dict | None = None,
    ) -> None:
        if valid_moves is None:
            valid_moves = []

        self._draw_gutter(screen)
        self._draw_tiles(screen, valid_moves)
        self._draw_walls(screen, board)

        if wall_preview:
            self._draw_wall_preview(screen, wall_preview)

        self._draw_ghost_pawns(screen, board, valid_moves, anim_t)
        self._draw_pawns(screen, board)

    def _draw_gutter(self, screen: pygame.Surface) -> None:
        gutter = pygame.Rect(
            self.margin_x - 4, self.margin_y - 4,
            self._board_px + 8, self._board_px + 8,
        )
        pygame.draw.rect(screen, _BG_GUTTER, gutter, border_radius=8)

        frame_rect = pygame.Rect(
            self.margin_x - 14, self.margin_y - 14,
            self._board_px + 28, self._board_px + 28
        )
        pygame.draw.rect(screen, _CELL_BORDER, frame_rect, width=2, border_radius=12)

    def _draw_tiles(
        self,
        screen: pygame.Surface,
        valid_moves: list[tuple[int, int]],
    ) -> None:
        vm_set = set(valid_moves)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                rect  = self._cell_rect(r, c)
                color = _CELL_HIGHLIGHT if (r, c) in vm_set else _CELL_IDLE
                pygame.draw.rect(screen, color, rect, border_radius=5)
                pygame.draw.rect(screen, _CELL_BORDER, rect, width=1, border_radius=5)

    def _draw_walls(self, screen: pygame.Surface, board) -> None:
        step = self.cell_size + self.wall_width

        for r, c in board.h_walls:
            rect = pygame.Rect(
                self.margin_x + c * step,
                self.margin_y + (r + 1) * step - self.wall_width,
                self.cell_size * 2 + self.wall_width,
                self.wall_width,
            )
            pygame.draw.rect(screen, _WALL_COLOR, rect, border_radius=4)

        for r, c in board.v_walls:
            rect = pygame.Rect(
                self.margin_x + (c + 1) * step - self.wall_width,
                self.margin_y + r * step,
                self.wall_width,
                self.cell_size * 2 + self.wall_width,
            )
            pygame.draw.rect(screen, _WALL_COLOR, rect, border_radius=4)

    def _draw_wall_preview(self, screen: pygame.Surface, preview: dict) -> None:
        r, c = preview["anchor"]
        horiz = preview["horizontal"]
        step  = self.cell_size + self.wall_width

        surf = pygame.Surface(
            (self.cell_size * 2 + self.wall_width, self.wall_width)
            if horiz else
            (self.wall_width, self.cell_size * 2 + self.wall_width),
            pygame.SRCALPHA,
        )
        surf.fill((*_WALL_PREVIEW, 110))

        if horiz:
            pos = (
                self.margin_x + c * step,
                self.margin_y + (r + 1) * step - self.wall_width,
            )
        else:
            pos = (
                self.margin_x + (c + 1) * step - self.wall_width,
                self.margin_y + r * step,
            )
        screen.blit(surf, pos)

    def _draw_ghost_pawns(
        self,
        screen:      pygame.Surface,
        board,
        valid_moves: list[tuple[int, int]],
        anim_t:      float,
    ) -> None:
        if not valid_moves: return

        pulse = (math.sin(anim_t * math.pi / 0.36) + 1) / 2
        alpha = int(70 + 120 * pulse)

        base_col = _P1_COLOR if board.current_player == P1 else _P2_COLOR
        r        = self._ghost_r
        diam     = r * 2

        ghost = pygame.Surface((diam, diam), pygame.SRCALPHA)
        ghost.fill((0, 0, 0, 0))
        pygame.draw.circle(ghost, (*base_col, alpha),     (r, r), r)
        pygame.draw.circle(ghost, (*base_col, 0),         (r, r), max(2, r - 5))

        for pos in valid_moves:
            cx, cy = self.cell_center(pos)
            screen.blit(ghost, (cx - r, cy - r))

    def _draw_pawns(self, screen: pygame.Surface, board) -> None:
        for player, base_color in [(P1, _P1_COLOR), (P2, _P2_COLOR)]:
            r, c = board.get_position(player)
            cx, cy = self.cell_center((r, c))

            radius = self.cell_size // 3
            pygame.draw.circle(screen, (*base_color, 80), (cx, cy), radius + 4)
            pygame.draw.circle(screen, base_color, (cx, cy), radius)
            pygame.draw.circle(screen, (255, 255, 255), (cx - 4, cy - 4), 4)

    def identify_click(self, mouse_pos: tuple[int, int]) -> tuple[str, object]:
        x, y   = mouse_pos
        step   = self.cell_size + self.wall_width
        rel_x  = x - self.margin_x
        rel_y  = y - self.margin_y

        if rel_x < 0 or rel_y < 0 or rel_x >= self._board_px or rel_y >= self._board_px:
            return "none", None

        col    = rel_x // step
        row    = rel_y // step
        off_x  = rel_x % step
        off_y  = rel_y % step

        col = min(col, BOARD_SIZE - 1)
        row = min(row, BOARD_SIZE - 1)

        if off_x > self.cell_size:
            return "wall", {"anchor": (row, col), "horizontal": False}
        if off_y > self.cell_size:
            return "wall", {"anchor": (row, col), "horizontal": True}
        return "cell", (row, col)

    def get_wall_preview(self, mouse_pos: tuple[int, int]) -> dict | None:
        kind, data = self.identify_click(mouse_pos)
        if kind == "wall": return data
        return None