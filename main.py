import pygame
import random
import sys
from data.button import Button
from data.listframe import ListFrames


pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

# Khởi tạo màn hình
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

background_image = pygame.image.load('assets/2304x1296.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

background_x = 0
background_y = 0

json_layout_menu_nhanvat = {
        "1": [80, 62],
        "2": [88, 66],
        "3": [100, 46],
        "4": [100, 61],
        "5": [100, 53],
        "6": [80, 62],
        "7": [80, 65],
        "8": [80, 64],
        "9": [80, 66],
        "10": [100, 52],
        "11": [100, 54],
        "12": [100, 54],
        "13": [88, 68],
        "14": [88, 67],
        "15": [88, 68],
        "16": [88, 67],
        "17": [88, 68],
        "18": [88, 70],
        "19": [88, 68],
        "20": [88, 69],
}


def get_font(size):
    return pygame.font.Font("assets/04B_30__.TTF", size)


def draw_text_with_border(text, font, color, border_color, pos, border_width=4):
    # Tạo text chính và text border
    text_surface = font.render(text, True, color)
    text_border = font.render(text, True, border_color)

    # Vẽ text border trước (với border_width)
    x, y = pos
    for dx in range(-border_width, border_width + 1):
        for dy in range(-border_width, border_width + 1):
            if dx != 0 or dy != 0:
                screen.blit(text_border, (x + dx, y + dy))

    screen.blit(text_surface, pos)


class Character(pygame.sprite.Sprite):
    def __init__(self, frames, x, y, reset_position: bool= None, go_back:bool = None, go_up:bool = None, speed=6,
                 animation_cooldown=200) -> None:
        super().__init__()  # Gọi phương thức khởi tạo của lớp cha (pygame.sprite.Sprite)
        self.frames = frames
        self.image = frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.frame = 0
        self.speed = speed
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = animation_cooldown
        self.reset_position = reset_position
        self.go_back = go_back
        self.go_up = go_up


    def update_image(self):
        # Chọn một hình ảnh mới từ json_layout_menu_nhanvat
        nhan_vat_choice = random.choice(list(json_layout_menu_nhanvat.keys()))  # Random một số để chọn hình ảnh
        nhan_vat = json_layout_menu_nhanvat[nhan_vat_choice]
        frames = ListFrames(frame_width=nhan_vat[0], frame_height=nhan_vat[1], image=f"menu_game/{nhan_vat_choice}.png", scale=3, color=(255, 255, 0)).run()
        self.frames = frames
        self.image = self.frames[0]  # Cập nhật hình ảnh nhân vật

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.frames):
                self.frame = 0
            self.image = self.frames[self.frame]

        if self.go_back:
            self.move_go_back()

        if self.go_up:
            self.move_go_up()


    def reset_position_go_back(self):
        self.rect.x = SCREEN_WIDTH
        self.update_image()

    def reset_position_go_up(self):
        self.rect.x = 0

    def move_go_back(self):
        # Di chuyển nhân vật đi lùi
        self.rect.x -= self.speed

        if self.reset_position:
            # Nếu nhân vật đi lùi hết màn hình, đặt lại vị trí về màn hình
            if self.rect.x + self.rect.width < 0:  # Nếu nhân vật ra ngoài màn hình
                self.reset_position_go_back()  # Đặt lại vị trí ngẫu nhiên cho nhân vật

    def move_go_up(self):
        # Di chuyển nhân vật đi lên
        self.rect.x += self.speed

        if self.reset_position:
            if self.rect.x + self.rect.width >= SCREEN_WIDTH:
                self.reset_position_go_up()



def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        screen.fill("white")

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(640, 260))
        screen.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(
            image=None, pos=(640, 460),
            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green"
            )

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    home_game()

        pygame.display.update()


def play():

    global background_x, background_y


    frames_nhanvat1 = ListFrames(
        frame_width=80, frame_height=62, image="png_ngua_dua/ngua_dua_1.png", scale=3, color=(255, 255, 0)
        ).run()
    frames_nhanvat2 = ListFrames(
        frame_width=80, frame_height=62, image="png_ngua_dua/ngua_dua_2.png", scale=3, color=(255, 255, 0)
        ).run()
    frames_nhanvat3 = ListFrames(
        frame_width=80, frame_height=62, image="png_ngua_dua/ngua_dua_3.png", scale=3, color=(255, 255, 0)
        ).run()
    frames_nhanvat4 = ListFrames(
        frame_width=80, frame_height=62, image="png_ngua_dua/ngua_dua_4.png", scale=3, color=(255, 255, 0)
        ).run()
    frames_nhanvat5 = ListFrames(
        frame_width=80, frame_height=62, image="png_ngua_dua/ngua_dua_5.png", scale=3, color=(255, 255, 0)
        ).run()
    frames_nhanvat6 = ListFrames(
        frame_width=80, frame_height=62, image="png_ngua_dua/ngua_dua_6.png", scale=3, color=(255, 255, 0)
        ).run()

    # Tạo các đối tượng nhân vật và thêm vào nhóm sprite
    character1 = Character(frames_nhanvat1, 10, 440, speed=1, animation_cooldown=80, go_up=True)
    character2 = Character(frames_nhanvat2, 10, 470, speed=1, animation_cooldown=80, go_up=True)
    character3 = Character(frames_nhanvat3, 10, 500, speed=1, animation_cooldown=80, go_up=True)
    character4 = Character(frames_nhanvat4, 10, 530, speed=1, animation_cooldown=80, go_up=True)
    character5 = Character(frames_nhanvat5, 10, 560, speed=1, animation_cooldown=80, go_up=True)
    character6 = Character(frames_nhanvat6, 10, 590, speed=1, animation_cooldown=80, go_up=True)

    # Tạo một nhóm chứa tất cả các sprite
    all_sprites = pygame.sprite.Group()
    all_sprites.add(character1, character2, character3, character4, character5, character6, character6)

    screen_width, screen_height = screen.get_size()

    # Khởi tạo clock
    clock = pygame.time.Clock()

    # Theo dõi thời gian thay đổi tốc độ
    last_speed_change = pygame.time.get_ticks()
    speed_change_interval = 1000  # Thay đổi tốc độ mỗi 1 giây

    run = True

    while run:
        # Di chuyển background
        background_x -= 9  # Di chuyển từ phải qua trái (hoặc có thể thay đổi tốc độ)
        if background_x <= -screen_width:  # Khi background đã đi qua hết màn hình, reset lại vị trí
            background_x = 0

        screen.blit(background_image, (background_x, background_y))

        # Nếu muốn background trượt liên tục, vẽ lại từ phải sang trái
        if background_x < 0:
            screen.blit(background_image, (background_x + screen_width, background_y))

        # Thay đổi tốc độ ngẫu nhiên cho các con ngựa mỗi giây
        current_time = pygame.time.get_ticks()
        if current_time - last_speed_change >= speed_change_interval:
            last_speed_change = current_time
            # Cập nhật tốc độ ngẫu nhiên cho mỗi con ngựa
            character2.speed = random.randint(0, 2)
            character3.speed = random.randint(0, 2)
            character4.speed = random.randint(0, 2)
            character5.speed = random.randint(0, 2)
            character6.speed = random.randint(0, 2)
            character6.speed = random.randint(0, 2)

        # Cập nhật tất cả các sprite trong nhóm
        all_sprites.update()

        # Vẽ tất cả các sprite lên màn hình
        all_sprites.draw(screen)

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.flip()
        clock.tick(60)  # Điều chỉnh tốc độ FPS


def menu_game_play():

    global background_x, background_y

    countdown = 30  # Bắt đầu từ 30
    last_tick = pygame.time.get_ticks()  # Lấy thời gian ban đầu

    khung_cuoc = pygame.image.load('assets/khung_ten.png')
    khung_cuoc = pygame.transform.scale(khung_cuoc, (200, 150))

    frames_nhanvat1 = ListFrames(
        frame_width=80, frame_height=66, image="ngua_vay_duoi/1.png", scale=1.6, color=(255, 255, 0)
    ).run()

    frames_nhanvat2 = ListFrames(
        frame_width=80, frame_height=66, image="ngua_vay_duoi/2.png", scale=1.6, color=(255, 255, 0)
    ).run()

    #
    frames_nhanvat3 = ListFrames(
        frame_width=80, frame_height=66, image="ngua_vay_duoi/3.png", scale=1.6, color=(255, 255, 0)
    ).run()
    #
    frames_nhanvat4 = ListFrames(
        frame_width=80, frame_height=66, image="ngua_vay_duoi/4.png", scale=1.6, color=(255, 255, 0)
    ).run()
    #
    frames_nhanvat5 = ListFrames(
        frame_width=80, frame_height=66, image="ngua_vay_duoi/5.png", scale=1.6, color=(255, 255, 0)
    ).run()
    #
    frames_nhanvat6 = ListFrames(
        frame_width=80, frame_height=66, image="ngua_vay_duoi/6.png", scale=1.6, color=(255, 255, 0)
    ).run()

    character1 = Character(frames_nhanvat1, 78, 350, speed=0)
    character2 = Character(frames_nhanvat2, 310, 350, speed=0)
    character3 = Character(frames_nhanvat3, 530, 350, speed=0)
    character4 = Character(frames_nhanvat4, 750, 350, speed=0)
    character5 = Character(frames_nhanvat5, 970, 350, speed=0)
    character6 = Character(frames_nhanvat6, 1190, 350, speed=0)

    all_sprites = pygame.sprite.Group()
    all_sprites.add(character1, character2, character3, character4, character5, character6)


    while True:

        current_time = pygame.time.get_ticks()
        if current_time - last_tick >= 1000:  # Mỗi 1000ms (1 giây)
            countdown -= 1
            last_tick = current_time

        if countdown < 0:
            play()  # Hết thời gian thì vào chơi game


        background_x -= 1
        if background_x <= -SCREEN_WIDTH:
            background_x = 0

        screen.blit(background_image, (background_x, background_y))
        if background_x < 0:
            screen.blit(background_image, (background_x + SCREEN_WIDTH, background_y))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        ngua_1 = Button(
            image=khung_cuoc, pos=(140, 390),
            text_input="KIM CUONG", font=get_font(17), base_color="BLACK", hovering_color="BLACK", colour=(84, 84, 84),
            text_offset=(0, -51)
        )

        ngua_2 = Button(
            image=khung_cuoc, pos=(360, 390),
            text_input="THIEN LONG", font=get_font(17), base_color="BLACK", hovering_color="BLACK", colour=(84, 84, 84),
            text_offset=(0, -51)
        )

        ngua_3 = Button(
            image=khung_cuoc, pos=(580, 390),
            text_input="CHAN SAT", font=get_font(17), base_color="BLACK", hovering_color="BLACK", colour=(84, 84, 84),
            text_offset=(0, -51)
        )

        ngua_4 = Button(
            image=khung_cuoc, pos=(800, 390),
            text_input="BACH MA", font=get_font(17), base_color="BLACK", hovering_color="BLACK", colour=(84, 84, 84),
            text_offset=(0, -51)
        )

        ngua_5 = Button(
            image=khung_cuoc, pos=(1020, 390),
            text_input="BO MONG", font=get_font(17), base_color="BLACK", hovering_color="BLACK", colour=(84, 84, 84),
            text_offset=(0, -51)
        )

        ngua_6 = Button(
            image=khung_cuoc, pos=(1240, 390),
            text_input="HAC BACH", font=get_font(17), base_color="BLACK", hovering_color="BLACK", colour=(84, 84, 84),
            text_offset=(0, -51)
        )



        for button in [ngua_1, ngua_2, ngua_3, ngua_4, ngua_5, ngua_6]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        # Vẽ số đếm ngược
        MENU_TEXT = get_font(100).render(str(countdown), True, "#d70000")
        MENU_RECT = MENU_TEXT.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(MENU_TEXT, MENU_RECT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Cập nhật tất cả các sprite trong nhóm

        all_sprites.update()

        # Vẽ tất cả các sprite lên màn hình
        all_sprites.draw(screen)

        pygame.display.update()


def home_game():

    global background_x, background_y

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
        character = Character(frames, x, y, speed=1, go_back=True, reset_position=True)
        characters.append(character)

    # Nhóm sprite
    all_sprites = pygame.sprite.Group(characters)

    while True:
        # Di chuyển background mỗi lần lặp
        background_x -= 3  # Di chuyển từ phải qua trái (hoặc có thể thay đổi tốc độ)
        if background_x <= -SCREEN_WIDTH:  # Khi background đã đi qua hết màn hình, reset lại vị trí
            background_x = 0

        screen.blit(background_image, (background_x, background_y))

        # Nếu muốn background trượt liên tục, vẽ lại từ phải sang trái
        if background_x < 0:
            screen.blit(background_image, (background_x + SCREEN_WIDTH, background_y))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # Vẽ menu với hiệu ứng border cho chữ
        draw_text_with_border(
            "HORSE RACING", get_font(100), "#d70000", "black", (SCREEN_WIDTH // 2 - 520, 60), 4
        )

        # Các nút Play, Options, Quit
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
            button.update(screen)

        # Kiểm tra sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    menu_game_play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        # Cập nhật tất cả các sprite trong nhóm
        all_sprites.update()

        all_sprites.draw(screen)

        pygame.display.update()




def main():
    home_game()




if __name__ == '__main__':
    main()