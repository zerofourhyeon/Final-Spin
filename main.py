import pygame
import random
import math
import os
from enum import Enum

# --- 상수 정의 ---

# 색상
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# 창 크기 및 제목
WINDOW_WIDTH = 1260
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Buckshot Roulette"

# 폰트
FONT_NAME = None  # 시스템 기본 폰트 사용
FONT_SIZE = 25
MENU_FONT_SIZE = 60  # 메뉴 폰트 크기
BOLD_FONT = True  # 굵은 폰트 사용 여부

# 이미지 경로
IMAGE_DIR = "images"
BACKGROUND_IMAGE_PATH = os.path.join(IMAGE_DIR, "background.png")
BLUR_BACKGROUND_IMAGE_PATH = os.path.join(IMAGE_DIR, "blur_background.png")
SHOTGUN_IMAGE_PATH = os.path.join(IMAGE_DIR, "shotgun.png")
BLANK_IMAGE_PATH = os.path.join(IMAGE_DIR, "fake_bullet.png")
LIVE_IMAGE_PATH = os.path.join(IMAGE_DIR, "real_bullet.png")
TABLE_IMAGE_PATH = os.path.join(IMAGE_DIR, "table.png")
GRENADE_IMAGE_PATH = os.path.join(IMAGE_DIR, "grenade.png")
SCARECROW_IMAGE_PATH = os.path.join(IMAGE_DIR, "scarecrow.png")
SYRINGE_IMAGE_PATH = os.path.join(IMAGE_DIR, "syringe.png")
BULLET_ENHANCE_IMAGE_PATH = os.path.join(IMAGE_DIR, "bullet.png")

# 사운드 경로
SOUND_DIR = "sounds"
REAL_BULLET_SOUND_PATH = os.path.join(SOUND_DIR, "real_bullet.wav")
FAKE_BULLET_SOUND_PATH = os.path.join(SOUND_DIR, "fake_bullet.wav")
BULLET_ENHANCED_SOUND_PATH = os.path.join(SOUND_DIR, "bullet.wav")
BULLET_CARD_SOUND_PATH = os.path.join(SOUND_DIR, "bullet_card.wav")
CARD_SOUND_PATH = os.path.join(SOUND_DIR, "card.wav")
CARD_DELETE_SOUND_PATH = os.path.join(SOUND_DIR, "card_delete.wav")
SYRINGE_SOUND_PATH = os.path.join(SOUND_DIR, "syringe.wav")
GRENADE_SOUND_PATH = os.path.join(SOUND_DIR, "grenade.wav")
SCARECROW_CARD_SOUND_PATH = os.path.join(SOUND_DIR, "scarecrow_card.wav")
SCARECROW_SOUND_PATH = os.path.join(SOUND_DIR, "scarecrow.wav")
GAME_OVER_SOUND_PATH = os.path.join(SOUND_DIR, "game_over.wav")
DRAW_SOUND_PATH = os.path.join(SOUND_DIR, "draw.wav")

# 게임 설정
INITIAL_LIVES = 5
NB_SLOTS = 8

# 아이템 카드 크기
ITEM_WIDTH = 165
ITEM_HEIGHT = 214

# --- 열거형 정의 ---

class MenuState(Enum):
    MAIN = 0

class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1

# --- 클래스 ---

class Weapon:
    def __init__(self, player_lives):
        # 샷건 이미지 로드 및 크기 조정
        try:
            self.shotgun = pygame.image.load(SHOTGUN_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load shotgun image: {e}")
            self.shotgun = pygame.Surface((340, 100), pygame.SRCALPHA)  # 크기 확대
        self.shotgun = pygame.transform.scale(self.shotgun, (340, 100))  # 크기 확대

        # 공포탄 이미지 로드
        try:
            self.blank = pygame.image.load(BLANK_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load blank bullet image: {e}")
            self.blank = pygame.Surface((35, 18), pygame.SRCALPHA)
        self.blank = pygame.transform.scale(self.blank, (40, 23))
        self.blank = pygame.transform.rotate(self.blank, -90)

        # 실탄 이미지 로드
        try:
            self.live = pygame.image.load(LIVE_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load live bullet image: {e}")
            self.live = pygame.Surface((35, 18), pygame.SRCALPHA)
        self.live = pygame.transform.scale(self.live, (40, 23))
        self.live = pygame.transform.rotate(self.live, -90)

        # 사운드 로드
        try:
            self.real_bullet_sound = pygame.mixer.Sound(REAL_BULLET_SOUND_PATH)
            self.fake_bullet_sound = pygame.mixer.Sound(FAKE_BULLET_SOUND_PATH)
            self.bullet_enhanced_sound = pygame.mixer.Sound(
                BULLET_ENHANCED_SOUND_PATH
            )  # bullet.wav 사운드 추가
        except pygame.error as e:
            print(f"Failed to load bullet sound: {e}")
            self.real_bullet_sound = None
            self.fake_bullet_sound = None
            self.bullet_enhanced_sound = None  # None으로 초기화

        self.player_lives = player_lives
        self.magazine = []
        self.blanks = []  # 공포탄 인덱스 저장
        self.lives = []  # 실탄 인덱스 저장

    def reload(self):
        """총알을 재장전"""
        if not self.magazine or 0 in self.player_lives:
            self.magazine = []
            self.blanks = []
            self.lives = []
            magazine_capacity = random.randint(2, 8)
            if magazine_capacity == 2:
                nb_live_bullets = 1
            else:
                nb_live_bullets = random.uniform(
                    magazine_capacity / 4, float(magazine_capacity // 2)
                )
            ceil_nb_live_bullets = math.ceil(nb_live_bullets)

            # 실탄과 공포탄을 분리하여 리스트에 추가
            for i in range(ceil_nb_live_bullets):
                self.magazine.append(1)
                self.lives.append(len(self.magazine) - 1)
            for i in range(magazine_capacity - ceil_nb_live_bullets):
                self.magazine.append(0)
                self.blanks.append(len(self.magazine) - 1)

            random.shuffle(self.magazine)  # 섞인 탄창

            # 섞인 탄창을 기반으로 실탄과 공포탄 인덱스 업데이트
            self.blanks = [i for i, x in enumerate(self.magazine) if x == 0]
            self.lives = [i for i, x in enumerate(self.magazine) if x == 1]

    def shoot(self, bullet_enhanced, current_player, scarecrow_protected, target_player):
        """총알 발사 및 사운드 재생"""
        if self.magazine:
            if len(self.blanks) > 0 and len(self.lives) > 0:  # 실탄과 공포탄이 모두 있는 경우
                if random.choice([True, False]):  # 무작위로 실탄 또는 공포탄 선택
                    index = random.choice(self.lives)
                else:
                    index = random.choice(self.blanks)
            elif len(self.lives) > 0:  # 실탄만 있는 경우
                index = random.choice(self.lives)
            else:  # 공포탄만 있는 경우
                index = random.choice(self.blanks)

            bullet_type = self.magazine.pop(index)

            # 실탄 및 공포탄 인덱스 업데이트
            self.blanks = [i for i in self.blanks if i < index] + [
                i - 1 for i in self.blanks if i > index
            ]
            self.lives = [i for i in self.lives if i < index] + [
                i - 1 for i in self.lives if i > index
            ]

            # 사운드 재생
            if bullet_type == 1:
                if not scarecrow_protected[target_player]:  # scarecrow가 비활성화 된 경우에만 실탄 사운드 재생
                    if bullet_enhanced[current_player]:
                        # bullet 카드 효과가 적용된 실탄일 경우 bullet.wav 재생
                        if self.bullet_enhanced_sound:
                            self.bullet_enhanced_sound.play()
                    elif self.real_bullet_sound:
                        # 일반 실탄일 경우 real_bullet.wav 재생
                        self.real_bullet_sound.play()
            elif bullet_type == 0 and self.fake_bullet_sound:
                # 공포탄일 경우 fake_bullet.wav 재생
                self.fake_bullet_sound.play()

            return bullet_type
        else:
            return None

    def display_bullet(self, window, pos_x, color):
        """총알 표시 (박스 포함)"""
        bullet_width = 15  # 총알 너비 확대
        bullet_height = 30  # 총알 높이 확대
        bullet_rect = pygame.Rect(
            pos_x, WINDOW_HEIGHT - bullet_height - 200, bullet_width, bullet_height
        )  # 위치 및 크기 조정
        pygame.draw.rect(window, color, bullet_rect, 0)
        pygame.draw.rect(
            window, BLACK, (pos_x, WINDOW_HEIGHT - bullet_height - 200 - 8, bullet_width, 8), 0
        )

        # 박스 그리기 (총알 크기에 맞게 조정, 흰색으로 변경)
        box_rect = pygame.Rect(
            pos_x - 6,
            WINDOW_HEIGHT - bullet_height - 200 - 18,
            bullet_width + 12,
            bullet_height + 26,
        )  # 박스 크기 조정
        pygame.draw.rect(window, WHITE, box_rect, 2)  # 테두리 색상 흰색으로 변경

    def display_shotgun(self, window):
        """샷건 이미지 표시"""
        window.blit(self.shotgun, (WINDOW_WIDTH // 2 - 170, WINDOW_HEIGHT // 2 - 50))

    def display_magazine(self, window):
        """화면에 현재 탄창 상태를 중앙에 렌더링 (박스 포함)"""
        bullets_margin = 15  # 총알 간 추가 간격
        bullet_width = 15  # 총알 너비
        total_bullets_width = (
            len(self.magazine) * (bullet_width + bullets_margin) - bullets_margin
        )
        start_pos_x = (WINDOW_WIDTH - total_bullets_width) // 2

        for i, bullet_type in enumerate(self.magazine):
            pos_x = start_pos_x + i * (bullet_width + bullets_margin)
            if bullet_type == 0:
                self.display_bullet(window, pos_x, WHITE)
            else:
                self.display_bullet(window, pos_x, RED)

class Syringe:
    def __init__(self, position):
        # 주사기 이미지 로드
        try:
            self.image = pygame.image.load(SYRINGE_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load syringe image: {e}")
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image = pygame.transform.scale(self.image, (ITEM_WIDTH, ITEM_HEIGHT))
        self.rect = self.image.get_rect(topleft=position)
        self.active = False  # 수정: 초기값을 False로 변경
        self.used_this_turn = False  # 턴당 사용 여부 추적 변수 추가

        # 사운드 로드
        try:
            self.sound = pygame.mixer.Sound(SYRINGE_SOUND_PATH)  # syringe.wav 로드
        except pygame.error as e:
            print(f"Failed to load syringe sound: {e}")
            self.sound = None

    def heal(self, player_lives, player_index):
        """플레이어의 생명력을 1 회복"""
        if player_lives[player_index] < INITIAL_LIVES:
            player_lives[player_index] += 1
            self.active = False
            if self.sound:  # 사운드 재생
                self.sound.play()

    def display_syringe(self, window):
        """지정된 위치에 주사기 표시"""
        if not self.active:
            return
        if self.active:
            window.blit(self.image, self.rect.topleft)

    def reactivate(self):
        """50% 확률로 주사기를 재활성화"""
        self.active = random.choice([True, False])  # 수정: 50%로 다시 변경

    def is_clicked(self, mouse_pos):
        """주사기가 클릭되었는지 확인"""
        return self.active and self.rect.collidepoint(mouse_pos)

class Bullet:
    def __init__(self, position, size=(50, 69)):  # 수정: 크기 조정
        # 총알 이미지 로드
        try:
            self.image = pygame.image.load(BULLET_ENHANCE_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load bullet image: {e}")
            self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image = pygame.transform.scale(self.image, (ITEM_WIDTH, ITEM_HEIGHT))
        self.rect = self.image.get_rect(topleft=position)
        self.active = True
        self.used_this_turn = False  # 턴당 사용 여부 추적 변수 추가

        # 사운드 로드
        try:
            self.sound = pygame.mixer.Sound(BULLET_CARD_SOUND_PATH)  # bullet_card.wav 로드
        except pygame.error as e:
            print(f"Failed to load bullet card sound: {e}")
            self.sound = None

    def enhance(self):
        """총알 아이템을 사용하여 플레이어의 다음 공격을 강화하고 아이템 비활성화"""
        self.active = False
        if self.sound:
            self.sound.play()  # bullet_card.wav 재생

    def draw(self, window):
        """아이템 그리기"""
        if not self.active:
            return
        if self.active:
            window.blit(self.image, self.rect.topleft)

    def is_clicked(self, mouse_pos):
        """총알 아이템이 클릭되었는지 확인"""
        return self.active and self.rect.collidepoint(mouse_pos)

    def reactivate(self):
        """총알 아이템 상태 재설정"""
        self.active = True

class Game:
    def __init__(self):
        self.game_state = GameState.PLAYING
        # 테이블 이미지 로드
        try:
            self.table = pygame.image.load(TABLE_IMAGE_PATH).convert_alpha()
            self.table_image = pygame.transform.scale(
                self.table, (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
        except pygame.error as e:
            print(f"Failed to load table image: {e}")
            self.table = pygame.Surface((860, 320), pygame.SRCALPHA)  # 임의의 크기

        # 흐릿한 배경 이미지 로드
        try:
            self.blur_background = pygame.image.load(
                BLUR_BACKGROUND_IMAGE_PATH
            ).convert()
            self.blur_background = pygame.transform.scale(
                self.blur_background, (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
        except pygame.error as e:
            print(f"Failed to load blur background image: {e}")
            self.blur_background = pygame.Surface(
                (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
            )
            self.blur_background.fill(BLACK)  # 실패 시 검은색으로 채움

    def display_table(self, window):
        """게임 테이블 그리기"""
        if self.game_state == GameState.PLAYING:
            window.blit(self.table_image, (0, 0))

class Grenade:
    def __init__(self, position, size=(ITEM_WIDTH, ITEM_HEIGHT)):
        # 수류탄 이미지 로드
        try:
            self.image = pygame.image.load(GRENADE_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load grenade image: {e}")
            self.image = pygame.Surface(size, pygame.SRCALPHA)
            self.image.fill(RED)
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(topleft=position)
        self.active = False  # 수정: 초기값을 False로 변경
        self.used_this_turn = False  # 턴당 사용 여부 추적 변수 추가

        # 사운드 로드
        try:
            self.sound = pygame.mixer.Sound(GRENADE_SOUND_PATH)  # grenade.wav 로드
        except pygame.error as e:
            print(f"Failed to load grenade sound: {e}")
            self.sound = None

    def draw(self, window):
        """수류탄 그리기"""
        if not self.active:
            return
        if self.active:
            window.blit(self.image, self.rect.topleft)

    def is_clicked(self, pos):
        """수류탄 클릭 여부 확인"""
        return self.active and self.rect.collidepoint(pos)

    def use(self, player_lives):
        """수류탄 사용 처리"""
        self.active = False
        for i in range(len(player_lives)):
            player_lives[i] = max(0, player_lives[i] - 1)
        print("Grenade used: All players' HP decreased by 1.")
        if self.sound:  # 사운드 재생
            self.sound.play()

    def reactivate(self):
        """수류탄 아이템 재활성화"""
        self.active = random.choice([True, False])

class Card:
    def __init__(self):
        # 테이블 이미지 로드
        try:
            self.table_image = pygame.image.load(TABLE_IMAGE_PATH).convert_alpha()
            self.table_image = pygame.transform.scale(
                self.table_image, (WINDOW_WIDTH, WINDOW_HEIGHT)
            )
        except pygame.error as e:
            print(f"Failed to load table image: {e}")
            self.table_image = pygame.Surface(
                (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
            )

    def draw_table(self, window):
        """게임 테이블 그리기"""
        window.blit(self.table_image, (0, 0))

class Menu:
    def __init__(self):
        self.menu_state = MenuState.MAIN

    def is_hovered(self, rect):
        """마우스가 버튼 위에 있는지 확인"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return rect.collidepoint(mouse_x, mouse_y)

    def show_main_menu(self, window, play_text_rect, quit_text_rect):
        """메인 메뉴 표시"""
        # 메뉴 텍스트 그리기
        # 텍스트를 그릴 때, 텍스트의 get_rect() 함수를 써서 그리는 대신, rect 인자를 직접 사용

        # 텍스트 위치 계산 (수정)
        play_text_x = WINDOW_WIDTH // 15 - play_text_rect.width // 4  # 중앙 정렬
        quit_text_x = WINDOW_WIDTH // 15 - quit_text_rect.width // 4  # 중앙 정렬

        # "Play" 텍스트 렌더링 및 위치 조정
        if self.is_hovered(play_text_rect):
            window.blit(
                menu_font.render("Play", True, RED),
                (play_text_x, play_text_rect.y),  # 수정: x좌표를 play_text_x로 설정
            )
        else:
            window.blit(
                menu_font.render("Play", True, WHITE),
                (play_text_x, play_text_rect.y),  # 수정: x좌표를 play_text_x로 설정
            )

        # "Quit" 텍스트 렌더링 및 위치 조정
        if self.is_hovered(quit_text_rect):
            window.blit(
                menu_font.render("Quit", True, RED),
                (quit_text_x, quit_text_rect.y),  # 수정: x좌표를 quit_text_x로 설정
            )
        else:
            window.blit(
                menu_font.render("Quit", True, WHITE),
                (quit_text_x, quit_text_rect.y),  # 수정: x좌표를 quit_text_x로 설정
            )

class Scarecrow:
    def __init__(self, position, size=(ITEM_WIDTH, ITEM_HEIGHT)):
        self.position = position
        self.size = size
        # 허수아비 이미지 로드
        try:
            self.image = pygame.image.load(SCARECROW_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load Scarecrow image: {e}")
            self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft=self.position)
        self.active = False
        self.used_this_turn = False  # 턴당 사용 여부 추적 변수 추가

        # 사운드 로드
        try:
            self.sound = pygame.mixer.Sound(SCARECROW_CARD_SOUND_PATH)  # scarecrow_card.wav 로드
            self.scarecrow_sound = pygame.mixer.Sound(SCARECROW_SOUND_PATH)  # scarecrow.wav 로드
        except pygame.error as e:
            print(f"Failed to load scarecrow sound: {e}")
            self.sound = None
            self.scarecrow_sound = None

    def draw(self, screen):
        """화면에 아이템 그리기"""
        if self.active:
            screen.blit(self.image, self.rect)

    def click(self, mouse_pos):
        """아이템 클릭 여부 확인"""
        return self.active and self.rect.collidepoint(mouse_pos)

    def apply_effect(self):
        """허수아비 아이템 효과 적용 및 scarecrow_card.wav 재생"""
        self.active = False
        if self.sound:
            self.sound.play()  # scarecrow_card.wav 재생
        print("Scarecrow activated!")

    def reactivate(self, new_position=None):
        """아이템 재활성화 및 선택적으로 위치 변경"""
        if new_position:
            self.position = new_position
            self.rect.topleft = self.position
        self.active = random.choice([True, False])

# --- 함수 ---

def display_lives(window, lives):
    """두 플레이어의 생명력을 화면 중앙에 표시"""
    life_font = pygame.font.SysFont(FONT_NAME, 36)
    window_rect = window.get_rect()
    text_y = window_rect.centery - 215  # 수정: 텍스트 y 좌표 조정

    for i, life in enumerate(lives):
        text = f"Player {i+1} HP: {life}"
        text_surface = life_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(window_rect.centerx, text_y))
        window.blit(text_surface, text_rect)
        text_y += 35

# display_turn 함수 정의
def display_turn(window, current_player):
    """현재 플레이어 턴 표시"""
    turn_font = pygame.font.SysFont(FONT_NAME, 36)  # 폰트 크기 확대
    if current_player == 0:
        turn_text = turn_font.render("Player 1 Turn", True, RED)
        turn_text_rect = turn_text.get_rect(topleft=(50, 30))  # 왼쪽 위에 위치
    else:
        turn_text = turn_font.render("Player 2 Turn", True, RED)
        turn_text_rect = turn_text.get_rect(topright=(WINDOW_WIDTH - 50, 30))  # 오른쪽 위에 위치

    window.blit(turn_text, turn_text_rect)

def display_status_effects(window, bullet_enhanced, scarecrow_protected):
    """각 플레이어의 Bullet 및 Scarecrow 효과 활성화 상태를 텍스트로 표시"""
    font = pygame.font.SysFont(FONT_NAME, 25)

    # Player 1 상태 텍스트
    player1_bullet_text = "Bullet: " + ("ON" if bullet_enhanced[0] else "OFF")
    player1_scarecrow_text = "Scarecrow: " + ("ON" if scarecrow_protected[0] else "OFF")

    # Player 2 상태 텍스트
    player2_bullet_text = "Bullet: " + ("ON" if bullet_enhanced[1] else "OFF")
    player2_scarecrow_text = "Scarecrow: " + ("ON" if scarecrow_protected[1] else "OFF")

    # 텍스트 Surface 생성
    player1_bullet_surface = font.render(player1_bullet_text, True, WHITE)
    player1_scarecrow_surface = font.render(player1_scarecrow_text, True, WHITE)
    player2_bullet_surface = font.render(player2_bullet_text, True, WHITE)
    player2_scarecrow_surface = font.render(player2_scarecrow_text, True, WHITE)

    # 텍스트 위치 설정
    player1_bullet_rect = player1_bullet_surface.get_rect(
        bottomleft=(50, WINDOW_HEIGHT - 60)
    )
    player1_scarecrow_rect = player1_scarecrow_surface.get_rect(
        bottomleft=(50, WINDOW_HEIGHT - 35)
    )
    player2_bullet_rect = player2_bullet_surface.get_rect(
        bottomright=(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 60)
    )
    player2_scarecrow_rect = player2_scarecrow_surface.get_rect(
        bottomright=(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 35)
    )

    # 텍스트 그리기
    window.blit(player1_bullet_surface, player1_bullet_rect)
    window.blit(player1_scarecrow_surface, player1_scarecrow_rect)
    window.blit(player2_bullet_surface, player2_bullet_rect)
    window.blit(player2_scarecrow_surface, player2_scarecrow_rect)

def check_game_over(lives):
    """게임 종료 조건 확인, game_over.wav 또는 draw.wav 재생"""
    global game_state

    if lives[0] <= 0 and lives[1] <= 0:
        game_state = GameState.GAME_OVER
        if draw_sound:  # 무승부일 때 draw.wav 재생
            draw_sound.play()
        return True, -1  # 무승부
    elif lives[0] <= 0:
        game_state = GameState.GAME_OVER
        if game_over_sound:  # 다른 경우에는 game_over.wav 재생
            game_over_sound.play()
        return True, 1  # Player 2 승리
    elif lives[1] <= 0:
        game_state = GameState.GAME_OVER
        if game_over_sound:  # 다른 경우에는 game_over.wav 재생
            game_over_sound.play()
        return True, 0  # Player 1 승리
    else:
        return False, -1  # 게임 진행 중

def draw_game_over(window, winner_index):
    """게임 종료 화면을 그리고 Quit 버튼을 표시합니다. 마우스 오버 시 Quit 텍스트 색상 변경"""
    global quit_text

    # 흐릿한 배경 이미지 렌더링
    window.blit(game.blur_background, (0, 0))

    game_over_font = pygame.font.SysFont(FONT_NAME, 72)

    # 무승부 처리 (수정)
    if winner_index == -1:
        winner_text = "Draw!"
    else:
        winner_text = f"Player {winner_index + 1} Wins!"

    game_over_text = game_over_font.render(winner_text, True, WHITE)

    # "Quit" 텍스트를 위한 폰트 설정
    quit_font = pygame.font.Font(FONT_NAME, FONT_SIZE)
    if BOLD_FONT:
        quit_font.set_bold(True)

    # "Quit" 텍스트 렌더링
    quit_text = quit_font.render("Quit", True, WHITE)

    mouse_pos = pygame.mouse.get_pos()
    quit_text_rect = quit_text.get_rect(
        center=(window.get_width() // 2, window.get_height() // 2 + 50)
    )

    # "Quit" 텍스트의 마우스 오버 효과
    if quit_text_rect.collidepoint(mouse_pos):
        quit_text = quit_font.render("Quit", True, RED)

    # winner_text와 quit_text를 화면에 그림
    text_x = window.get_width() // 2
    text_y = window.get_height() // 2
    window.blit(
        game_over_text,
        (text_x - game_over_text.get_width() // 2, text_y - game_over_text.get_height() // 2),
    )
    window.blit(quit_text, quit_text_rect)

def draw_buttons(
    window,
    shoot_self_button_rect,
    shoot_opponent_button_rect,
    shoot_self_text,
    shoot_opponent_text,
    weapon
):
    """발사 버튼 그리기"""
    # 버튼 텍스트 중앙 정렬 및 크기 조정
    shoot_self_text_rect = shoot_self_text.get_rect(center=shoot_self_button_rect.center)
    shoot_opponent_text_rect = shoot_opponent_text.get_rect(
        center=shoot_opponent_button_rect.center
    )

    pygame.draw.rect(
        window,
        RED if menu.is_hovered(shoot_self_button_rect) else WHITE,
        shoot_self_button_rect,
        2,
    )
    pygame.draw.rect(
        window,
        RED if menu.is_hovered(shoot_opponent_button_rect) else WHITE,
        shoot_opponent_button_rect,
        2,
    )

    window.blit(
        shoot_self_text,
        shoot_self_text_rect,
    )
    window.blit(
        shoot_opponent_text,
        shoot_opponent_text_rect,
    )

def handle_bullet_click(mouse_pos, bullets, bullet_enhanced, current_player):
    """총알 아이템 클릭 처리 (card_delete.wav 재생)"""
    global item_used_this_turn
    for bullet in bullets:
        if bullet.is_clicked(mouse_pos) and not bullet.used_this_turn and not item_used_this_turn:
            # 아이템 발동/삭제 여부 결정 (기존 코드와 동일)
            bullet.enhance()
            bullet_enhanced[current_player] = True
            bullet.used_this_turn = True
            item_used_this_turn = True
            return True
    return False

def handle_scarecrow_click(
    mouse_pos, scarecrow1, scarecrow2, current_player, scarecrow_protected
):
    """허수아비 아이템 클릭 처리 (card_delete.wav, scarecrow_card.wav 재생)"""
    global item_used_this_turn
    if current_player == 0:
        if scarecrow1.active and scarecrow1.click(mouse_pos) and not scarecrow1.used_this_turn and not item_used_this_turn:
            if random.random() < 0.3:  # 30% 확률로 발동
                scarecrow1.apply_effect()  # scarecrow_card.wav 재생
                scarecrow_protected[0] = True
            else:
                print("Scarecrow effect did not activate!")  # 발동 실패 메시지
                scarecrow1.active = False  # 수정: 발동 실패 시 카드 비활성화
                if card_delete_sound:
                    card_delete_sound.play()
            scarecrow1.used_this_turn = True
            item_used_this_turn = True
            return True
    elif current_player == 1:
        if scarecrow2.active and scarecrow2.click(mouse_pos) and not scarecrow2.used_this_turn and not item_used_this_turn:
            if random.random() < 0.3:  # 30% 확률로 발동
                scarecrow2.apply_effect()  # scarecrow_card.wav 재생
                scarecrow_protected[1] = True
            else:
                print("Scarecrow effect did not activate!")  # 발동 실패 메시지
                scarecrow2.active = False  # 수정: 발동 실패 시 카드 비활성화
                if card_delete_sound:
                    card_delete_sound.play()
            scarecrow2.used_this_turn = True
            item_used_this_turn = True
            return True
    return False

def handle_grenade_click(mouse_pos, grenades, player_lives):
    """수류탄 아이템 클릭 처리 (card_delete.wav 재생)"""
    global item_used_this_turn
    global current_player
    global game_state
    global winner_index

    for grenade in grenades:
        if grenade.is_clicked(mouse_pos) and not grenade.used_this_turn and not item_used_this_turn:
            if random.random() < 0.5:  # 50% 확률로 발동
                grenade.use(player_lives)
                print("Grenade effect activated!")
            else:
                grenade.active = False  # 발동 실패 시 카드 비활성화
                if card_delete_sound:
                    card_delete_sound.play() # card_delete_sound 재생성
                print("Grenade effect did not activate!")

            grenade.used_this_turn = True
            item_used_this_turn = True

            # 즉시 턴 종료 후 게임 종료 여부 확인 (수정)
            current_player = (current_player + 1) % 2
            item_used_this_turn = False  # 수정: 턴 변경 후 item_used_this_turn 재설정

            for bullet in bullets:
                bullet.used_this_turn = False
            for g in grenades:
                g.used_this_turn = False
            syringe1.used_this_turn = False
            syringe2.used_this_turn = False
            scarecrow1.used_this_turn = False
            scarecrow2.used_this_turn = False

            game_over, winner_index = check_game_over(player_lives)
            if game_over:
                game_state = GameState.GAME_OVER

            return True
    return False

def handle_syringe_click(mouse_pos, syringe, player_lives, player_index):
    """주사기 클릭 처리 (card_delete.wav 재생)"""
    global item_used_this_turn
    if syringe.active and syringe.rect.collidepoint(mouse_pos) and not syringe.used_this_turn and not item_used_this_turn:
        if random.random() < 0.7:  # 70% 확률로 발동
            syringe.heal(player_lives, player_index)
            print("Syringe effect activated!")
        else:
            print("Syringe effect did not activate!")
            syringe.active = False  # 발동 실패 시 카드 비활성화
            if card_delete_sound:
                card_delete_sound.play()  # card_delete.wav 재생성
        syringe.used_this_turn = True
        item_used_this_turn = True
        return True


def handle_shoot_action(
        weapon,
        current_player,
        player_lives,
        bullet_enhanced,
        scarecrow_protected,
        target_self,
):
    """발사 액션 처리 및 총알 타입 반환"""
    global item_used_this_turn
    target_player = current_player if target_self else (current_player + 1) % 2
    bullet_type = weapon.shoot(bullet_enhanced, current_player, scarecrow_protected, target_player)

    if bullet_type is not None:
        damage = calculate_damage(bullet_enhanced, current_player)

        if bullet_type == 1:
            apply_damage(target_player, damage, scarecrow_protected, player_lives)

        # 총알 발사 후 턴 변경 (수정)
        if not (
                bullet_type == 0 and target_self
        ):  # "Shoot Self"를 클릭했고, 데미지를 입지 않은 경우 (공포탄) 가 아닐 때만 턴을 넘김
            current_player = (current_player + 1) % 2
        # 턴 변경 시에, item_used_this_turn을 False로 설정
        item_used_this_turn = False

        return True, bullet_type
    return False, None

def handle_shoot_buttons_click(
    mouse_pos,
    shoot_self_button_rect,
    shoot_opponent_button_rect,
    weapon,
    current_player,
    player_lives,
    bullet_enhanced,
    scarecrow_protected
):
    """발사 버튼 클릭 처리"""
    if shoot_self_button_rect.collidepoint(mouse_pos):
        return handle_shoot_action(
            weapon,
            current_player,
            player_lives,
            bullet_enhanced,
            scarecrow_protected,
            target_self=True
        )
    elif shoot_opponent_button_rect.collidepoint(mouse_pos):
        return handle_shoot_action(
            weapon,
            current_player,
            player_lives,
            bullet_enhanced,
            scarecrow_protected,
            target_self=False
        )

    return False, None

def calculate_damage(bullet_enhanced, current_player):
    """피해량 계산"""
    damage = 1
    if bullet_enhanced[current_player]:
        damage *= 2
        bullet_enhanced[current_player] = False
    return damage


def apply_damage(target_player, damage, scarecrow_protected, player_lives):
    """피해 적용 (허수아비 보호 상태 고려, scarecrow_sound 재생)"""
    global scarecrow1, scarecrow2

    if current_player == 0:
        scarecrow = scarecrow2
    else:
        scarecrow = scarecrow1

    if not scarecrow_protected[target_player]:
        player_lives[target_player] = max(0, player_lives[target_player] - damage)
    else:
        if scarecrow.scarecrow_sound:
            scarecrow.scarecrow_sound.play()  # scarecrow_sound 재생 위치 변경
        print(f"Player {target_player + 1} is protected by Scarecrow!")
        scarecrow_protected[target_player] = False

def handle_reload(weapon, syringe1, syringe2, scarecrow1, scarecrow2, bullets, grenades):
    """재장전 및 아이템 재활성화 처리 (card.wav 재생)"""
    global item_used_this_turn
    if not weapon.magazine:
        weapon.reload()

        # Scarecrow 카드 처리 (수정)
        if not scarecrow_protected[0]: # scarecrow1 (Player 1)이 보호 중이 아닐 때만 reactivate
            scarecrow1.reactivate(new_position=scarecrow1_position)
        if not scarecrow_protected[1]: # scarecrow2 (Player 2)가 보호 중이 아닐 때만 reactivate
            scarecrow2.reactivate(new_position=scarecrow2_position)

        # 나머지 아이템들은 이전과 동일하게 처리
        for bullet in bullets:
            bullet.reactivate()
            bullet.used_this_turn = False
        for grenade in grenades:
            grenade.reactivate()
            grenade.used_this_turn = False
        syringe1.reactivate()
        syringe2.reactivate()
        syringe1.used_this_turn = False
        syringe2.used_this_turn = False
        scarecrow1.used_this_turn = False
        scarecrow2.used_this_turn = False
        item_used_this_turn = False

        # 재장전 사운드 재생
        if card_sound:
            card_sound.play()

# --- 초기화 ---

# Pygame 초기화
pygame.init()

# 사운드 시스템 초기화
pygame.mixer.init()

# 창 생성
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# 배경 이미지 로드
try:
    background = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
except pygame.error as e:
    print(f"Failed to load background image: {e}")
    background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

# 메뉴 폰트 로드 (굵은 폰트 적용)
menu_font = pygame.font.Font(FONT_NAME, MENU_FONT_SIZE)
if BOLD_FONT:
    menu_font.set_bold(True)

# 일반 폰트 로드
font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

# 클래스 인스턴스 생성
game = Game()
menu = Menu()
player_lives = [INITIAL_LIVES, INITIAL_LIVES]
weapon = Weapon(player_lives)
card = Card()

# 사운드 로드
try:
    card_sound = pygame.mixer.Sound(CARD_SOUND_PATH)
    card_delete_sound = pygame.mixer.Sound(CARD_DELETE_SOUND_PATH)
    syringe_sound = pygame.mixer.Sound(SYRINGE_SOUND_PATH)
    grenade_sound = pygame.mixer.Sound(GRENADE_SOUND_PATH)
    scarecrow_card_sound = pygame.mixer.Sound(SCARECROW_CARD_SOUND_PATH)
    scarecrow_sound = pygame.mixer.Sound(SCARECROW_SOUND_PATH)
    game_over_sound = pygame.mixer.Sound(GAME_OVER_SOUND_PATH)
    draw_sound = pygame.mixer.Sound(DRAW_SOUND_PATH)
except pygame.error as e:
    print(f"Failed to load card sound: {e}")
    card_sound = None
    card_delete_sound = None
    syringe_sound = None
    grenade_sound = None
    scarecrow_card_sound = None
    scarecrow_sound = None
    game_over_sound = None
    draw_sound = None

# 아이템 카드 크기
ITEM_WIDTH = 165
ITEM_HEIGHT = 214

# 아이템 카드 위치 좌표
# Player 1
SCARECROW1_POS = (55, 125)  # Player1 - 오른쪽 위
BULLET1_POS = (225, 125)  # Player1 - 왼쪽 위
SYRINGE1_POS = (225, 350)  # Player1 - 왼쪽 아래
GRENADE1_POS = (55, 350)  # Player1 - 오른쪽 아래

# Player 2
SCARECROW2_POS = (1040, 125)  # Player2 - 왼쪽 위
BULLET2_POS = (870, 125) # Player2 - 오른쪽 위
SYRINGE2_POS = (870, 350)  # Player2 - 오른쪽 아래
GRENADE2_POS = (1040, 350)  # Player2 - 왼쪽 아래

# 버튼 위치 및 크기 설정: 중앙 하단에 배치
BUTTON_WIDTH = WINDOW_WIDTH * 0.15
BUTTON_HEIGHT = WINDOW_HEIGHT * 0.08
BUTTON_MARGIN = WINDOW_WIDTH * 0.015  # 버튼 간 간격
shoot_self_button_rect = pygame.Rect(
    WINDOW_WIDTH // 2 - BUTTON_WIDTH - BUTTON_MARGIN // 2,
    WINDOW_HEIGHT - BUTTON_HEIGHT - 110,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)
shoot_opponent_button_rect = pygame.Rect(
    WINDOW_WIDTH // 2 + BUTTON_MARGIN // 2,
    WINDOW_HEIGHT - BUTTON_HEIGHT - 110,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
)

# 1. Scarecrow 위치 설정
scarecrow_size = (ITEM_WIDTH, ITEM_HEIGHT)
scarecrow1_position = SCARECROW1_POS
scarecrow2_position = SCARECROW2_POS
scarecrow1 = Scarecrow(scarecrow1_position, size=scarecrow_size)
scarecrow2 = Scarecrow(scarecrow2_position, size=scarecrow_size)

# 2. Bullet 위치 설정
bullet_size = (ITEM_WIDTH, ITEM_HEIGHT)
bullet_positions = [
    BULLET1_POS,
    BULLET2_POS
]
bullets = [Bullet(pos, size=bullet_size) for pos in bullet_positions]

# 3. Syringe 위치 설정
syringe_size = (ITEM_WIDTH, ITEM_HEIGHT)
syringe1_position = SYRINGE1_POS
syringe2_position = SYRINGE2_POS
syringe1 = Syringe(syringe1_position)
syringe2 = Syringe(syringe2_position)

# 4. Grenade 위치 설정
grenade_size = (ITEM_WIDTH, ITEM_HEIGHT)
grenade1_position = GRENADE1_POS
grenade2_position = GRENADE2_POS
grenades = [
    Grenade(pos, size=grenade_size) for pos in [grenade1_position, grenade2_position]
]

# 버튼 텍스트 (크기 조정)
shoot_self_text = font.render("Shoot Self", True, WHITE)
shoot_opponent_text = font.render("Shoot Opponent", True, WHITE)

# 변수 초기화
current_player = 0
game_over = False
in_menu = True
game_state = GameState.PLAYING
bullet_enhanced = [False, False]
scarecrow_protected = [False, False]
item_used_this_turn = False

# --- 메인 루프 ---

run = True
while run:
    window.blit(background, (0, 0))

    if in_menu:
        # 메뉴 텍스트 위치 계산 (수정)
        # PLAY_TEXT_X = 0  # 이제 안쓰이는 변수
        PLAY_TEXT_Y = WINDOW_HEIGHT // 2 + 70  # 수정: 130을 더 뺌
        # QUIT_TEXT_X = 0  # 이제 안쓰이는 변수
        QUIT_TEXT_Y = PLAY_TEXT_Y + menu_font.get_height() + 20

        # 메뉴 버튼 텍스트 렌더링 (굵은 폰트 사용)
        play_text = menu_font.render("Play", True, WHITE)
        quit_text = menu_font.render("Quit", True, WHITE)

        # rect 객체를 이벤트 루프 바깥에서 생성하도록 수정 (수정)
        play_text_rect = play_text.get_rect()
        # play_text_rect.centerx = WINDOW_WIDTH // 2  # centerx 설정 제거
        play_text_rect.x = WINDOW_WIDTH // 15 - play_text_rect.width // 4  # x좌표 설정
        play_text_rect.y = PLAY_TEXT_Y
        quit_text_rect = quit_text.get_rect()
        # quit_text_rect.centerx = WINDOW_WIDTH // 2  # centerx 설정 제거
        quit_text_rect.x = WINDOW_WIDTH // 15 - quit_text_rect.width // 4  # x좌표 설정
        quit_text_rect.y = QUIT_TEXT_Y

        if menu.menu_state == MenuState.MAIN:
            menu.show_main_menu(window, play_text_rect, quit_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu.menu_state == MenuState.MAIN:
                    if play_text_rect.collidepoint(pygame.mouse.get_pos()):
                        in_menu = False
                        game.game_state = GameState.PLAYING
                        weapon.reload()
                        scarecrow1.reactivate(new_position=scarecrow1_position)
                        scarecrow2.reactivate(new_position=scarecrow2_position)
                        for bullet in bullets:
                            bullet.reactivate()
                        for grenade in grenades:
                            grenade.reactivate()
                        syringe1.active = True
                        syringe2.active = True
                    elif quit_text_rect.collidepoint(pygame.mouse.get_pos()):
                        run = False

    elif game.game_state == GameState.PLAYING:
        # 게임 화면
        card.draw_table(window)
        weapon.display_shotgun(window)
        weapon.display_magazine(window)
        display_lives(window, player_lives)
        display_turn(window, current_player)
        draw_buttons(
            window,
            shoot_self_button_rect,
            shoot_opponent_button_rect,
            shoot_self_text,
            shoot_opponent_text,
            weapon
        )

        scarecrow1.draw(window)
        scarecrow2.draw(window)
        syringe1.display_syringe(window)
        syringe2.display_syringe(window)

        for bullet in bullets:
            bullet.draw(window)

        for grenade in grenades:
            grenade.draw(window)

        # Bullet 및 Scarecrow 효과 상태 표시
        display_status_effects(window, bullet_enhanced, scarecrow_protected)

        for event in pygame.event.get():
            # 허수아비, 돌아가기 버튼 관련 변수는 이벤트 루프 밖에서 한 번만 정의
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:  # 수정: MOUSEBUTTONDOWN 이벤트를 elif에서 if로 변경
                mouse_pos = pygame.mouse.get_pos()

                # 아이템 클릭 여부 확인 (클릭 여부만 확인)
                bullet_clicked = handle_bullet_click(
                    mouse_pos, bullets, bullet_enhanced, current_player
                )

                scarecrow_clicked = handle_scarecrow_click(
                    mouse_pos,
                    scarecrow1,
                    scarecrow2,
                    current_player,
                    scarecrow_protected,
                )

                grenade_clicked = handle_grenade_click(
                    mouse_pos, grenades, player_lives
                )

                syringe_clicked = False
                if current_player == 0:
                    syringe_clicked = handle_syringe_click(mouse_pos, syringe1, player_lives, 0)
                elif current_player == 1:
                    syringe_clicked = handle_syringe_click(mouse_pos, syringe2, player_lives, 1)

                if not (bullet_clicked or scarecrow_clicked or grenade_clicked or syringe_clicked):
                    # 발사 버튼 클릭 및 총알 발사 여부 확인
                    shoot_clicked, bullet_type = handle_shoot_buttons_click(
                        mouse_pos,
                        shoot_self_button_rect,
                        shoot_opponent_button_rect,
                        weapon,
                        current_player,
                        player_lives,
                        bullet_enhanced,
                        scarecrow_protected,
                    )

                    if shoot_clicked:  # 발사 버튼이 클릭된 경우
                        # 총알 발사 후 즉시 화면 업데이트 (수정: 이부분 삭제)
                        # "Shoot Self"를 클릭했고, 데미지를 입지 않은 경우 (공포탄)
                        if bullet_type == 0 and (mouse_pos[0] >= shoot_self_button_rect.left and mouse_pos[
                            0] <= shoot_self_button_rect.right and mouse_pos[1] >= shoot_self_button_rect.top and
                                                 mouse_pos[1] <= shoot_self_button_rect.bottom):
                            pass
                        else:
                            current_player = (current_player + 1) % 2
                            # 플레이어 턴이 끝나는 시점에 item_used_this_turn을 False로 설정 (제거)
                            for bullet in bullets:
                                bullet.used_this_turn = False
                            for grenade in grenades:
                                grenade.used_this_turn = False
                            syringe1.used_this_turn = False
                            syringe2.used_this_turn = False
                            scarecrow1.used_this_turn = False
                            scarecrow2.used_this_turn = False
            # 수정 : KEYDOWN 이벤트를 MOUSEBUTTONDOWN와 독립적으로 처리
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if game.game_state == GameState.PLAYING:  # 이부분이 중첩 if문 안으로 이동
                        handle_reload(
                            weapon,
                            syringe1,
                            syringe2,
                            scarecrow1,
                            scarecrow2,
                            bullets,
                            grenades
                        )

        # 게임 종료 여부 확인 (이벤트 루프 밖으로 이동, 위치 수정)
        game_over, winner_index = check_game_over(player_lives)  # 반환값을 game_over, winner_index에 저장
        if game_over:  # game_over가 True이면
            game.game_state = GameState.GAME_OVER  # game.game_state를 GAME_OVER로 설정

        pygame.display.update()  # 이부분을 앞으로 이동

    elif game.game_state == GameState.GAME_OVER:
        # 게임 종료 상태
        draw_game_over(window, winner_index)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                quit_text_rect = quit_text.get_rect(center=(window.get_width() // 2, window.get_height() // 2 + 50))
                if quit_text_rect.collidepoint(mouse_pos):
                    run = False

    pygame.display.update()

pygame.quit()