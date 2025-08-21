import pygame
import random
import sys
from data.button import Button
from data.listframe import ListFrames
from PodSixNet.Connection import ConnectionListener, connection

pygame.init()
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

background_image = pygame.image.load('assets/2304x1296.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

json_layout_menu_nhanvat = {
    "1": [80, 62], "2": [88, 66], "3": [100, 46], "4": [100, 61], "5": [100, 53], "6": [80, 62],
    "7": [80, 65], "8": [80, 64], "9": [80, 66], "10": [100, 52], "11": [100, 54], "12": [100, 54],
    "13": [88, 68], "14": [88, 67], "15": [88, 68], "16": [88, 67], "17": [88, 68], "18": [88, 70],
    "19": [88, 68], "20": [88, 69],
}

def get_font(size):
    return pygame.font.Font("assets/04B_30__.TTF", size)

def draw_text_with_border(text, font, color, border_color, pos, border_width=4):
    text_surface = font.render(text, True, color)
    text_border = font.render(text, True, border_color)
    x, y = pos
    for dx in range(-border_width, border_width + 1):
        for dy in range(-border_width, border_width + 1):
            if dx != 0 or dy != 0:
                screen.blit(text_border, (x + dx, y + dy))
    screen.blit(text_surface, pos)

class Character(pygame.sprite.Sprite):
    def __init__(self, frames, x, y, id=0, speed=0, animation_cooldown=200):
        super().__init__()
        self.frames = frames
        self.image = frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.frame = 0
        self.id = id
        self.speed = speed
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = animation_cooldown

    def update(self, x=None, y=None, frame=None):
        if x is not None and y is not None and frame is not None:
            self.rect.x = x
            self.rect.y = y
            self.frame = frame % len(self.frames) if len(self.frames) > 0 else 0
            self.image = self.frames[self.frame]

class Game(ConnectionListener):
    def __init__(self):
        pygame.init()
        self.screen = screen
        self.background_image = background_image
        self.background_x = 0
        self.clock = pygame.time.Clock()
        self.state = "home"
        self.countdown = 30
        self.frame_counts = {1: 8, 2: 8, 3: 8, 4: 8, 5: 8, 6: 8}
        self.ranking = []
        self.connected = False
        self.characters = []

    def Network_init(self, data):
        self.frame_counts = data["frame_counts"]
        self.state = data["state"]
        self.countdown = data["countdown"]
        print(f"Initialized: state={self.state}, frame_counts={self.frame_counts}, countdown={self.countdown}")

    def Network_update(self, data):
        print(f"Received data: {data}")  # Debug
        self.state = data["state"]
        self.background_x = data["background_x"]
        if self.state == "waiting":
            self.countdown = data["countdown"]
        else:  # playing
            self.ranking = data.get("ranking", [])
            for char_data in data.get("characters", []):
                for character in self.characters:
                    if character.id == char_data["id"]:
                        frame = char_data["frame"] % self.frame_counts[character.id] if self.frame_counts[character.id] > 0 else 0
                        print(f"Updating horse {character.id}: x={char_data['x']}, y={char_data['y']}, frame={frame}")  # Debug
                        character.update(char_data["x"], char_data["y"], frame)

    def home_game(self):
        choices = random.sample(list(json_layout_menu_nhanvat.keys()), 4)
        positions = [(0, 500), (360, 560), (720, 500), (1100, 560)]
        characters = []
        for i in range(4):
            name = choices[i]
            frame_w, frame_h = json_layout_menu_nhanvat[name]
            frames = ListFrames(
                frame_width=frame_w,
                frame_height=frame_h,
                image=f"menu_game/{name}.png",
                scale=3,
                color=(255, 255, 0)
            ).run()
            x, y = positions[i]
            character = Character(frames, x, y, speed=1, animation_cooldown=200)
            characters.append(character)
        all_sprites = pygame.sprite.Group(characters)

        while self.state == "home":
            self.background_x -= 3
            if self.background_x <= -SCREEN_WIDTH:
                self.background_x = 0
            self.screen.blit(self.background_image, (self.background_x, 0))
            if self.background_x < 0:
                self.screen.blit(self.background_image, (self.background_x + SCREEN_WIDTH, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            draw_text_with_border(
                "HORSE RACING", get_font(100), "#d70000", "black", (SCREEN_WIDTH // 2 - 520, 60), 4
            )
            PLAY_BUTTON = Button(
                image=pygame.image.load("assets/Options Rect.png"), pos=(SCREEN_WIDTH // 2, 250),
                text_input="PLAY", font=get_font(65), base_color="#ff5f00", hovering_color="grey", border_color_text="BLACK",
                colour=(84, 84, 84)
            )
            OPTIONS_BUTTON = Button(
                image=pygame.image.load("assets/Options Rect.png"), pos=(SCREEN_WIDTH // 2, 370),
                text_input="OPTIONS", font=get_font(65), base_color="#005fff", hovering_color="grey", border_color_text="BLACK", colour=(84, 84, 84)
            )
            QUIT_BUTTON = Button(
                image=pygame.image.load("assets/Quit Rect.png"), pos=(SCREEN_WIDTH // 2, 480),
                text_input="QUIT", font=get_font(65), base_color="#ff005f", hovering_color="grey", border_color_text="BLACK", colour=(84, 84, 84)
            )
            for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        try:
                            self.Connect(("localhost", 31425))
                            self.connected = True
                            self.state = "waiting"
                        except Exception as e:
                            print(f"Connection failed: {e}")
                            self.state = "home"
                    if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.options()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pygame.quit()
                        sys.exit()
            all_sprites.update()
            all_sprites.draw(self.screen)
            pygame.display.update()
            if self.connected:
                connection.Pump()
                self.Pump()

    def options(self):
        while self.state == "options":
            self.screen.fill("white")
            OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
            OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
            self.screen.blit(OPTIONS_TEXT, OPTIONS_RECT)
            OPTIONS_BACK = Button(
                image=None, pos=(640, 460),
                text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green"
            )
            OPTIONS_BACK.changeColor(pygame.mouse.get_pos())
            OPTIONS_BACK.update(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if OPTIONS_BACK.checkForInput(pygame.mouse.get_pos()):
                        self.state = "home"
            pygame.display.update()
            if self.connected:
                connection.Pump()
                self.Pump()

    def menu_bet(self):
        frame_dat_cuoc = pygame.image.load('assets/khung_cuoc_1.png')
        frame_dat_cuoc = pygame.transform.scale(frame_dat_cuoc, (500, 250))
        frame_dat_cuoc.set_colorkey((84, 84, 84))
        khung_cuoc = pygame.image.load('assets/khung_cuoc_1.png')
        khung_cuoc = pygame.transform.scale(khung_cuoc, (350, 110))
        frames_nhanvat = [
            ListFrames(
                frame_width=80, frame_height=66, image=f"ngua_vay_duoi/{i}.png", scale=1.3, color=(255, 255, 0)
            ).run() for i in range(1, 7)
        ]
        characters = [
            Character(frames_nhanvat[i], 35, 45 + i * 120, id=i + 1, speed=0) for i in range(6)
        ]
        all_sprites = pygame.sprite.Group(characters)

        while self.state == "waiting":
            self.screen.blit(self.background_image, (self.background_x, 0))
            if self.background_x < 0:
                self.screen.blit(self.background_image, (self.background_x + SCREEN_WIDTH, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            ngua_1 = Button(
                image=khung_cuoc, pos=(200, 90),
                text_input="      KIM CUONG #1", font=get_font(19), base_color="BLACK", hovering_color="Green", colour=(84, 84, 84)
            )
            ngua_2 = Button(
                image=khung_cuoc, pos=(200, 210),
                text_input="      THIEN LONG #2", font=get_font(19), base_color="BLACK", hovering_color="Green", colour=(84, 84, 84)
            )
            ngua_3 = Button(
                image=khung_cuoc, pos=(200, 330),
                text_input="      CHAN SAT #3", font=get_font(19), base_color="BLACK", hovering_color="Green", colour=(84, 84, 84)
            )
            ngua_4 = Button(
                image=khung_cuoc, pos=(200, 450),
                text_input="      BACH MA #4", font=get_font(19), base_color="BLACK", hovering_color="Green", colour=(84, 84, 84)
            )
            ngua_5 = Button(
                image=khung_cuoc, pos=(200, 570),
                text_input="      BO MONG #5", font=get_font(19), base_color="BLACK", hovering_color="Green", colour=(84, 84, 84)
            )
            ngua_6 = Button(
                image=khung_cuoc, pos=(200, 690),
                text_input="      HAC BACH #6", font=get_font(19), base_color="BLACK", hovering_color="Green", colour=(84, 84, 84)
            )
            place_bet = Button(
                image=pygame.image.load("assets/Quit Rect.png"), pos=(1400 - 280, 350),
                text_input="PLACE BET", font=get_font(50), base_color="#ff005f", hovering_color="grey",
                border_color_text="BLACK", colour=(84, 84, 84), border_width=6
            )
            cancel = Button(
                image=pygame.image.load("assets/Quit Rect.png"), pos=(1400 - 280, 450),
                text_input="CANCEL", font=get_font(45), base_color="#ff8700", hovering_color="grey",
                border_color_text="BLACK", colour=(84, 84, 84)
            )
            for button in [ngua_1, ngua_2, ngua_3, ngua_4, ngua_5, ngua_6, cancel, place_bet]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)
            draw_text_with_border(
                str(self.countdown), get_font(80), "#d70000", "black", (SCREEN_WIDTH // 2 - 90, 60), 4
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if cancel.checkForInput(MENU_MOUSE_POS):
                        self.state = "home"
                        connection.Close()
                        self.connected = False
            self.screen.blit(frame_dat_cuoc, (SCREEN_WIDTH - frame_dat_cuoc.get_width() - 30, 30))
            all_sprites.update()
            all_sprites.draw(self.screen)
            pygame.display.update()
            if self.connected:
                connection.Pump()
                self.Pump()

    def play(self):
        frames_nhanvat = [
            ListFrames(
                frame_width=80, frame_height=62, image=f"png_ngua_dua/ngua_dua_{i}.png", scale=3, color=(255, 255, 0)
            ).run() for i in range(1, 7)
        ]
        self.characters = [
            Character(frames_nhanvat[i], 10, 440 + i * 30, id=i + 1, speed=0) for i in range(6)
        ]
        all_sprites = pygame.sprite.Group(self.characters)

        while self.state == "playing":
            self.screen.blit(self.background_image, (self.background_x, 0))
            if self.background_x < 0:
                self.screen.blit(self.background_image, (self.background_x + SCREEN_WIDTH, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.ranking:
                draw_text_with_border(
                    "RANKING:", get_font(40), "#d70000", "black", (SCREEN_WIDTH - 300, 50), 2
                )
                for idx, horse_id in enumerate(self.ranking, start=1):
                    draw_text_with_border(
                        f"Rank {idx}: Horse {horse_id}", get_font(30), "#d70000", "black", (SCREEN_WIDTH - 300, 100 + idx * 40), 2
                    )
            all_sprites.draw(self.screen)
            print(f"Drawing sprites: {[sprite.rect.x for sprite in self.characters]}")  # Debug
            pygame.display.update()
            if self.connected:
                connection.Pump()
                self.Pump()
            self.clock.tick(60)

    def run(self):
        while True:
            print(f"Current state: {self.state}")  # Debug
            if self.state == "home":
                self.home_game()
            elif self.state == "options":
                self.options()
            elif self.state == "waiting":
                self.menu_bet()
            elif self.state == "playing":
                self.play()

if __name__ == '__main__':
    game = Game()
    game.run()
pygame.quit()