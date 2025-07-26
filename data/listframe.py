import pygame
from data.spritesheet import SpriteSheet


class ListFrames:
    def __init__(self, frame_width: int, frame_height: int, image: str, scale: int, color: tuple) -> None:
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale = scale
        self.image = image

        self.sprite_sheet_image = pygame.image.load(self.image).convert_alpha()
        self.sprite_sheet = SpriteSheet(self.sprite_sheet_image)
        self.list_frames = []
        self.color = color

        for i in range(self.sprite_sheet_image.get_width() // self.frame_width):
            frame = self.sprite_sheet.get_image(i, self.frame_width, self.frame_height, self.scale, self.color)
            self.list_frames.append(frame)

    def run(self) -> list:
        return self.list_frames