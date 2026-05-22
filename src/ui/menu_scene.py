# src/ui/menu_scene.py

from __future__ import annotations
import math
import random
import time as _time
import pygame

from src.ui.scene_manager import Scene, SceneManager
from src.ui.game_config import GameConfig, GameMode, Difficulty

BG_MAIN    = ( 98,  43,  20)  # Dark Earth Brown
BG_PANEL   = (156, 102,  51)  # Tawny/Warm Brown
BG_CARD    = (135,  85,  38)  # Mid-Tone Tawny
BG_CARD_A  = (234, 222, 191)  # Pale Cream / Bone
PURPLE     = (234, 222, 191)  # Start Button
PURPLE_DK  = (156, 102,  51)  # Start Button Darker
TEAL       = (137, 131, 104)  # Opponent active background (Olive Green)
AMBER      = (255, 255, 255)  # Walls
TEXT_PRI   = (234, 222, 191)  # Main Titles (Cream)
TEXT_SEC   = (137, 131, 104)  # Sub-Labels (Olive Green)
TEXT_DIM   = ( 98,  43,  20)  # Dark Brown (on Cream backgrounds)
BORDER     = (137, 131, 104)  # Olive Green Borders
BORDER_A   = (234, 222, 191)  # Cream Active Borders

class _AmbientParticle:
    def __init__(self, w, h):
        self.x = random.randint(0, w)
        self.y = random.randint(0, h)
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-10, -3)
        self.size = random.randint(3, 6)
        self.max_life = random.uniform(5, 10)
        self.life = self.max_life

    def update(self, dt_s, w, h):
        self.x += self.vx * dt_s
        self.y += self.vy * dt_s
        self.life -= dt_s
        if self.life <= 0 or self.y < -10:
            self.y = h + 10
            self.x = random.randint(0, w)
            self.life = self.max_life

    def draw(self, screen):
        alpha = int(70 * (self.life / self.max_life))
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*BG_PANEL, alpha), (self.size, self.size), self.size)
        screen.blit(s, (self.x, self.y))

class _TextBox:
    """Interactive text input box for player names."""
    def __init__(self, rect, default_text=""):
        self.rect = rect
        self.text = default_text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < 14 and event.unicode.isprintable():
                self.text += event.unicode

    def draw(self, screen, font):
        bg = BG_CARD_A if self.active else BG_CARD
        brd = BORDER_A if self.active else BORDER
        txt_col = TEXT_DIM if self.active else TEXT_PRI

        pygame.draw.rect(screen, bg, self.rect, border_radius=12)
        pygame.draw.rect(screen, brd, self.rect, width=2, border_radius=12)

        # Blinking cursor effect
        cursor = "|" if self.active and int(_time.time() * 2) % 2 == 0 else ""
        txt_surf = font.render(self.text + cursor, True, txt_col)
        screen.blit(txt_surf, (self.rect.x + 16, self.rect.centery - txt_surf.get_height() // 2))

class MenuScene(Scene):
    W, H = 1000, 750

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.config = GameConfig()

        pygame.font.init()
        self._font_title = pygame.font.SysFont("segoeui", 72, bold=True)
        self._font_sub   = pygame.font.SysFont("segoeui", 22)
        self._font_btn   = pygame.font.SysFont("segoeui", 22, bold=True)
        self._font_sect  = pygame.font.SysFont("segoeui", 16, bold=True)
        self._font_btn_dk = pygame.font.SysFont("segoeui", 22, bold=True)

        self._anim_t = 0.0
        self._particles = [_AmbientParticle(self.W, self.H) for _ in range(60)]

        left_w = 550
        lx = (left_w - 440) // 2 + 30
        
        # FIX: Position Player 2 textbox dynamically just like Player 1
        self._tb_p1 = _TextBox(pygame.Rect(lx, 470, 440, 56), "You")
        self._tb_p2 = _TextBox(pygame.Rect(lx, 570, 440, 56), "Player 2")

        self._init_buttons(left_w, lx)

    def _init_buttons(self, left_w, lx) -> None:
        self._rect_hvh = pygame.Rect(lx, 290, 440, 64)
        self._rect_hvc = pygame.Rect(lx, 366, 440, 64)
        self._rect_start = pygame.Rect(lx, 660, 440, 60) 
        self._chip_rects = []
        for i in range(3):
            width = 136
            if i == 1: width = 144 
            x_pos = lx + i*146
            self._chip_rects.append(pygame.Rect(x_pos, 570, width, 48))

    def handle_event(self, event: pygame.event.Event) -> None:
        # Route events to the correct text boxes
        self._tb_p1.handle_event(event)
        
        if self.config.mode == GameMode.HUMAN_VS_HUMAN:
            self._tb_p2.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect_hvh.collidepoint(event.pos):
                self.config.mode = GameMode.HUMAN_VS_HUMAN
            elif self._rect_hvc.collidepoint(event.pos):
                self.config.mode = GameMode.HUMAN_VS_AI

            if self.config.mode == GameMode.HUMAN_VS_AI:
                for i, r in enumerate(self._chip_rects):
                    if r.collidepoint(event.pos):
                        self.config.difficulty = list(Difficulty)[i]

            if self._rect_start.collidepoint(event.pos):
                # FIX: Save the correct names based on game mode
                self.config.p1_name = self._tb_p1.text.strip() or "Player 1"
                
                if self.config.mode == GameMode.HUMAN_VS_AI:
                    ai_names = ["Ashraf", "Yahia", "Amr"]
                    # difficulty.value is 1, 2, or 3. List index is 0, 1, or 2.
                    self.config.p2_name = ai_names[self.config.difficulty.value - 1]
                else:
                    self.config.p2_name = self._tb_p2.text.strip() or "Player 2"

                from src.ui.game_scene import GameScene
                self.manager.switch(GameScene(self.manager, self.config))

    def update(self, dt: float) -> None:
        dt_s = dt / 1000.0
        self._anim_t += dt_s
        for p in self._particles:
            p.update(dt_s, self.W, self.H)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BG_MAIN)
        for p in self._particles:
            p.draw(screen)

        left_w = 550
        cx = left_w // 2
        lx = (left_w - 440) // 2 + 30

        title = self._font_title.render("QUORIDOR", True, TEXT_PRI)
        screen.blit(title, title.get_rect(centerx=cx, top=100))
      #  sub = self._font_sub.render("CSE472s · AI Project", True, TEXT_SEC)
       # screen.blit(sub, sub.get_rect(centerx=cx, top=180))

        # ── Mode Selection ──
        self._draw_sect_label(screen, "GAME MODE", lx, 255)
        self._draw_mode_card(screen, self._rect_hvh, "Human vs. Human", self.config.mode == GameMode.HUMAN_VS_HUMAN)
        self._draw_mode_card(screen, self._rect_hvc, "Human vs. Computer", self.config.mode == GameMode.HUMAN_VS_AI)

        # ── Player Details (DYNAMIC TOGGLE) ──
        ai_active = self.config.mode == GameMode.HUMAN_VS_AI

        if ai_active:
            self._draw_sect_label(screen, "YOUR NAME", lx, 440)
            self._tb_p1.draw(screen, self._font_sect)
            
            self._draw_sect_label(screen, "OPPONENT", lx, 540)
            opp_names = ["EASY (ASHRAF)", "MEDIUM (YAHIA)", "HARD (AMR)"]
            for i, r in enumerate(self._chip_rects):
                is_sel = (self.config.difficulty.value == (i + 1))
                self._draw_chip(screen, r, opp_names[i], is_sel)
        else:
            self._draw_sect_label(screen, "PLAYER 1 NAME", lx, 440)
            self._tb_p1.draw(screen, self._font_sect)
            
            self._draw_sect_label(screen, "PLAYER 2 NAME", lx, 540)
            self._tb_p2.draw(screen, self._font_sect)

        hover = self._rect_start.collidepoint(pygame.mouse.get_pos())
        self._draw_start_btn(screen, self._rect_start, hover)

        right_w = 450
        right_x = self.W - right_w
        pygame.draw.line(screen, BG_PANEL, (right_x, 0), (right_x, self.H), width=2)
        self._draw_board_preview(screen, right_x + (right_w // 2), self.H // 2)

    def _draw_mode_card(self, screen, rect, label, active):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        if active:
            bg, brd, txt_col = BG_CARD_A, BORDER_A, TEXT_DIM
        elif hover:
            bg, brd, txt_col = BG_PANEL, BORDER_A, TEXT_PRI
        else:
            bg, brd, txt_col = BG_CARD, BORDER, TEXT_PRI

        pygame.draw.rect(screen, bg, rect, border_radius=16)
        pygame.draw.rect(screen, brd, rect, width=2, border_radius=16)

        lbl_fnt = self._font_btn_dk if active else self._font_btn
        lbl = lbl_fnt.render(label, True, txt_col)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_chip(self, screen, rect, label, selected):
        bg = TEAL if selected else BG_CARD
        brd = BORDER_A if selected else BORDER
        pygame.draw.rect(screen, bg, rect, border_radius=24)
        pygame.draw.rect(screen, brd, rect, width=2, border_radius=24)

        txt_col = TEXT_DIM if selected else TEXT_SEC
        lbl = self._font_sect.render(label.upper(), True, txt_col)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_start_btn(self, screen, rect, hover):
        color = PURPLE if hover else BG_PANEL
        txt_col = TEXT_DIM if hover else TEXT_PRI
        pygame.draw.rect(screen, color, rect, border_radius=16)
        lbl = self._font_btn_dk.render("START →", True, txt_col)
        screen.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_sect_label(self, screen, text, x, y, alpha=255):
        lbl = self._font_sect.render(text, True, TEXT_SEC)
        lbl.set_alpha(alpha)
        screen.blit(lbl, (x, y))

    def _draw_board_preview(self, screen, cx, cy):
        cell, wall = 30, 8
        step = cell + wall
        total_size = 9 * cell + 8 * wall
        ox, oy = cx - total_size // 2, cy - total_size // 2

        pygame.draw.rect(screen, BG_PANEL, (ox - 20, oy - 20, total_size + 40, total_size + 40), border_radius=16)
        
        for r in range(9):
            for c in range(9):
                rect = pygame.Rect(ox + c * step, oy + r * step, cell, cell)
                pygame.draw.rect(screen, BG_MAIN, rect, border_radius=6)
                pygame.draw.rect(screen, TEXT_SEC, rect, width=1, border_radius=6)

        for r, c in [(3, 4)]:
            wr = pygame.Rect(ox + c * step, oy + (r + 1) * step - wall, cell * 2 + wall, wall)
            pygame.draw.rect(screen, AMBER, wr, border_radius=3)
        for r, c in [(5, 5)]:
            wr = pygame.Rect(ox + (c + 1) * step - wall, oy + r * step, wall, cell * 2 + wall)
            pygame.draw.rect(screen, AMBER, wr, border_radius=3)

        pulse = (math.sin(self._anim_t * 2) + 1) / 2
        aura_r = cell // 2 + 5
        
        _P1_COLOR, _P2_COLOR = (74, 118, 129), (193, 84, 61)
        
        for pos, col in [( (4, 1), _P2_COLOR), ( (4, 7), _P1_COLOR)]:
            r, c = pos
            centre = (ox + c * step + cell // 2, oy + r * step + cell // 2)
            
            s = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, 80), (aura_r, aura_r), aura_r)
            screen.blit(s, (centre[0] - aura_r, centre[1] - aura_r))
            pygame.draw.circle(screen, col, centre, cell // 3 + 2)