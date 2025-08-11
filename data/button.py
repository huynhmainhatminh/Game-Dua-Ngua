import pygame

class Button:
    def __init__(self, image, pos, text_input, font, base_color, hovering_color,
                 border_color_text=None,
                 border_color_img=None,
                 colour: tuple = None,
                 border_width=4,
                 text_offset=(0, 0)  # ✅ Cho phép chỉnh vị trí chữ
                 ):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.colour = colour
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.border_color_text = border_color_text
        self.border_color_img = border_color_img
        self.border_width = border_width
        self.text_offset = text_offset  # Lưu offset

        # Render văn bản ban đầu
        self.text = self.font.render(self.text_input, True, self.base_color)

        # Nếu không có ảnh, dùng chữ làm nút
        if self.image is None:
            self.image = self.text

        # Tô màu nền trong suốt nếu cần
        if self.colour:
            self.image.set_colorkey(self.colour)

        # Vị trí nút và chữ
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos + self.text_offset[0],
                                                    self.y_pos + self.text_offset[1]))

    def update(self, screen):
        # Vẽ ảnh nút
        if self.image is not None:
            screen.blit(self.image, self.rect)

        # Viền ảnh nếu có
        if self.border_color_img:
            pygame.draw.rect(screen, self.border_color_img, self.rect, self.border_width)

        # Viền chữ nếu có
        if self.border_color_text:
            self.draw_text_with_border(screen)

        # Vẽ chữ chính
        screen.blit(self.text, self.text_rect)

    def draw_text_with_border(self, screen):
        """Vẽ chữ với viền"""
        text_border = self.font.render(self.text_input, True, self.border_color_text)
        x, y = self.text_rect.topleft
        for dx in range(-self.border_width, self.border_width + 1):
            for dy in range(-self.border_width, self.border_width + 1):
                if dx != 0 or dy != 0:
                    screen.blit(text_border, (x + dx, y + dy))

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        if self.checkForInput(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

        # Cập nhật lại vị trí text_rect sau khi render lại chữ
        self.text_rect = self.text.get_rect(center=(self.x_pos + self.text_offset[0],
                                                    self.y_pos + self.text_offset[1]))
