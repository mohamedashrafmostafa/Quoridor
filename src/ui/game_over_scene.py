# src/ui/game_over_scene.py
from __future__ import annotations
import math
import random
import time as _time
from typing import Optional
import pygame

from src.ui.scene_manager import Scene, SceneManager
from src.ui.game_config import GameConfig
from src.engine.board import P1, P2

BG_MAIN    = ( 98,  43,  20)  # Dark Earth Brown
BG_PANEL   = (156, 102,  51)  # Tawny/Warm Brown
BG_CARD    = (135,  85,  38)  # Mid-Tone Tawny
BG_CARD_A  = (234, 222, 191)  # Pale Cream / Bone
BORDER     = (137, 131, 104)  # Olive Green Borders
BORDER_A   = (234, 222, 191)  # Cream Active Borders
TEXT_PRI   = (234, 222, 191)  # Cream
TEXT_SEC   = (234, 222, 191)  # Cream
TEXT_DIM   = (137, 131, 104)  # Olive Green (for subtext)
TEXT_INV   = ( 62,  27,  12)  # Dark Brown (Text on Cream)
RED_PLAYER = (193,  84,  61)  # Terracotta
BLUE_AI    = ( 74, 118, 129)  # Slate Blue
OVERLAY    = ( 62,  27,  12, 190) # Very Dark Brown, semi-transparent

# Earthy confetti particle colors
_PARTICLE_PALETTE = [
    (234, 222, 191, 255),  # Cream
    (156, 102,  51, 255),  # Tawny
    (137, 131, 104, 255),  # Olive Green
    (193,  84,  61, 255),  # Terracotta
    ( 74, 118, 129, 210),  # Slate Blue
]

_SLIDE_DURATION_S = 0.85
_GRAVITY_PX_S2    = 300.0   

# ── Procedural Vector Icons ──
def _draw_icon_crown(screen, color, cx, cy, scale=1.0):
    w = 40 * scale
    h = 24 * scale
    pts = [
        (cx - w//2, cy + h//2),
        (cx + w//2, cy + h//2),
        (cx + w//2 + 6*scale, cy - h//2 + 6*scale),
        (cx + w//6, cy),
        (cx, cy - h//2 - 4*scale),
        (cx - w//6, cy),
        (cx - w//2 - 6*scale, cy - h//2 + 6*scale)
    ]
    pygame.draw.polygon(screen, color, pts)
    # Jewels on tips
    pygame.draw.circle(screen, color, (cx - w//2 - 6*scale, cy - h//2 + 6*scale), 5*scale)
    pygame.draw.circle(screen, color, (cx, cy - h//2 - 4*scale), 5*scale)
    pygame.draw.circle(screen, color, (cx + w//2 + 6*scale, cy - h//2 + 6*scale), 5*scale)
    # Inner base cutline
    pygame.draw.line(screen, BG_CARD, (cx - w//2 + 4*scale, cy + h//2 - 5*scale), (cx + w//2 - 4*scale, cy + h//2 - 5*scale), max(1, int(3*scale)))

def _draw_icon_reset(screen, color, cx, cy):
    pygame.draw.arc(screen, color, (cx-6, cy-6, 12, 12), math.radians(45), math.radians(315), 2)
    pygame.draw.polygon(screen, color, [(cx+5, cy-5), (cx+5, cy-10), (cx, cy-5)])

def _draw_icon_home(screen, color, cx, cy):
    pygame.draw.polygon(screen, color, [(cx, cy-6), (cx-6, cy), (cx-4, cy), (cx-4, cy+6), (cx+4, cy+6), (cx+4, cy), (cx+6, cy)], 2)
    pygame.draw.rect(screen, color, (cx-1, cy+2, 3, 4))


class _Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "radius", "color")
    def __init__(self, cx: float, cy: float) -> None:
        angle        = random.uniform(0, math.tau)
        speed        = random.uniform(70, 360)
        self.x       = cx
        self.y       = cy
        self.vx      = math.cos(angle) * speed
        self.vy      = math.sin(angle) * speed - random.uniform(30, 110)
        self.max_life = random.uniform(0.55, 1.45)
        self.life    = self.max_life
        self.radius  = random.randint(3, 7)
        self.color   = random.choice(_PARTICLE_PALETTE)

    def update(self, dt_s: float) -> None:
        self.vy  += _GRAVITY_PX_S2 * dt_s
        self.x   += self.vx * dt_s
        self.y   += self.vy * dt_s
        self.life = max(0.0, self.life - dt_s)

    @property
    def alive(self) -> bool: return self.life > 0.0

    def draw(self, screen: pygame.Surface) -> None:
        alpha = int(255 * (self.life / self.max_life))
        r, g, b, _ = self.color
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (r, g, b, alpha), (self.radius, self.radius), self.radius)
        screen.blit(s, (int(self.x) - self.radius, int(self.y) - self.radius))

def _frosted_crop(source: pygame.Surface, rect: pygame.Rect, blur_factor: int = 7) -> pygame.Surface:
    crop = source.subsurface(rect).copy()
    small_w = max(1, rect.w // blur_factor)
    small_h = max(1, rect.h // blur_factor)
    small = pygame.transform.smoothscale(crop, (small_w, small_h))
    return pygame.transform.smoothscale(small, (rect.w, rect.h))


class GameOverScene(Scene):
    W, H = 1000, 750

    def __init__(self, manager: SceneManager, config: GameConfig, winner: str, winner_idx: int = P1, screenshot: Optional[pygame.Surface] = None) -> None:
        super().__init__(manager)
        self.config = config
        self.winner = winner
        self.winner_idx = winner_idx
        self.screenshot = screenshot

        pygame.font.init()
        self._font_h1  = pygame.font.SysFont("segoeui", 32, bold=True)
        self._font_sub = pygame.font.SysFont("segoeui", 14, bold=True)
        self._font_btn = pygame.font.SysFont("segoeui", 17, bold=True)

        self._cw = 360
        self._ch = 330
        self._card_x = (self.W - self._cw) // 2
        self._final_y = (self.H - self._ch) // 2 

        bx = self._card_x + 28
        bw = self._cw - 56
        self._btn_play = pygame.Rect(bx, 0, bw, 50) 
        self._btn_menu = pygame.Rect(bx, 0, bw, 42) 
        self._hover_play, self._hover_menu = False, False

        self._overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self._overlay.fill(OVERLAY)

        card_rect = pygame.Rect(self._card_x, self._final_y, self._cw, self._ch)
        if screenshot and screenshot.get_size() == (self.W, self.H):
            safe_rect = card_rect.clip(screenshot.get_rect())
            self._frosted_bg: Optional[pygame.Surface] = (_frosted_crop(screenshot, safe_rect) if safe_rect.size == card_rect.size else None)
        else:
            self._frosted_bg = None

        self._enter_t = _time.monotonic()
        self._anim_t  = 0.0
        self._particles: list[_Particle] = [_Particle(self.W // 2, self.H // 2) for _ in range(70)]

    def on_enter(self) -> None:
        self._enter_t = _time.monotonic()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._hover_play = self._btn_play.collidepoint(event.pos)
            self._hover_menu = self._btn_menu.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER): self._restart()
            elif event.key == pygame.K_ESCAPE: self._go_menu()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_play.collidepoint(event.pos): self._restart()
            elif self._btn_menu.collidepoint(event.pos): self._go_menu()

    def update(self, dt: float) -> None:
        dt_s = dt / 1000.0
        self._anim_t += dt_s
        for p in self._particles: p.update(dt_s)
        self._particles = [p for p in self._particles if p.alive]

    def draw(self, screen: pygame.Surface) -> None:
        if self.screenshot: screen.blit(self.screenshot, (0, 0))
        else: screen.fill(BG_MAIN)
        screen.blit(self._overlay, (0, 0))

        for p in self._particles: p.draw(screen)

        raw = min(1.0, self._anim_t / _SLIDE_DURATION_S)
        eased = 1.0 - (1.0 - raw) ** 3
        card_y = int(-self._ch + (self._final_y + self._ch) * eased)
        self._draw_card(screen, card_y)

    def _draw_card(self, screen: pygame.Surface, card_y: int) -> None:
        card = pygame.Rect(self._card_x, card_y, self._cw, self._ch)

        if self._frosted_bg:
            fb = self._frosted_bg.copy()
            fb.set_alpha(150)
            screen.blit(fb, card.topleft)

        fill = pygame.Surface((self._cw, self._ch), pygame.SRCALPHA)
        fill.fill((*BG_CARD, 240))
        screen.blit(fill, card.topleft)

        # Highlight color matches the winner
        accent_col = RED_PLAYER if self.winner_idx == P1 else BLUE_AI
        
        pygame.draw.rect(screen, accent_col, card, width=2, border_radius=18)
        
        outer = card.inflate(4, 4)
        outer_s = pygame.Surface((outer.w, outer.h), pygame.SRCALPHA)
        pygame.draw.rect(outer_s, (*accent_col, 60), (0, 0, outer.w, outer.h), width=2, border_radius=19)
        screen.blit(outer_s, outer.topleft)

        cx, ty = card.centerx, card.top + 24

        # ── Procedural Crown ──
        scale = 1.0 + 0.08 * math.sin(self._anim_t * math.tau / 1.4)
        _draw_icon_crown(screen, accent_col, cx, ty + 20, scale)

        sub = self._font_sub.render("W I N N E R", True, TEXT_DIM)
        screen.blit(sub, sub.get_rect(centerx=cx, top=ty + 70))

        name_surf  = self._font_h1.render(self.winner, True, TEXT_PRI)
        tint_surf  = self._font_h1.render(self.winner, True, accent_col)
        tint_surf.set_alpha(95)
        name_rect  = name_surf.get_rect(centerx=cx, top=ty + 102)
        screen.blit(name_surf, name_rect)
        screen.blit(tint_surf, name_rect)

        pygame.draw.circle(screen, accent_col, (name_rect.left - 14, name_rect.centery), 6)

        div_y = card.top + 216
        pygame.draw.line(screen, BORDER, (card.left + 28, div_y), (card.right - 28, div_y))

        btn_y = div_y + 14
        self._btn_play.y = btn_y
        self._btn_menu.y = btn_y + 60

        self._draw_play_btn(screen, self._btn_play)
        self._draw_menu_btn(screen, self._btn_menu)

    def _draw_play_btn(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        col = BG_CARD_A if self._hover_play else BG_PANEL
        txt_col = TEXT_INV if self._hover_play else TEXT_PRI
        pygame.draw.rect(screen, col, rect, border_radius=10)
        
        if self._hover_play:
            glow = rect.inflate(4, 4)
            gs = pygame.Surface((glow.w, glow.h), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*BG_CARD_A, 50), (0, 0, glow.w, glow.h), border_radius=12)
            screen.blit(gs, glow.topleft)
            
        lbl = self._font_btn.render("Play Again", True, txt_col)
        total_w = 16 + 12 + lbl.get_width()
        start_x = rect.x + (rect.w - total_w) // 2
        
        _draw_icon_reset(screen, txt_col, start_x + 8, rect.centery)
        screen.blit(lbl, (start_x + 28, rect.centery - lbl.get_height() // 2))

    def _draw_menu_btn(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        bg_col = BG_CARD_A if self._hover_menu else BG_CARD
        brd_col = BORDER_A if self._hover_menu else BORDER
        txt_col = TEXT_INV if self._hover_menu else TEXT_PRI
        
        pygame.draw.rect(screen, bg_col, rect, border_radius=10)
        pygame.draw.rect(screen, brd_col, rect, width=2, border_radius=10)
        
        lbl = self._font_btn.render("Main Menu", True, txt_col)
        total_w = 16 + 12 + lbl.get_width()
        start_x = rect.x + (rect.w - total_w) // 2
        
        _draw_icon_home(screen, txt_col, start_x + 8, rect.centery)
        screen.blit(lbl, (start_x + 28, rect.centery - lbl.get_height() // 2))

    def _restart(self) -> None:
        from src.ui.game_scene import GameScene  
        self.manager.switch_fade(GameScene(self.manager, self.config))

    def _go_menu(self) -> None:
        from src.ui.menu_scene import MenuScene 
        self.manager.switch_fade(MenuScene(self.manager))