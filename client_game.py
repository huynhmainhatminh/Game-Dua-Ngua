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


music_button = pygame.mixer.Sound('music/brick.wav')

music_loop = pygame.mixer.Sound('music/game-music-loop-7-145285.wav')
music_loop.play(loops=9999)


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
    def __init__(self, frames, x, y, id=0, speed=0, animation_cooldown=80):
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
        self.target_x = x
        self.target_y = y
        self.target_frame = 0
        self.lerp_speed = 0.1  # Interpolation speed (0 to 1, higher = faster)

    def update(self, x=None, y=None, frame=None):
        current_time = pygame.time.get_ticks()
        # Update animation locally
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.frames):
                self.frame = 0
            self.image = self.frames[self.frame]

        # Update target positions if provided
        if x is not None and y is not None and frame is not None:
            self.target_x = x
            self.target_y = y
            self.target_frame = frame % len(self.frames) if len(self.frames) > 0 else 0

        # Interpolate towards target position
        self.rect.x += (self.target_x - self.rect.x) * self.lerp_speed
        self.rect.y += (self.target_y - self.rect.y) * self.lerp_speed

class CharacterMenu(pygame.sprite.Sprite):
    def __init__(self, frames, x, y, speed=6, animation_cooldown=200):
        super().__init__()
        self.frames = frames
        self.image = frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.frame = 0
        self.speed = speed
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = animation_cooldown

    def update_image(self):
        nhan_vat_choice = random.choice(list(json_layout_menu_nhanvat.keys()))
        nhan_vat = json_layout_menu_nhanvat[nhan_vat_choice]
        frames = ListFrames(frame_width=nhan_vat[0], frame_height=nhan_vat[1], image=f"menu_game/{nhan_vat_choice}.png", scale=3, color=(255, 255, 0)).run()
        self.frames = frames
        self.image = self.frames[0]

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.frames):
                self.frame = 0
            self.image = self.frames[self.frame]
        self.move_go_back()

    def reset_position_go_back(self):
        self.rect.x = SCREEN_WIDTH
        self.update_image()

    def move_go_back(self):
        self.rect.x -= self.speed
        if self.rect.x + self.rect.width < 0:
            self.reset_position_go_back()

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
        self.bet = None
        self.last_network_update = pygame.time.get_ticks()

    def Network_init(self, data):
        self.frame_counts = data["frame_counts"]
        self.state = data["state"]
        self.countdown = data["countdown"]
        self.background_x = data.get("background_x", 0)
        # print(f"Initialized: state={self.state}, frame_counts={self.frame_counts}, countdown={self.countdown},
        # background_x={self.background_x}")

    def Network_update(self, data):
        current_time = pygame.time.get_ticks()
        self.last_network_update = current_time
        # print(f"Received data: {data}")
        self.state = data["state"]
        self.background_x = data.get("background_x", self.background_x)
        if self.state == "waiting":
            self.countdown = data["countdown"]
            self.ranking = data.get("ranking", [])
            # print(f"Countdown updated: {self.countdown}")
        else:  # playing
            self.ranking = data.get("ranking", [])
            for char_data in data.get("characters", []):
                for character in self.characters:
                    if character.id == char_data["id"]:
                        frame = char_data["frame"] % self.frame_counts[character.id] if self.frame_counts[character.id] > 0 else 0
                        # print(f"Updating horse {character.id}: x={char_data['x']}, y={char_data['y']}, frame={frame}")
                        character.update(char_data["x"], char_data["y"], frame)
            if len(self.ranking) == 6:
                print(self.ranking)
                self.state = "results"

    def home_game(self):

        self.ranking.clear()

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
            character = CharacterMenu(frames, x, y, speed=1, animation_cooldown=200)
            characters.append(character)
        all_sprites = pygame.sprite.Group(characters)

        while self.state == "home":
            self.screen.fill((0, 0, 0))
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
                text_input="PLAY", font=get_font(65), base_color="#ff5f00", hovering_color="grey",
                border_color_text="BLACK", colour=(84, 84, 84)
            )
            OPTIONS_BUTTON = Button(
                image=pygame.image.load("assets/Options Rect.png"), pos=(SCREEN_WIDTH // 2, 370),
                text_input="OPTIONS", font=get_font(65), base_color="#005fff", hovering_color="grey",
                border_color_text="BLACK", colour=(84, 84, 84)
            )
            QUIT_BUTTON = Button(
                image=pygame.image.load("assets/Quit Rect.png"), pos=(SCREEN_WIDTH // 2, 480),
                text_input="QUIT", font=get_font(65), base_color="#ff005f", hovering_color="grey",
                border_color_text="BLACK", colour=(84, 84, 84)
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
                            music_button.play()
                            self.Connect(("localhost", 31425))
                            self.connected = True
                            self.state = "waiting"
                        except Exception as e:
                            print(f"Connection failed: {e}")
                            draw_text_with_border(
                                f"Connection failed: {e}", get_font(30), "#ff0000", "black", (SCREEN_WIDTH // 2 - 200, 600), 2
                            )
                            pygame.display.update()
                            pygame.time.wait(2000)
                            self.state = "home"
                    if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        self.state = "options"
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pygame.quit()
                        sys.exit()
            all_sprites.update()
            all_sprites.draw(self.screen)
            pygame.display.update()
            if self.connected:
                try:
                    connection.Pump()
                    self.Pump()
                except:
                    print("Connection lost in home")
                    self.connected = False
                    self.state = "home"
            self.clock.tick(60)

    def options(self):
        while self.state == "options":
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background_image, (self.background_x, 0))
            if self.background_x < 0:
                self.screen.blit(self.background_image, (self.background_x + SCREEN_WIDTH, 0))
            OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "#d70000")
            OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 260))
            self.screen.blit(OPTIONS_TEXT, OPTIONS_RECT)
            OPTIONS_BACK = Button(
                image=pygame.image.load("assets/Quit Rect.png"), pos=(SCREEN_WIDTH // 2, 460),
                text_input="BACK", font=get_font(75), base_color="#ff8700", hovering_color="grey",
                border_color_text="BLACK", colour=(84, 84, 84)
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
                try:
                    connection.Pump()
                    self.Pump()
                except:
                    print("Connection lost in options")
                    self.connected = False
                    self.state = "home"
            self.clock.tick(60)

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
            Character(frames_nhanvat[i], 35, 45 + i * 120, id=i + 1, speed=0, animation_cooldown=200) for i in range(6)
        ]
        all_sprites = pygame.sprite.Group(characters)

        while self.state == "waiting":
            self.screen.fill((0, 0, 0))
            self.background_x -= 3
            if self.background_x <= -SCREEN_WIDTH:
                self.background_x = 0
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
                str(self.countdown), get_font(80), "#d70000", "black", (SCREEN_WIDTH // 2 - 90, 100), 4
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if cancel.checkForInput(MENU_MOUSE_POS):
                        music_button.play()
                        self.menu_game_play()
                        # self.state = "waiting"
                        # connection.Close()
                        # self.connected = False
                    if ngua_1.checkForInput(MENU_MOUSE_POS):
                        self.bet = 1
                        print("Bet placed on Horse 1")
                    elif ngua_2.checkForInput(MENU_MOUSE_POS):
                        self.bet = 2
                        print("Bet placed on Horse 2")
                    elif ngua_3.checkForInput(MENU_MOUSE_POS):
                        self.bet = 3
                        print("Bet placed on Horse 3")
                    elif ngua_4.checkForInput(MENU_MOUSE_POS):
                        self.bet = 4
                        print("Bet placed on Horse 4")
                    elif ngua_5.checkForInput(MENU_MOUSE_POS):
                        self.bet = 5
                        print("Bet placed on Horse 5")
                    elif ngua_6.checkForInput(MENU_MOUSE_POS):
                        self.bet = 6
                        print("Bet placed on Horse 6")
                    if place_bet.checkForInput(MENU_MOUSE_POS):
                        if self.bet is not None:
                            print(f"Bet confirmed: Horse {self.bet}")
                            self.menu_game_play()
                        else:
                            draw_text_with_border(
                                "Please select a horse!", get_font(30), "#ff0000", "black", (SCREEN_WIDTH // 2 - 150, 600), 2
                            )
                            pygame.display.update()
                            pygame.time.wait(2000)
            self.screen.blit(frame_dat_cuoc, (SCREEN_WIDTH - frame_dat_cuoc.get_width() - 30, 30))
            all_sprites.update()
            all_sprites.draw(self.screen)
            pygame.display.update()
            if self.connected:
                try:
                    connection.Pump()
                    self.Pump()
                except:
                    print("Connection lost in menu_bet")
                    self.connected = False
                    self.state = "home"
            self.clock.tick(60)

    def menu_game_play(self):

        self.ranking.clear()

        khung_cuoc = pygame.image.load('assets/khung_ten.png')
        khung_cuoc = pygame.transform.scale(khung_cuoc, (200, 150))
        frames_nhanvat = [
            ListFrames(
                frame_width=80, frame_height=66, image=f"ngua_vay_duoi/{i}.png", scale=1.6, color=(255, 255, 0)
            ).run() for i in range(1, 7)
        ]
        characters = [
            Character(frames_nhanvat[i], 78 + i * 220, 350, id=i + 1, speed=0, animation_cooldown=200) for i in range(6)
        ]
        all_sprites = pygame.sprite.Group(characters)

        while self.state == "waiting":
            self.screen.fill((0, 0, 0))
            self.background_x -= 3
            if self.background_x <= -SCREEN_WIDTH:
                self.background_x = 0
            self.screen.blit(self.background_image, (self.background_x, 0))
            if self.background_x < 0:
                self.screen.blit(self.background_image, (self.background_x + SCREEN_WIDTH, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()
            ngua_1 = Button(
                image=khung_cuoc, pos=(140, 390),
                text_input="KIM CUONG", font=get_font(17), base_color="BLACK", hovering_color="BLACK",
                colour=(84, 84, 84), text_offset=(0, -51)
            )
            ngua_2 = Button(
                image=khung_cuoc, pos=(360, 390),
                text_input="THIEN LONG", font=get_font(17), base_color="BLACK", hovering_color="BLACK",
                colour=(84, 84, 84), text_offset=(0, -51)
            )
            ngua_3 = Button(
                image=khung_cuoc, pos=(580, 390),
                text_input="CHAN SAT", font=get_font(17), base_color="BLACK", hovering_color="BLACK",
                colour=(84, 84, 84), text_offset=(0, -51)
            )
            ngua_4 = Button(
                image=khung_cuoc, pos=(800, 390),
                text_input="BACH MA", font=get_font(17), base_color="BLACK", hovering_color="BLACK",
                colour=(84, 84, 84), text_offset=(0, -51)
            )
            ngua_5 = Button(
                image=khung_cuoc, pos=(1020, 390),
                text_input="BO MONG", font=get_font(17), base_color="BLACK", hovering_color="BLACK",
                colour=(84, 84, 84), text_offset=(0, -51)
            )
            ngua_6 = Button(
                image=khung_cuoc, pos=(1240, 390),
                text_input="HAC BACH", font=get_font(17), base_color="BLACK", hovering_color="BLACK",
                colour=(84, 84, 84), text_offset=(0, -51)
            )
            button_bet = Button(
                image=pygame.image.load("assets/Quit Rect.png"), pos=(SCREEN_WIDTH - 200, 670),
                text_input="BET", font=get_font(90), base_color="#ff005f", hovering_color="grey",
                border_color_text="BLACK", colour=(84, 84, 84), border_width=7
            )
            for button in [button_bet, ngua_1, ngua_2, ngua_3, ngua_4, ngua_5, ngua_6]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)
            draw_text_with_border(
                str(self.countdown), get_font(80), "#d70000", "black", (SCREEN_WIDTH // 2 - 90, 100), 4
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_bet.checkForInput(MENU_MOUSE_POS):
                        music_button.play()

                        self.menu_bet()
            all_sprites.update()
            all_sprites.draw(self.screen)
            pygame.display.update()
            if self.connected:
                try:
                    connection.Pump()
                    self.Pump()
                except:
                    print("Connection lost in menu_game_play")
                    self.connected = False
                    self.state = "home"
            self.clock.tick(60)

    def play(self):
        frames_nhanvat = [
            ListFrames(
                frame_width=80, frame_height=62, image=f"png_ngua_dua/ngua_dua_{i}.png", scale=3, color=(255, 255, 0)
            ).run() for i in range(1, 7)
        ]
        self.characters = [
            Character(frames_nhanvat[i], 10, 440 + i * 30, id=i + 1, speed=0, animation_cooldown=80) for i in range(6)
        ]
        all_sprites = pygame.sprite.Group(self.characters)

        while self.state == "playing":
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background_image, (self.background_x, 0))
            if self.background_x < 0:
                self.screen.blit(self.background_image, (self.background_x + SCREEN_WIDTH, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:

                    music_button.play()

                    pygame.quit()
                    sys.exit()
            if self.ranking:
                draw_text_with_border(
                    "RANKING:", get_font(40), "#d70000", "black", (SCREEN_WIDTH - 300, 50), 2
                )
                for idx, horse_id in enumerate(self.ranking, start=1):

                    if idx == 1:
                        draw_text_with_border(
                            f"Rank {idx}: Horse {horse_id}", get_font(30), "#ffff00", "black",
                            (SCREEN_WIDTH - 300, 100 + idx * 40), 2
                        )
                    elif idx == 2:
                        draw_text_with_border(
                            f"Rank {idx}: Horse {horse_id}", get_font(30), "#C0C0C0", "black",
                            (SCREEN_WIDTH - 300, 100 + idx * 40), 2
                        )
                    elif idx == 3:
                        draw_text_with_border(
                            f"Rank {idx}: Horse {horse_id}", get_font(30), "#CD7F32", "black",
                            (SCREEN_WIDTH - 300, 100 + idx * 40), 2
                        )
                    else:
                        draw_text_with_border(
                            f"Rank {idx}: Horse {horse_id}", get_font(30), "#d70000", "black", (SCREEN_WIDTH - 300, 100 + idx * 40), 2
                        )
            all_sprites.update()
            all_sprites.draw(self.screen)
            # print(f"Drawing sprites: {[sprite.rect.x for sprite in self.characters]}")
            # current_time = pygame.time.get_ticks()
            # if current_time - self.last_network_update > 1000:
            #     print("Warning: No network updates for 1 second")
            pygame.display.update()
            if self.connected:
                try:
                    connection.Pump()
                    self.Pump()
                except:
                    print("Connection lost in play")
                    self.connected = False
                    self.state = "home"
            self.clock.tick(60)

    def results(self):
        while self.state == "results":
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background_image, (self.background_x, 0))
            if self.background_x < 0:
                self.screen.blit(self.background_image, (self.background_x + SCREEN_WIDTH, 0))
            # draw_text_with_border(
            #     "FINAL RESULTS", get_font(60), "#d70000", "black", (SCREEN_WIDTH // 2 - 200, 50), 2
            # )
            for idx, horse_id in enumerate(self.ranking, start=1):
                if idx == 1:
                    draw_text_with_border(
                        f"Rank {idx}: Horse {horse_id}", get_font(40), "#ffff00", "black",
                        (SCREEN_WIDTH // 2 - 150, 150 + idx * 50), 2
                    )
                elif idx == 2:
                    draw_text_with_border(
                        f"Rank {idx}: Horse {horse_id}", get_font(40), "#C0C0C0", "black",
                        (SCREEN_WIDTH // 2 - 150, 150 + idx * 50), 2
                    )
                elif idx == 3:
                    draw_text_with_border(
                        f"Rank {idx}: Horse {horse_id}", get_font(40), "#CD7F32", "black",
                        (SCREEN_WIDTH // 2 - 150, 150 + idx * 50), 2
                    )
                else:
                    draw_text_with_border(
                        f"Rank {idx}: Horse {horse_id}", get_font(40), "#d70000", "black", (SCREEN_WIDTH // 2 - 150, 150 + idx * 50), 2
                    )
            if self.bet and self.ranking:
                result_text = "You Win!" if self.ranking[0] == self.bet else "You Lose!"
                draw_text_with_border(
                    result_text, get_font(50), "#00ff00" if self.ranking[0] == self.bet else "#ff0000", "black", (SCREEN_WIDTH // 2 - 100, 500), 2
                )


            BACK_BUTTON = Button(
                image=pygame.image.load("assets/Quit Rect.png"), pos=(SCREEN_WIDTH // 2, 600),
                text_input="BACK", font=get_font(45), base_color="#ff8700", hovering_color="grey",
                border_color_text="BLACK", colour=(84, 84, 84)
            )
            BACK_BUTTON.changeColor(pygame.mouse.get_pos())
            BACK_BUTTON.update(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:

                    music_button.play()

                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(pygame.mouse.get_pos()):

                        music_button.play()

                        self.state = "playing"
                        # self.bet = None
                        # connection.Close()
                        # self.connected = False
            pygame.display.update()
            self.clock.tick(60)

    def run(self):
        while True:
            print(f"Current state: {self.state}")
            if self.state == "home":
                self.home_game()
            elif self.state == "waiting":
                self.menu_game_play()
            elif self.state == "playing":
                self.play()
            elif self.state == "results":
                self.results()
            elif self.state == "options":
                self.options()

if __name__ == '__main__':
    game = Game()
    game.run()
pygame.quit()
