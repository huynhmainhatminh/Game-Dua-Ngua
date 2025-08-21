import PodSixNet.Server
from PodSixNet.Channel import Channel
import pygame
import random
from time import sleep

# Frame counts for ngua_dua_*.png
HORSE_FRAME_COUNTS = {
    1: 8, 2: 8, 3: 8, 4: 8, 5: 8, 6: 8
}

class ClientChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

class Character:
    def __init__(self, x, y, speed=1, animation_cooldown=150, id=0):
        self.rect = pygame.Rect(x, y, 80, 62)
        self.frame = 0
        self.speed = speed
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = animation_cooldown
        self.id = id

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= HORSE_FRAME_COUNTS.get(self.id, 8):
                self.frame = 0
        self.rect.x += self.speed

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
        self.state = "waiting"
        self.countdown = 30
        self.last_tick = pygame.time.get_ticks()
        self.ranking = []

        # Initialize horses
        for i in range(1, 7):
            self.characters.append(Character(10, 440 + (i-1) * 30, speed=1, animation_cooldown=80, id=i))

        self.frame_counts = HORSE_FRAME_COUNTS

    def Connected(self, channel, addr):
        print(f"New client connected: {addr}")
        channel.Send({
            "action": "init",
            "frame_counts": self.frame_counts,
            "state": self.state,
            "countdown": self.countdown,
            "background_x": self.background_x
        })

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
            self.background_x -= 2
            if self.background_x <= -1400:
                self.background_x = 0
            state = {
                "action": "update",
                "state": self.state,
                "countdown": self.countdown,
                "background_x": self.background_x,
                "ranking": [character.id for character in self.ranking]
            }
        else:  # playing
            if current_time - self.last_speed_change >= self.speed_change_interval:
                self.last_speed_change = current_time
                for character in self.characters:
                    character.speed = random.randint(0, 2)
            for character in self.characters:
                character.update()
            for i, character in enumerate(self.characters, start=1):
                if character.rect.x >= 1400 and character not in self.ranking:
                    self.ranking.append(character)
                    print(f"Horse {i} finished in position {len(self.ranking)}!")
            self.background_x -= random.randint(7, 9)
            if self.background_x <= -1400:
                self.background_x = 0
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
            if len(self.ranking) == 6:
                print("\nFINAL RESULTS:")
                for idx, horse in enumerate(self.ranking, start=1):
                    print(f"Rank {idx}: Horse {horse.id}")
                self.state = "waiting"
                self.countdown = 30
                self.last_tick = current_time

        print(f"Sending state: {state}")
        for channel in self.channels:
            channel.Send(state)

print("Server starting...")
server = GameServer(localaddr=("localhost", 31425))
while True:
    server.Pump()
    server.update()
    sleep(0.0001)