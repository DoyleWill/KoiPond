import pygame
import pygame_gui
import random
import math
import threading
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from mock_controller import launch_controller

pygame.init()

WIDTH, HEIGHT = 225, 300
window_surface = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Koi Pond')

def load_sprite_sheet(path, frame_count):
  sheet = pygame.image.load(path).convert_alpha()
  sheet_width, sheet_height = sheet.get_size()
  frame_width = sheet_width // frame_count
  frames = []
  for i in range(frame_count):
    frame = sheet.subsurface((i * frame_width, 0, frame_width, sheet_height)).copy()
    frames.append(frame)
  return frames

FISH_COLORS = [
  "black_white_fish.png",
  "plain_orange_fish.png",
  "plain_white_fish.png",
  "white_orange_fish.png",
  "white_pink_fish.png"
]

def load_all_koi_sprites(base_dir, filenames, frame_count):
  sprites = {}
  for filename in filenames:
    path = os.path.join(base_dir, "..", "..", "assets", filename)
    sprites[filename] = load_sprite_sheet(path, frame_count)
  return sprites

koi_sprites = load_all_koi_sprites(BASE_DIR, FISH_COLORS, 8)

ui_manager = pygame_gui.UIManager((WIDTH,HEIGHT))

clock = pygame.time.Clock()
is_running = True

BG_COLOR = (2,7,7)

LILY_COLORS = [
    (34, 139, 34),
    (46, 139, 87),
    (60, 150, 60),
    (85, 160, 70),
    (40, 120, 55),
]

def generate_lily_pads(count,width,height):
  pads = []
  for _ in range(count):
    radius = random.randint(8,22)
    x = random.randint(radius, width - radius)
    y = random.randint(radius, height - radius)
    color = random.choice(LILY_COLORS)
    notch_angle = random.uniform(0,360)
    notch_width = random.uniform(25,50)
    pads.append({'origin_x': x, 
                 'origin_y': y, 
                 'x': x, 'y': y, 
                 'radius': radius, 
                 'color': color, 
                 'notch_angle': notch_angle, 
                 'notch_width': notch_width,
                 'drift_speed_x': random.uniform(0.01, 0.1),
                 'drift_speed_y': random.uniform(0.01, 0.1),
                 'phase_x': random.uniform(0, math.tau),
                 'phase_y': random.uniform(0, math.tau),
                 'drift_amount': random.uniform(2, 4),})
  return pads


def draw_lily_pad(surface, pad, bg_color):
  r = pad['radius']
  size = int(r * 3) + 4
  center = size // 2

  pad_surface = pygame.Surface((size, size), pygame.SRCALPHA)
  pygame.draw.circle(pad_surface, pad['color'], (center, center), r)

  angle = math.radians(pad['notch_angle'])
  half_width = math.radians(pad['notch_width'] / 2)
  p1 = (center, center)
  p2 = (center + r * 1.5 * math.cos(angle - half_width),
        center + r * 1.5 * math.sin(angle - half_width))
  p3 = (center + r * 1.5 * math.cos(angle + half_width),
        center + r * 1.5 * math.sin(angle + half_width))

  mask = pygame.Surface((size, size), pygame.SRCALPHA)
  pygame.draw.polygon(mask, (0, 0, 0, 255), [p1, p2, p3])
  pad_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

  surface.blit(pad_surface, (pad['x'] - center, pad['y'] - center))


def move_pads(pads, elapsed_time):
  for pad in pads:
    pad['x'] = pad['origin_x'] + math.sin(elapsed_time * pad['drift_speed_x'] + pad['phase_x']) * pad['drift_amount']
    pad['y'] = pad['origin_y'] + math.sin(elapsed_time * pad['drift_speed_y'] + pad['phase_y']) * pad['drift_amount']


def generate_food(count,width,height):
  food = []
  for _ in range(count):
    radius = random.randint(2,4)
    x = random.randint(radius, width - radius)
    y = random.randint(radius, height - radius)
    color = (207,204,54)
    food.append({'origin_x': x, 
                 'origin_y': y, 
                 'x': x, 'y': y, 
                 'radius': radius, 
                 'color': color, 
                 'drift_speed_x': random.uniform(0.15, 0.35),
                 'drift_speed_y': random.uniform(0.15, 0.35),
                 'phase_x': random.uniform(0, math.tau),
                 'phase_y': random.uniform(0, math.tau),
                 'drift_amount': random.uniform(2, 4),
                 'claimed': False,})
  return food


def draw_food(surface, food, bg_color):
  r = food['radius']
  size = int(r * 3) + 4
  center = size // 2

  food_surface = pygame.Surface((size, size), pygame.SRCALPHA)
  pygame.draw.circle(food_surface, food['color'], (center, center), r)

  mask = pygame.Surface((size, size), pygame.SRCALPHA)
  food_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

  surface.blit(food_surface, (food['x'] - center, food['y'] - center))


def move_food(food, elapsed_time):
  for crumb in food:
    crumb['x'] = crumb['origin_x'] + math.sin(elapsed_time * crumb['drift_speed_x'] + crumb['phase_x']) * crumb['drift_amount']
    crumb['y'] = crumb['origin_y'] + math.sin(elapsed_time * crumb['drift_speed_y'] + crumb['phase_y']) * crumb['drift_amount']


def generate_fish(count, width, height):
  fish = []
  for _ in range(count):
    radius = random.randint(5, 10)
    x = random.randint(radius, width - radius)
    y = random.randint(radius, height - radius)
    color = random.choice(FISH_COLORS)
    fish.append({
        'x': x, 'y': y,
        'radius': radius,
        'color': color,
        'angle': random.uniform(0, math.tau),
        'speed': random.uniform(5, 20),
        'target_angle': random.uniform(0, math.tau),
        'target_speed': random.uniform(5, 75),
        'turn_timer': random.uniform(1, 3),
        'target_food': None,
        'anim_frame': 0,
        'anim_distance': 0.0,
    })
  return fish


def draw_fishes(surface, fish, koi_sprites):
  frames = koi_sprites[fish['color']]
  frame = frames[fish['anim_frame']]
  angle_degrees = -math.degrees(fish['angle'])
  angle_degrees -= 90
  rotated = pygame.transform.rotate(frame, angle_degrees)
  rect = rotated.get_rect(center=(fish['x'], fish['y']))
  surface.blit(rotated, rect)


def move_fish(fishes, food, time_delta, width, height):
  for fish in fishes:
    if fish['target_food'] is None:
      unclaimed = [crumb for crumb in food if not crumb['claimed']]
      if unclaimed:
        chosen = random.choice(unclaimed)
        chosen['claimed'] = True
        fish['target_food'] = chosen

    if fish['target_food'] is not None:
      target = fish['target_food']
      still_there = any(crumb is target for crumb in food)

      if not still_there:
        fish['target_food'] = None
      else:
        dx_to_food = target['x'] - fish['x']
        dy_to_food = target['y'] - fish['y']
        distance_to_food = math.hypot(dx_to_food, dy_to_food)

        if distance_to_food < fish['radius'] + target['radius'] + 2:
          food.remove(target)
          fish['target_food'] = None
        else:
          fish['target_angle'] = math.atan2(dy_to_food, dx_to_food)
          if distance_to_food < 20:
            fish['target_speed'] = 15
          else:
            fish['target_speed'] = 60

    else:
      fish['turn_timer'] -= time_delta
      if fish['turn_timer'] <= 0:
        fish['target_angle'] = fish['angle'] + random.uniform(-math.pi / 2, math.pi / 2)
        fish['target_speed'] = random.uniform(5, 40)
        fish['turn_timer'] = random.uniform(1, 4)

    angle_diff = (fish['target_angle'] - fish['angle'] + math.pi) % math.tau - math.pi
    fish['angle'] += angle_diff * min(1, time_delta * 1.5)

    fish['speed'] += (fish['target_speed'] - fish['speed']) * min(1, time_delta * 1.0)

    dx = math.cos(fish['angle']) * fish['speed'] * time_delta
    dy = math.sin(fish['angle']) * fish['speed'] * time_delta
    fish['x'] += dx
    fish['y'] += dy

    distance_moved = math.hypot(dx, dy)
    fish['anim_distance'] += distance_moved
    distance_per_frame = 6
    if fish['anim_distance'] >= distance_per_frame:
      fish['anim_distance'] = 0
      fish['anim_frame'] = (fish['anim_frame'] + 1) % len(koi_sprites)

    margin = fish['radius']
    if fish['x'] < margin:
      fish['x'] = margin
      fish['target_angle'] = 0.0
    elif fish['x'] > width - margin:
      fish['x'] = width - margin
      fish['target_angle'] = math.pi
    if fish['y'] < margin:
      fish['y'] = margin
      fish['target_angle'] = math.pi / 2
    elif fish['y'] > height - margin:
      fish['y'] = height - margin
      fish['target_angle'] = -math.pi / 2


def generate_ripple(width, height):
  return {'x': random.randint(0,width),
          'y': random.randint(0,height),
          'radius': 1,
          'alpha': 150,}


def update_ripples(ripples, ripple_timer, time_delta, width, height):
  ripple_timer -= time_delta
  if ripple_timer <= 0:
    ripples.append(generate_ripple(width, height))
    ripple_timer = random.uniform(3, 5.0)

  for ripple in ripples[:]:
    ripple['radius'] += 15 * time_delta
    ripple['alpha'] -= 90 * time_delta
    if ripple['alpha'] <=0:
      ripples.remove(ripple)

  return ripple_timer


def draw_ripple(surface, ripple):
  size = int(ripple['radius'] *2) + 4
  ripple_surface = pygame.Surface((size,size), pygame.SRCALPHA)
  center = size // 2
  color = (255,255,255, max(0, int(ripple['alpha'])))
  pygame.draw.circle(ripple_surface, color, (center, center), int(ripple['radius']), width=1)
  surface.blit(ripple_surface, (ripple['x'] - center, ripple['y'] - center))


def button1_pressed():
  pygame.event.post(pygame.event.Event(pygame.QUIT))


def button2_pressed():
  food.extend(generate_food(1, WIDTH, HEIGHT))
  if len(food) > 10:
    food.pop(0)
  print("Dropping Food")


def button3_pressed():
  fishes.extend(generate_fish(1, WIDTH, HEIGHT))
  if len(fishes) > 15:
    fishes.pop(0)
  print("Added 1 Koi")


def button4_pressed():
  if len(fishes) >= 1:
    fishes.pop(0)
  print("Relocated 1 Koi")


controller_thread = threading.Thread(
  target=launch_controller,
  args=(button1_pressed,button2_pressed,button3_pressed,button4_pressed),
  daemon=True,
)
controller_thread.start()


lily_pads = generate_lily_pads(13, WIDTH, HEIGHT)
fishes = generate_fish(5, WIDTH, HEIGHT)
food = generate_food(0, WIDTH, HEIGHT)
ripples = []
ripple_timer = random.uniform(3, 5)
elapsed_time = 0

while is_running:
  time_delta = clock.tick(60) / 1000
  elapsed_time += time_delta

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      is_running = False
    ui_manager.process_events(event)

  ui_manager.update(time_delta)
  move_pads(lily_pads, elapsed_time)
  move_fish(fishes, food, time_delta, WIDTH, HEIGHT)
  move_food(food, elapsed_time)
  ripple_timer = update_ripples(ripples, ripple_timer, time_delta, WIDTH, HEIGHT)

  window_surface.fill(BG_COLOR)

  for fish in fishes:
    draw_fishes(window_surface, fish, koi_sprites)

  for ripple in ripples:
    draw_ripple(window_surface, ripple)

  for pad in lily_pads:
    draw_lily_pad(window_surface, pad, BG_COLOR)

  for crumb in food:
    draw_food(window_surface, crumb, BG_COLOR)

  ui_manager.draw_ui(window_surface)

  pygame.display.update()

pygame.quit()
  