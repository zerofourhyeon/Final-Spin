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
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Buckshot Roulette"

# 폰트
FONT_NAME = "Times New Roman"
FONT_SIZE = 20

# 이미지 경로
IMAGE_DIR = "images"
BACKGROUND_IMAGE_PATH = os.path.join(IMAGE_DIR, "background.png")
BACKGROUND_BLUR_IMAGE_PATH = os.path.join(IMAGE_DIR, "background_flou.png")
SHOTGUN_IMAGE_PATH = os.path.join(IMAGE_DIR, "shotgun.png")
BLANK_IMAGE_PATH = os.path.join(IMAGE_DIR, "blanche.png")
LIVE_IMAGE_PATH = os.path.join(IMAGE_DIR, "rouge.png")
TABLE_IMAGE_PATH = os.path.join(IMAGE_DIR, "table.png")
BLACK_BACKGROUND_IMAGE_PATH = os.path.join(IMAGE_DIR, "fond_noir.png")
RETURN_IMAGE_PATH = os.path.join(IMAGE_DIR, "retour.png")
RULES_IMAGE_PATH = os.path.join(IMAGE_DIR, "regles.png")
CIGARETTE_IMAGE_PATH = os.path.join(IMAGE_DIR, "cigarette.png")
GRENADE_IMAGE_PATH = os.path.join(IMAGE_DIR, "grenade.png")

# 게임 설정
INITIAL_LIVES = 5
NB_SLOTS = 8

# --- 열거형 정의 ---

class MenuState(Enum):
    MAIN = 0
    RULES = 1

class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1

# --- 클래스 ---

class Weapon:
    def __init__(self, player_lives):
        # 샷건 이미지 로드
        try:
            self.shotgun = pygame.image.load(SHOTGUN_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load shotgun image: {e}")
            self.shotgun = pygame.Surface((170, 50), pygame.SRCALPHA)
        self.shotgun = pygame.transform.scale(self.shotgun, (170, 50))

        # 공포탄 이미지 로드
        try:
            self.blank = pygame.image.load(BLANK_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load blank bullet image: {e}")
            self.blank = pygame.Surface((69, 45), pygame.SRCALPHA)
        self.blank = pygame.transform.scale(self.blank, (69, 45))
        self.blank = pygame.transform.rotate(self.blank, 90)

        # 실탄 이미지 로드
        try:
            self.live = pygame.image.load(LIVE_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load live bullet image: {e}")
            self.live = pygame.Surface((69, 45), pygame.SRCALPHA)
        self.live = pygame.transform.scale(self.live, (69, 45))
        self.live = pygame.transform.rotate(self.live, 90)

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

    def shoot(self):
        """총알 발사"""
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
            self.blanks = [i for i in self.blanks if i < index] + [i - 1 for i in self.blanks if i > index]
            self.lives = [i for i in self.lives if i < index] + [i - 1 for i in self.lives if i > index]

            return bullet_type
        else:
            return None

    def display_bullet(self, window, pos_x, color):
        """총알 표시"""
        pygame.draw.rect(window, color, ((pos_x, 574), (8, 25)), 0)
        pygame.draw.rect(window, BLACK, ((pos_x, 574 - 8), (8, 8)), 0)

    def display_shotgun(self, window):
        """샷건 이미지 표시"""
        window.blit(self.shotgun, (455, 330))

    def display_magazine(self, window):
        """화면에 현재 탄창 상태 렌더링"""
        pos_x = 492
        for i in range(len(self.magazine)):
            if self.magazine[i] == 0:
                self.display_bullet(window, pos_x, WHITE)
            else:
                self.display_bullet(window, pos_x, RED)
            pos_x += 12

class Cigarette:
    def __init__(self, position):
        # 담배 이미지 로드
        try:
            self.image = pygame.image.load(CIGARETTE_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load cigarette image: {e}")
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)  # 임의의 크기로 설정, 필요에 따라 수정
        self.rect = self.image.get_rect(topleft=position)
        self.active = False

    def smoke(self, player_lives, player_index):
        """담배 피우기"""
        player_lives[player_index] += 1
        self.active = False

    def display_cigarette(self, window):
        """지정된 위치에 담배 표시"""
        if self.active:
            window.blit(self.image, self.rect.topleft)

    def reactivate(self):
        """50% 확률로 담배를 재활성화"""
        self.active = random.choice([True, False])

class Bullet:
    def __init__(self, position, size=(40, 40)):
        # 총알 이미지 로드
        try:
            self.image = pygame.image.load(LIVE_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load bullet image: {e}")
            self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(topleft=position)
        self.active = True

    def enhance(self):
        """총알 아이템을 사용하여 플레이어의 다음 공격을 강화하고 아이템 비활성화"""
        self.active = False

    def draw(self, window):
        """아이템 그리기"""
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
        except pygame.error as e:
            print(f"Failed to load table image: {e}")
            self.table = pygame.Surface((860, 320), pygame.SRCALPHA)  # 임의의 크기
        # 검은 배경 이미지 로드
        try:
            self.black_background = pygame.image.load(BLACK_BACKGROUND_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load black background image: {e}")
            self.black_background = pygame.Surface(
                (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
            )
        self.black_background = pygame.transform.scale(
            self.black_background, (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        self.roulette = Roulette((900, 50))  # 룰렛 위치 설정, 필요에 따라 수정
        self.item_slots = [
            ItemSlot((900, 150), RED),  # 빨간색 슬롯
            ItemSlot((950, 150), BLACK),  # 검은색 슬롯
        ]
        self.placed_item = None  # 현재 놓인 아이템
        self.spin_roulette = False  # 룰렛 회전 여부

    def display_table(self, window):
        """게임 테이블 그리기"""
        if self.game_state == GameState.PLAYING:
            window.blit(self.table, (-110, 50))

    def display_black_background(self, window):
        """검은색 배경 그리기"""
        if self.game_state == GameState.PLAYING:
            window.blit(self.black_background, (0, 0))

class Grenade:
    def __init__(self, position, size=(50, 50)):
        # 수류탄 이미지 로드
        try:
            self.image = pygame.image.load(GRENADE_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load grenade image: {e}")
            self.image = pygame.Surface(size, pygame.SRCALPHA)
            self.image.fill(RED)
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect(topleft=position)
        self.active = True

    def draw(self, window):
        """수류탄 그리기"""
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

    def reactivate(self):
        """수류탄 아이템 재활성화"""
        self.active = random.choice([True, False])

class Card:
    def __init__(self):
        self.slot_coords = [
            (30, 165),
            (150, 165),
            (30, 393),
            (150, 393),  # 왼쪽 슬롯
            (810, 165),
            (930, 165),
            (810, 393),
            (930, 393),  # 오른쪽 슬롯
        ]

    def draw_table(self, window):
        """게임 테이블 그리기"""
        pygame.draw.rect(window, (111, 63, 77), ((0, 145), (WINDOW_WIDTH, 420)), 0)
        pygame.draw.line(
            window, WHITE, (WINDOW_WIDTH // 2, 145), (WINDOW_WIDTH // 2, 563), 3
        )
        pygame.draw.circle(window, WHITE, (WINDOW_WIDTH // 2, 355), 210, 3)
        pygame.draw.rect(window, (192, 192, 192), ((487, 565), (106, 35)), 0)

    def draw_card_slots(self, window, width, height):
        """카드 슬롯 그리기"""
        for coord in self.slot_coords:
            pygame.draw.rect(
                window, WHITE, (coord[0], coord[1], width, height), 1
            )

class Menu:
    def __init__(self):
        self.menu_state = MenuState.MAIN
        # 흐린 배경 이미지 로드
        try:
            self.background_blur = pygame.image.load(
                BACKGROUND_BLUR_IMAGE_PATH
            ).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load blurred background image: {e}")
            self.background_blur = pygame.Surface(
                (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA
            )
        # 돌아가기 버튼 이미지 로드
        try:
            self.return_image = pygame.image.load(RETURN_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load return button image: {e}")
            self.return_image = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.return_image = pygame.transform.scale(self.return_image, (100, 100))

        # 규칙 이미지 로드
        try:
            self.rules_image = pygame.image.load(RULES_IMAGE_PATH).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load rules image: {e}")
            self.rules_image = pygame.Surface((780, 560), pygame.SRCALPHA)  # 임의의 크기

    def show_main_menu(self, window, play_text, rules_text, quit_text):
        """메인 메뉴 표시"""
        window.blit(play_text, (490, 475))
        window.blit(rules_text, (490, 510))
        window.blit(quit_text, (490, 545))

    def show_rules(self, window):
        """규칙 표시"""
        if self.menu_state == MenuState.RULES:
            window.blit(self.background_blur, (0, 0))
            window.blit(self.rules_image, (150, 80))
            window.blit(self.return_image, (0, 0))

    def is_hovered(self, x, y, width, height):
        """마우스가 버튼 위에 있는지 확인"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return x < mouse_x < x + width and y < mouse_y < y + height

class Scarecrow:
    def __init__(self, position, size=(80, 80)):
        self.position = position
        self.size = size
        # 허수아비 이미지 로드 (임시 이미지 사용)
        try:
            self.image = pygame.image.load(BLANK_IMAGE_PATH).convert_alpha()  # 임시 이미지
        except pygame.error as e:
            print(f"Failed to load Scarecrow image: {e}")
            self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(topleft=self.position)
        self.active = False

    def draw(self, screen):
        """화면에 아이템 그리기"""
        if self.active:
            screen.blit(self.image, self.rect)

    def click(self, mouse_pos):
        """아이템 클릭 여부 확인"""
        return self.active and self.rect.collidepoint(mouse_pos)

    def apply_effect(self):
        """허수아비 아이템 효과 적용"""
        self.active = False
        print("Scarecrow activated!")

    def reactivate(self, new_position=None):
        """아이템 재활성화 및 선택적으로 위치 변경"""
        if new_position:
            self.position = new_position
            self.rect.topleft = self.position
        self.active = random.choice([True, False])

class Roulette:
    def __init__(self, position):
        self.position = position
        self.wheel_colors = [RED, BLACK] * 5  # 룰렛 휠 색상 (빨강, 검정 번갈아 10개)
        random.shuffle(self.wheel_colors)  # 휠 색상 섞기
        self.wheel_radius = 50
        self.arrow_size = 10
        self.arrow_color = WHITE
        self.angle = 0
        self.spinning = False
        self.spin_speed = 0

    def draw(self, window):
        """룰렛 그리기"""
        # 휠 그리기
        for i, color in enumerate(self.wheel_colors):
            angle = math.radians(i * 36 + self.angle)  # 색상 각도 계산 (360도 / 10개 = 36도)
            x = self.position[0] + self.wheel_radius * math.cos(angle)
            y = self.position[1] + self.wheel_radius * math.sin(angle)
            pygame.draw.circle(window, color, (int(x), int(y)), 15)  # 색상 원 그리기

        # 화살표 그리기
        arrow_point = (
            self.position[0] + self.wheel_radius + self.arrow_size,
            self.position[1],
        )
        pygame.draw.polygon(
            window,
            self.arrow_color,
            [
                arrow_point,
                (arrow_point[0] - self.arrow_size, arrow_point[1] - self.arrow_size // 2),
                (arrow_point[0] - self.arrow_size, arrow_point[1] + self.arrow_size // 2),
            ],
        )

    def spin(self):
        """룰렛 회전 시작"""
        self.spinning = True
        self.spin_speed = random.randint(5, 15)  # 회전 속도 무작위 설정

    def update(self):
        """룰렛 회전 업데이트"""
        if self.spinning:
            self.angle = (self.angle + self.spin_speed) % 360
            self.spin_speed *= 0.95  # 회전 속도 점차 감소
            if self.spin_speed < 0.1:
                self.spinning = False
                self.spin_speed = 0

    def get_result(self):
        """룰렛 회전 결과 (빨간색 또는 검은색) 반환"""
        index = int((self.angle // 36) % 10)  # 화살표가 가리키는 색상 인덱스 계산
        return self.wheel_colors[index]

class ItemSlot:
    def __init__(self, position, color):
        self.position = position
        self.color = color
        self.rect = pygame.Rect(position[0], position[1], 50, 50)  # 슬롯 크기 설정
        self.item = None

    def draw(self, window):
        """슬롯 그리기"""
        pygame.draw.rect(window, self.color, self.rect, 2)  # 슬롯 테두리 그리기
        if self.item:
            # 슬롯에 아이템이 있으면 아이템 이미지 중앙에 그리기
            item_image = pygame.transform.scale(self.item.image, (40, 40))
            item_rect = item_image.get_rect(center=self.rect.center)
            window.blit(item_image, item_rect)

    def is_clicked(self, mouse_pos):
        """슬롯 클릭 여부 확인"""
        return self.rect.collidepoint(mouse_pos)

    def place_item(self, item):
        """슬롯에 아이템 배치"""
        self.item = item

    def remove_item(self):
        """슬롯에서 아이템 제거"""
        self.item = None

    def get_item(self):
        """슬롯에 있는 아이템 반환"""
        return self.item

# --- 함수 ---

def display_lives(window, lives):
    """두 플레이어의 생명력을 화면 중앙에 표시"""
    life_font = pygame.font.SysFont(FONT_NAME, 24)
    window_rect = window.get_rect()
    text_y = 50

    for i, life in enumerate(lives):
        text = f"Player {i+1} HP: {life}"
        text_surface = life_font.render(text, True, WHITE)
        window.blit(
            text_surface,
            ((window_rect.width - text_surface.get_width()) // 2, text_y),
        )
        text_y += 30

def display_turn(window, current_player):
    """현재 플레이어 턴 표시"""
    turn_text = font.render("Your Turn", True, RED)
    if current_player == 0:
        window.blit(turn_text, (20, 20))
    else:
        window.blit(
            turn_text, (window.get_width() - turn_text.get_width() - 20, 20)
        )

def check_game_over(lives):
    """게임 종료 조건 확인"""
    for i, life in enumerate(lives):
        if life <= 0:
            return True, i
    return False, -1

# 전역 변수로 quit_text 선언
quit_text = None

def draw_game_over(window, winner_index):
    """게임 종료 화면을 그리고 Quit 버튼을 표시합니다. 마우스 오버 시 Quit 텍스트 색상 변경"""
    global quit_text  # 전역 변수 quit_text 사용

    window.fill(BLACK)
    game_over_font = pygame.font.SysFont(FONT_NAME, 36)
    winner_text = f"Player {winner_index + 1} Wins!"
    game_over_text = game_over_font.render(winner_text, True, WHITE)

    mouse_pos = pygame.mouse.get_pos()
    quit_text_rect = quit_text.get_rect(center=(window.get_width() // 2, window.get_height() // 2 + 50))

    if quit_text_rect.collidepoint(mouse_pos):
        quit_text = font.render("Quit", True, RED)
    else:
        quit_text = font.render("Quit", True, WHITE)

    # winner_text와 quit_text를 화면에 그림
    text_x = window.get_width() // 2
    text_y = window.get_height() // 2
    window.blit(game_over_text, (text_x - game_over_text.get_width() // 2, text_y - game_over_text.get_height() // 2))
    window.blit(quit_text, quit_text_rect)

def draw_buttons(
    window,
    shoot_self_button_rect,
    shoot_opponent_button_rect,
    shoot_self_text,
    shoot_opponent_text,
):
    """발사 버튼 그리기"""
    pygame.draw.rect(
        window,
        RED if menu.is_hovered(*shoot_self_button_rect) else WHITE,
        shoot_self_button_rect,
        2,
    )
    pygame.draw.rect(
        window,
        RED if menu.is_hovered(*shoot_opponent_button_rect) else WHITE,
        shoot_opponent_button_rect,
        2,
    )
    window.blit(
        shoot_self_text,
        (shoot_self_button_rect.x + 10, shoot_self_button_rect.y + 10),
    )
    window.blit(
        shoot_opponent_text,
        (shoot_opponent_button_rect.x + 10, shoot_opponent_button_rect.y + 10),
    )

def handle_bullet_click(mouse_pos, bullets, bullet_enhanced, current_player):
    """총알 아이템 클릭 처리"""
    for bullet in bullets:
        if bullet.is_clicked(mouse_pos):
            bullet.enhance()
            bullet_enhanced[current_player] = True
            return True  # 클릭 여부 반환
    return False

def handle_scarecrow_click(
    mouse_pos, scarecrow1, scarecrow2, current_player, scarecrow_protected
):
    """허수아비 아이템 클릭 처리"""
    if scarecrow1.active and current_player == 0:
        if scarecrow1.click(mouse_pos):
            scarecrow1.apply_effect()
            scarecrow_protected[1] = True
            return True
    elif scarecrow2.active and current_player == 1:
        if scarecrow2.click(mouse_pos):
            scarecrow2.apply_effect()
            scarecrow_protected[0] = True
            return True
    return False

def handle_grenade_click(mouse_pos, grenades, player_lives):
    """수류탄 아이템 클릭 처리"""
    for grenade in grenades:
        if grenade.is_clicked(mouse_pos):
            grenade.use(player_lives)
            return True
    return False

def handle_cigarette_click(mouse_pos, cigarette, player_lives, player_index):
    """담배 아이템 클릭 처리"""
    if cigarette.active and cigarette.rect.collidepoint(mouse_pos):
        cigarette.smoke(player_lives, player_index)
        return True
    return False

def handle_shoot_action(
    weapon,
    current_player,
    player_lives,
    bullet_enhanced,
    scarecrow_protected,
    target_self,
):
    """발사 액션 처리 및 총알 타입 반환"""
    bullet_type = weapon.shoot()

    if bullet_type is not None:
        damage = calculate_damage(bullet_enhanced, current_player)
        target_player = current_player if target_self else (current_player + 1) % 2
        if bullet_type == 1:
            apply_damage(target_player, damage, scarecrow_protected, player_lives)

        # 총알 발사 후 턴 변경
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
    scarecrow_protected,
):
    """발사 버튼 클릭 처리"""
    if shoot_self_button_rect.collidepoint(mouse_pos):
        return handle_shoot_action(
            weapon,
            current_player,
            player_lives,
            bullet_enhanced,
            scarecrow_protected,
            target_self=True,
        )
    elif shoot_opponent_button_rect.collidepoint(mouse_pos):
        return handle_shoot_action(
            weapon,
            current_player,
            player_lives,
            bullet_enhanced,
            scarecrow_protected,
            target_self=False,
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
    """피해 적용 (허수아비 보호 상태 고려)"""
    if not scarecrow_protected[target_player]:
        player_lives[target_player] = max(0, player_lives[target_player] - damage)
    else:
        print(f"Player {target_player + 1} is protected by Scarecrow!")
        scarecrow_protected[target_player] = False

def handle_reload(weapon, cigarette1, cigarette2, scarecrow1, scarecrow2, bullets, grenades):
    """재장전 및 아이템 재활성화 처리"""
    weapon.reload()
    cigarette1.reactivate()
    cigarette2.reactivate()
    scarecrow1.reactivate(new_position=scarecrow1.position)
    scarecrow2.reactivate(new_position=scarecrow2.position)
    for bullet in bullets:
        bullet.reactivate()
    for grenade in grenades:
        grenade.reactivate()

def handle_item_placement(mouse_pos, item_slots, current_item, current_player):
    """아이템 배치 처리"""
    global placed_item
    for slot in item_slots:
        if slot.is_clicked(mouse_pos) and current_item:
            if placed_item[current_player] is not None:
                # 이미 놓인 아이템이 있으면 해당 아이템 비활성화
                placed_item[current_player].active = True

            slot.place_item(current_item)
            current_item.active = False  # 아이템 비활성화
            placed_item[current_player] = current_item  # 놓인 아이템 기록
            return True
    return False

def handle_roulette_spin(item_slots, roulette, current_player):
    """룰렛 회전 처리"""
    if placed_item[current_player] is not None:
        roulette.spin()
        return True
    return False

def activate_item(item_slot, roulette, player_lives, current_player, bullet_enhanced, scarecrow_protected):
    """룰렛 결과에 따른 아이템 발동 처리"""
    global placed_item
    if item_slot.item:
        result_color = roulette.get_result()
        if result_color == item_slot.color:
            print(f"Activating item: {type(item_slot.item).__name__}")
            if isinstance(item_slot.item, Cigarette):
                item_slot.item.smoke(player_lives, current_player)
            elif isinstance(item_slot.item, Bullet):
                item_slot.item.enhance()
                bullet_enhanced[current_player] = True
            elif isinstance(item_slot.item, Scarecrow):
                item_slot.item.apply_effect()
                scarecrow_protected[1 - current_player] = True
            elif isinstance(item_slot.item, Grenade):
                item_slot.item.use(player_lives)
        else:
            print(f"Item {type(item_slot.item).__name__} removed.")

        item_slot.remove_item()
        placed_item[current_player] = None

# --- 초기화 ---

# Pygame 초기화
pygame.init()

# 창 생성
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

# 배경 이미지 로드
try:
    background = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
except pygame.error as e:
    print(f"Failed to load background image: {e}")
    background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

# 폰트 로드
font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

# 메뉴 버튼 텍스트 렌더링
play_text = font.render("Play", True, WHITE)
rules_text = font.render("Rules", True, WHITE)
quit_text = font.render("Quit", True, WHITE)

# 클래스 인스턴스 생성
game = Game()
menu = Menu()
player_lives = [INITIAL_LIVES, INITIAL_LIVES]
weapon = Weapon(player_lives)
card = Card()

# 담배 위치 설정
cigarette1_position = (80, 200)
cigarette2_position = (920, 200)
cigarette1 = Cigarette(cigarette1_position)
cigarette2 = Cigarette(cigarette2_position)

# 허수아비 위치 설정
scarecrow1_position = (80, 400)
scarecrow2_position = (920, 400)
scarecrow1 = Scarecrow(scarecrow1_position)
scarecrow2 = Scarecrow(scarecrow2_position)

# 총알 위치 설정
bullet_size = (cigarette1.image.get_width(), cigarette1.image.get_height())
bullet_positions = [
    (cigarette1_position[0], cigarette1_position[1] + 100),
    (cigarette2_position[0], cigarette2_position[1] + 100),
]
bullets = [Bullet(pos, size=bullet_size) for pos in bullet_positions]

# 수류탄 위치 설정
grenade_offset_y = 80 + 10
grenade1_position = (scarecrow1_position[0], scarecrow1_position[1] + grenade_offset_y)
grenade2_position = (scarecrow2_position[0], scarecrow2_position[1] + grenade_offset_y)
grenades = [
    Grenade(pos, size=(50, 50)) for pos in [grenade1_position, grenade2_position]
]

# 버튼 위치 및 크기 설정
shoot_self_button_rect = pygame.Rect(420, 600, 120, 40)
shoot_opponent_button_rect = pygame.Rect(540, 600, 120, 40)
return_button_rect = menu.return_image.get_rect(topleft=(20, 620))

# 버튼 텍스트
shoot_self_text = font.render("Shoot Self", True, WHITE)
shoot_opponent_text = font.render("Shoot Opponent", True, WHITE)

# 변수 초기화
current_player = 0
game_over = False
in_menu = True
game_state = GameState.PLAYING
bullet_enhanced = [False, False]
scarecrow_protected = [False, False]
placed_item = [None, None]  # 각 플레이어가 놓은 아이템

# --- 메인 루프 ---

run = True
while run:
    window.blit(background, (0, 0))

    if in_menu:
        # 메뉴 화면 처리
        if menu.is_hovered(490, 475, play_text.get_width(), play_text.get_height()):
            play_text = font.render("Play", True, RED)
        else:
            play_text = font.render("Play", True, WHITE)
        if menu.is_hovered(490, 510, rules_text.get_width(), rules_text.get_height()):
            rules_text = font.render("Rules", True, RED)
        else:
            rules_text = font.render("Rules", True, WHITE)
        if menu.is_hovered(490, 545, quit_text.get_width(), quit_text.get_height()):
            quit_text = font.render("Quit", True, RED)
        else:
            quit_text = font.render("Quit", True, WHITE)

        if menu.menu_state == MenuState.MAIN:
            menu.show_main_menu(window, play_text, rules_text, quit_text)
        elif menu.menu_state == MenuState.RULES:
            menu.show_rules(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu.menu_state == MenuState.MAIN:
                    if pygame.Rect(
                        490, 475, play_text.get_width(), play_text.get_height()
                    ).collidepoint(pygame.mouse.get_pos()):
                        in_menu = False
                        game.game_state = GameState.PLAYING
                        weapon.reload()
                        cigarette1.active = True
                        cigarette2.active = True
                        scarecrow1.reactivate(new_position=scarecrow1_position)
                        scarecrow2.reactivate(new_position=scarecrow2_position)
                        for bullet in bullets:
                            bullet.reactivate()
                        for grenade in grenades:
                            grenade.reactivate()
                    elif pygame.Rect(
                        490, 510, rules_text.get_width(), rules_text.get_height()
                    ).collidepoint(pygame.mouse.get_pos()):
                        menu.menu_state = MenuState.RULES
                    elif pygame.Rect(
                        490, 545, quit_text.get_width(), quit_text.get_height()
                    ).collidepoint(pygame.mouse.get_pos()):
                        run = False
                elif menu.menu_state == MenuState.RULES:
                    if pygame.Rect(
                        0, 0, menu.return_image.get_width(), menu.return_image.get_height()
                    ).collidepoint(pygame.mouse.get_pos()):
                        menu.menu_state = MenuState.MAIN

    elif game.game_state == GameState.PLAYING:
        # 게임 화면
        game.display_black_background(window)
        card.draw_table(window)
        card.draw_card_slots(window, 120, 70)
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
        )

        window.blit(menu.return_image, return_button_rect.topleft)
        cigarette1.display_cigarette(window)
        cigarette2.display_cigarette(window)
        scarecrow1.draw(window)
        scarecrow2.draw(window)

        for bullet in bullets:
            bullet.draw(window)

        for grenade in grenades:
            grenade.draw(window)

        # 룰렛 및 아이템 슬롯 그리기
        game.roulette.draw(window)
        for slot in game.item_slots:
            slot.draw(window)

        # 룰렛 회전 애니메이션 업데이트
        game.roulette.update()

        # 현재 턴인 플레이어에 따라 사용 가능한 아이템 설정
        available_items = []
        if current_player == 0:
            available_items = [cigarette1, scarecrow1] + [b for b in bullets if b.rect.x < WINDOW_WIDTH // 2] + [g for g in grenades if g.rect.x < WINDOW_WIDTH // 2]
        else:
            available_items = [cigarette2, scarecrow2] + [b for b in bullets if b.rect.x > WINDOW_WIDTH // 2] + [g for g in grenades if g.rect.x > WINDOW_WIDTH // 2]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # 아이템 클릭 확인 및 슬롯에 배치
                for item in available_items:
                    if item.active and item.rect.collidepoint(mouse_pos):
                        current_item = item
                        item_placed = handle_item_placement(
                            mouse_pos, game.item_slots, current_item, current_player
                        )
                        break

                if return_button_rect.collidepoint(mouse_pos):
                    in_menu = True
                    game.game_state = GameState.PLAYING

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

                if shoot_clicked:
                    # 총알 발사 후 즉시 화면 업데이트
                    pygame.display.update()
                    game_over, loser = check_game_over(player_lives)
                    if game_over:
                        game.game_state = GameState.GAME_OVER
                        winner_index = 1 - loser

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game.roulette.spinning:
                        # 룰렛 회전 및 아이템 사용
                        spin_clicked = handle_roulette_spin(
                            game.item_slots, game.roulette, current_player
                        )
                        if spin_clicked:
                            # 룰렛 회전 후 결과 확인 및 아이템 발동
                            pygame.display.update()  # 룰렛 회전 애니메이션을 위해 업데이트
                            pygame.time.delay(1000)  # 룰렛 회전 시간 지연
                            game.roulette.update()
                            for slot in game.item_slots:
                                activate_item(
                                    slot,
                                    game.roulette,
                                    player_lives,
                                    current_player,
                                    bullet_enhanced,
                                    scarecrow_protected,
                                )
                            # 턴 변경
                            current_player = (current_player + 1) % 2
                elif event.key == pygame.K_r:
                    handle_reload(
                        weapon,
                        cigarette1,
                        cigarette2,
                        scarecrow1,
                        scarecrow2,
                        bullets,
                        grenades,
                    )

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