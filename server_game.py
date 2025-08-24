import PodSixNet.Server
from PodSixNet.Channel import Channel
import pygame
import random
from time import sleep

# Frame counts from json_layout_menu_nhanvat (adjusted for ngua_dua_*.png)
HORSE_FRAME_COUNTS = {
    1: 8,  # Adjust based on actual sprite sheet for ngua_dua_1.png
    2: 8,
    3: 8,
    4: 8,
    5: 8,
    6: 8,
}


class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)


class GameServer(PodSixNet.Server.Server):
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        PodSixNet.Server.Server.__init__(self, *args, **kwargs)
        pygame.init()
        self.clock = pygame.time.Clock()
        self.characters = []
        self.last_speed_change = pygame.time.get_ticks()
        self.speed_change_interval = 1000
        self.background_x = 0
        self.state = "waiting"  # waiting or playing
        self.countdown = 30
        self.last_tick = pygame.time.get_ticks()
        self.ranking = []

        # Initialize horses
        self.characters.append(
            Character(None, 10, 440, speed=1, animation_cooldown=80, id=1, frame_count=HORSE_FRAME_COUNTS[1])
            )
        self.characters.append(
            Character(None, 10, 470, speed=1, animation_cooldown=80, id=2, frame_count=HORSE_FRAME_COUNTS[2])
            )
        self.characters.append(
            Character(None, 10, 500, speed=1, animation_cooldown=80, id=3, frame_count=HORSE_FRAME_COUNTS[3])
            )
        self.characters.append(
            Character(None, 10, 530, speed=1, animation_cooldown=80, id=4, frame_count=HORSE_FRAME_COUNTS[4])
            )
        self.characters.append(
            Character(None, 10, 560, speed=1, animation_cooldown=80, id=5, frame_count=HORSE_FRAME_COUNTS[5])
            )
        self.characters.append(
            Character(None, 10, 590, speed=1, animation_cooldown=80, id=6, frame_count=HORSE_FRAME_COUNTS[6])
            )

        self.frame_counts = HORSE_FRAME_COUNTS

    def Connected(self, channel, addr):
        print(f"New client connected: {addr}")
        channel.Send(
            {"action": "init", "frame_counts": self.frame_counts, "state": self.state, "countdown": self.countdown}
            )

    def update(self):
        self.clock.tick(60)
        current_time = pygame.time.get_ticks()

        if self.state == "waiting":
            if current_time - self.last_tick >= 1000:
                self.countdown -= 1
                self.last_tick = current_time
                if self.countdown <= 0:
                    self.state = "playing"
                    self.ranking = []
                    for character in self.characters:
                        character.rect.x = 10  # Reset positions
                    print("Game started!")

            # Send waiting state
            state = {
                "action": "update",
                "state": self.state,
                "countdown": self.countdown,
            }
        else:  # playing
            # Update horse speeds
            if current_time - self.last_speed_change >= self.speed_change_interval:
                self.last_speed_change = current_time
                for character in self.characters:
                    character.speed = random.randint(0, 2)

            # Update horse states
            for character in self.characters:
                character.update()

            # Check for finishers
            for i, character in enumerate(self.characters, start=1):
                if character.rect.x >= 1400 and character not in self.ranking:
                    self.ranking.append(character)
                    print(f"Horse {i} finished in position {len(self.ranking)}!")

            # Move background
            self.background_x -= random.randint(7, 9)
            if self.background_x <= -1400:
                self.background_x = 0

            # Send playing state
            state = {
                "action": "update",
                "state": self.state,
                "background_x": self.background_x,
                "characters": [
                    {
                        "id": character.id,
                        "x": character.rect.x,
                        "y": character.rect.y,
                        "frame": character.frame,
                        "speed": character.speed
                    } for character in self.characters
                ],
                "ranking": [character.id for character in self.ranking]
            }

            # End game when all horses finish
            if len(self.ranking) == 6:
                print("\nFINAL RESULTS:")
                for idx, horse in enumerate(self.ranking, start=1):
                    print(f"Rank {idx}: Horse {horse.id}")
                self.state = "waiting"
                self.countdown = 30
                self.last_tick = current_time
                self.ranking.clear()

        # Send state to all clients
        for channel in self.channels:
            channel.Send(state)


class Character:
    def __init__(self, frames, x, y, speed=6, animation_cooldown=200, id=0, frame_count=8):
        self.rect = pygame.Rect(x, y, 80, 62)
        self.frame = 0
        self.speed = speed
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = animation_cooldown
        self.id = id
        self.frame_count = frame_count

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= self.frame_count:
                self.frame = 0
        self.rect.x += self.speed


print("Server starting...")
server = GameServer(localaddr=("localhost", 31425))
while True:
    server.Pump()
    server.update()
    sleep(0.0001)
