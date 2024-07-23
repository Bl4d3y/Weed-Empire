import pygame
import sys
import os
import random
import time
import pickle
import getpass

pygame.init()

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FONT_NAME = 'Arial'
DAY_DURATION = 30 
SAVE_FILE = 'game_save.pkl'

def get_asset_path(filename):
    return os.path.join(os.path.dirname(__file__), 'Assets', filename)

SUN_IMG = pygame.transform.scale(pygame.image.load(get_asset_path('Sun.png')), (100, 100))
MOON_IMG = pygame.transform.scale(pygame.image.load(get_asset_path('Moon.png')), (100, 100))
BACKGROUND_IMG = pygame.transform.scale(pygame.image.load(get_asset_path('Background.jpg')), (WIDTH, HEIGHT))
PLANT_IMG = pygame.transform.scale(pygame.image.load(get_asset_path('plant.png')), (50, 50))
BUTTON_IMG = pygame.transform.scale(pygame.image.load(get_asset_path('Button.png')), (200, 50))
BUTTON_HOVER_IMG = pygame.transform.scale(pygame.image.load(get_asset_path('Check.png')), (200, 50))
HARVESTED_IMG = pygame.transform.scale(pygame.image.load(get_asset_path('Har.png')), (50, 50))
pygame.mixer.music.load(get_asset_path('Sfx/Background.mp3'))
PLANT_SOUND = pygame.mixer.Sound(get_asset_path('Sfx/Plant.mp3'))
HARVEST_SOUND = pygame.mixer.Sound(get_asset_path('Sfx/Harvesting.wav'))
UPGRADE_SOUND = pygame.mixer.Sound(get_asset_path('Sfx/Upgrade.wav'))

class WeedEmpireGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Weed Empire')
        self.clock = pygame.time.Clock()
        self.running = True
        self.money = 100
        self.weed_plants = []
        self.plant_cost = 10
        self.harvest_amount = 5
        self.sell_price = 20
        self.upgrade_cost = 200
        self.upgrade_level = 1
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.show_plant_popup = False
        self.show_harvest_popup = False
        self.popup_timer = 0
        self.day_time = True
        self.day_start_time = time.time()
        self.weather = "Sunny"
        self.achievements = []

        pygame.mixer.music.play(-1)

        self.load_game()

        self.username = getpass.getuser()
        self.is_developer = (self.username == "Lucas")
        self.show_dev_panel = False

    def save_game(self):
        game_state = {
            'money': self.money,
            'weed_plants': self.weed_plants,
            'plant_cost': self.plant_cost,
            'harvest_amount': self.harvest_amount,
            'sell_price': self.sell_price,
            'upgrade_cost': self.upgrade_cost,
            'upgrade_level': self.upgrade_level,
            'day_time': self.day_time,
            'day_start_time': self.day_start_time,
            'weather': self.weather,
            'achievements': self.achievements,
        }
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump(game_state, f)

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, 'rb') as f:
                    game_state = pickle.load(f)
                    self.money = game_state['money']
                    self.weed_plants = game_state['weed_plants']
                    self.plant_cost = game_state['plant_cost']
                    self.harvest_amount = game_state['harvest_amount']
                    self.sell_price = game_state['sell_price']
                    self.upgrade_cost = game_state['upgrade_cost']
                    self.upgrade_level = game_state['upgrade_level']
                    self.day_time = game_state['day_time']
                    self.day_start_time = game_state['day_start_time']
                    self.weather = game_state['weather']
                    self.achievements = game_state['achievements']
            except (EOFError, pickle.UnpicklingError):
                print("Error loading save file. Starting a new game.")
                self.money = 100
                self.weed_plants = []
                self.plant_cost = 10
                self.harvest_amount = 5
                self.sell_price = 20
                self.upgrade_cost = 200
                self.upgrade_level = 1
                self.day_time = True
                self.day_start_time = time.time()
                self.weather = "Sunny"
                self.achievements = []

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.SysFont(FONT_NAME, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, img, hover_img, x, y, text, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        button_rect = img.get_rect(topleft=(x, y))

        if button_rect.collidepoint(mouse):
            self.screen.blit(hover_img, (x, y))
            if click[0] == 1 and action is not None:
                action()
        else:
            self.screen.blit(img, (x, y))

        self.draw_text(text, 20, WHITE, x + img.get_width() // 2, y + img.get_height() // 4)

    def plant_weed(self):
        if self.money >= self.plant_cost:
            self.money -= self.plant_cost
            plant = {'growth': 0, 'x': random.randint(50, WIDTH - 100), 'y': random.randint(300, HEIGHT - 100)}
            self.weed_plants.append(plant)
            self.show_plant_popup = True
            self.popup_timer = pygame.time.get_ticks()
            PLANT_SOUND.play()

    def harvest_weed(self):
        harvested = 0
        for plant in self.weed_plants:
            if plant['growth'] >= 100:
                harvested += self.harvest_amount
                self.weed_plants.remove(plant)
        if harvested > 0:
            self.show_harvest_popup = True
            self.popup_timer = pygame.time.get_ticks()
            HARVEST_SOUND.play()
        return harvested

    def sell_weed(self):
        harvested = self.harvest_weed()
        if harvested > 0:
            earnings = harvested * self.sell_price
            self.money += earnings

    def upgrade_farm(self):
        if self.money >= self.upgrade_cost:
            self.money -= self.upgrade_cost
            self.upgrade_level += 1
            self.plant_cost -= 1
            self.harvest_amount += 2
            self.sell_price += 5
            self.upgrade_cost *= 2
            UPGRADE_SOUND.play()

    def draw_popups(self):
        current_time = pygame.time.get_ticks()
        if self.show_plant_popup:
            self.draw_text("Weed Planted!", 30, GREEN, WIDTH // 2, HEIGHT // 2)
            if current_time - self.popup_timer > 1000: 
                self.show_plant_popup = False
        if self.show_harvest_popup:
            self.draw_text("Weed Harvested!", 30, RED, WIDTH // 2, HEIGHT // 2)
            if current_time - self.popup_timer > 1000:  
                self.show_harvest_popup = False

    def draw_ui(self):
        self.draw_text(f"Money: ${self.money}", 24, BLACK, WIDTH // 2, 20)
        self.draw_text(f"Weed Plants: {len(self.weed_plants)}", 24, BLACK, WIDTH // 2, 60)
        self.draw_text(f"Plant Cost: ${self.plant_cost}", 24, BLACK, WIDTH // 2, 100)
        self.draw_text(f"Harvest Amount: {self.harvest_amount} grams per plant", 24, BLACK, WIDTH // 2, 140)
        self.draw_text(f"Sell Price: ${self.sell_price} per gram", 24, BLACK, WIDTH // 2, 180)
        self.draw_text(f"Upgrade Cost: ${self.upgrade_cost}", 24, BLACK, WIDTH // 2, 220)
        self.draw_text(f"Farm Upgrade Level: {self.upgrade_level}", 24, BLACK, WIDTH // 2, 260)
        self.draw_text(f"Weather: {self.weather}", 24, BLACK, WIDTH // 2, 300)
        self.draw_text(f"Time: {'Day' if self.day_time else 'Night'}", 24, BLACK, WIDTH // 2, 340)

        button_width = 200
        button_height = 50
        button_x_positions = [100, WIDTH // 2 - button_width // 2, WIDTH - button_width - 100]
        button_y_position = HEIGHT - button_height - 50

        self.draw_button(BUTTON_IMG, BUTTON_HOVER_IMG, button_x_positions[0], button_y_position, "Plant Weed", self.plant_weed)
        self.draw_button(BUTTON_IMG, BUTTON_HOVER_IMG, button_x_positions[1], button_y_position, "Harvest & Sell", self.sell_weed)
        self.draw_button(BUTTON_IMG, BUTTON_HOVER_IMG, button_x_positions[2], button_y_position, "Upgrade Farm", self.upgrade_farm)

        if self.is_developer:
            self.draw_button(BUTTON_IMG, BUTTON_HOVER_IMG, WIDTH - 200, 20, "Dev Panel", self.toggle_dev_panel)

        if self.show_dev_panel:
            self.draw_dev_panel()

    def toggle_dev_panel(self):
        self.show_dev_panel = not self.show_dev_panel

    def give_infinite_weed(self):
        self.weed_plants.extend([{'growth': 100, 'x': random.randint(50, WIDTH - 100), 'y': random.randint(300, HEIGHT - 100)} for _ in range(10)])

    def give_infinite_money(self):
        self.money += 1000000

    def draw_dev_panel(self):
        dev_panel_rect = pygame.Rect(WIDTH - 220, 60, 200, 150)
        pygame.draw.rect(self.screen, BLACK, dev_panel_rect)
        self.draw_text("Developer Panel", 20, WHITE, WIDTH - 120, 70)
        self.draw_button(BUTTON_IMG, BUTTON_HOVER_IMG, WIDTH - 220, 90, "Infinite Weed", self.give_infinite_weed)
        self.draw_button(BUTTON_IMG, BUTTON_HOVER_IMG, WIDTH - 220, 140, "Infinite Money", self.give_infinite_money)

    def update_weather(self):
        weather_conditions = ["Sunny", "Rainy", "Windy", "Cloudy"]
        self.weather = random.choice(weather_conditions)
        if self.weather == "Rainy":
            for plant in self.weed_plants:
                if plant['growth'] < 100:
                    plant['growth'] += 2  

    def update_day_night_cycle(self):
        current_time = time.time()
        if current_time - self.day_start_time >= DAY_DURATION:
            self.day_time = not self.day_time
            self.day_start_time = current_time
            self.update_weather()

    def draw_background(self):
        self.screen.blit(BACKGROUND_IMG, (0, 0))
        if self.day_time:
            self.screen.blit(SUN_IMG, (WIDTH - 120, 20))
        else:
            self.screen.blit(MOON_IMG, (WIDTH - 120, 20))

    def check_achievements(self):
        if len(self.weed_plants) >= 10 and "Plant Master" not in self.achievements:
            self.achievements.append("Plant Master")
            self.show_plant_popup = True
            self.popup_timer = pygame.time.get_ticks()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game()  
                    self.running = False

            self.update_day_night_cycle()
            self.draw_background()
            self.draw_ui()

            for plant in self.weed_plants:
                if plant['growth'] < 100:
                    plant['growth'] += 1  
                    self.screen.blit(PLANT_IMG, (plant['x'], plant['y']))
                else:
                    self.screen.blit(HARVESTED_IMG, (plant['x'], plant['y']))

            self.draw_popups()
            self.check_achievements()

            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = WeedEmpireGame()
    game.run()
