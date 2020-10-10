import random # for generating blocks
import pygame
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS

# ===== Game State =====

x_col_blocks = 7 # how many columns of blocks
y_row_blocks = 9 # how many row of blocks (last row is out of view due to generation; see comment below)

steps_per_block = 8 # how many steps each block is subdivided into (>= 1)
game_y_step = 0 # goes from 0 to steps_per_block - 1, then decreases back to 0 (i.e. decreases and wraps around)

generation_y_index = 0 # goes from 0 to y_row_blocks - 1, then decreases back to 0 (i.e. decreases and wraps around

block_array = [[0 for j in range(y_row_blocks)] for i in range(x_col_blocks)]

# update game state (game_y_step decrements and new row may be generated)
def UpdateGame():
    global game_y_step
    global generation_y_index
    # update y values
    game_y_step -= 1
    if game_y_step < 0: # next block reached
        game_y_step = steps_per_block - 1
        generation_y_index -= 1
        if generation_y_index < 0:
            generation_y_index = y_row_blocks - 1
        # generate new row
        for i in range(x_col_blocks):
            block_array[i][generation_y_index] = random.randint(0,1) # currently no checks for random generation

# ===== Player State =====

player_x_col = 3 # current x index in the block array
player_x_step = 0 # a number between 0 and steps_per_block - 1 (keep initialized to 0)

player_y_row_start = 5
player_y_row = player_y_row_start

# updates player state and returns reward/punishment from applying action
# looks into game state to determine reward/punishment
def ApplyAction(action):
    return 0

# ===== Render Game =====

# looks into game state and player state to determine how to render

block_size = 50 # how many pixels wide for the square blocks
line_thickness = 2 # how many pixels wide are the gridlines
block_offset = line_thickness + block_size # used for calculations later
step_offset = block_offset/steps_per_block # used for calculations later

free_block_color = (255,255,255) # white
solid_block_color = (125,125,125) # grey
line_color = (0,0,0) # black

x_canvas_pixels = block_offset*x_col_blocks # used for calculations later
y_canvas_pixels = block_offset*y_row_blocks # used for calculations later

# initialize pygame
pygame.init()
# last row is out of view due to generation (remove '- block_offset' to see why)
window = pygame.display.set_mode((x_canvas_pixels,y_canvas_pixels - block_offset))

# fills the entire canvas with line_color (squares then get drawn on top)
def DrawLines():
    pygame.draw.rect(window, line_color, (0, 0, x_canvas_pixels, y_canvas_pixels))

# draw a single row (used as a helper for DrawRows
def DrawRow(y_index, current_y):
    j = 0
    current_x = x_canvas_pixels/2 + line_thickness/2 - step_offset/2 - step_offset*player_x_step
    while (j < x_col_blocks):
        cur_block = block_array[(player_x_col + j) % x_col_blocks][y_index]
        square_color = free_block_color
        if cur_block == 1:
            square_color = solid_block_color

        # draw square
        pygame.draw.rect(window, square_color, (int(current_x), int(current_y), block_size, block_size))

        if (current_x + block_size) > x_canvas_pixels: # wrap around to left
            current_x -= x_canvas_pixels
            continue

        current_x += block_offset
        j += 1

# draw all rows
def DrawRows(y_lerp_offset):
    i = 0
    current_y = line_thickness/2 - step_offset*game_y_step + y_lerp_offset
    while (i < y_row_blocks):
        y_index = (generation_y_index + i) % y_row_blocks

        # draw row
        DrawRow(y_index, current_y)

        current_y += block_offset
        i += 1

# draw red circle w/ radius 3 pixels at where player is
def DrawPlayer():
    pygame.draw.circle(window, (255,0,0), (int(x_canvas_pixels/2), int(step_offset/2 + player_y_row_start*block_offset)), 3)

# draw the current game state
# 0 <= alpha < 1 is how close to next game state
def DrawGame(alpha):
    y_lerp_offset = alpha*step_offset
    DrawLines()
    DrawRows(y_lerp_offset)
    DrawPlayer()

# ===== Sensors =====

# looks into game state and player state to determine sensor state

sensor_state = 0

# ===== Game Loop =====

clock = pygame.time.Clock()
clock.tick()

state_delay = 50 # in ms
time_buffer = 0 # keep initialized to 0

running = True
while running:
    time_buffer += clock.tick()
    while time_buffer >= state_delay:
        state_copy = sensor_state # for updating Q-value later (store in an array for multiple players)

        # get action using epsilon-greedy, softmax, etc.
        action = 0

        reward = ApplyAction(action) # apply action and update player state

        # can repeat the above in a loop for multiple players

        UpdateGame() # done once per loop

        # make sure to update sensor_state

        # Q[state_copy,action] += ... use sensor_state and reward to update Q value

        # can repeat the above in a loop to update the Q-value for each player

        time_buffer -= state_delay

    DrawGame(time_buffer/state_delay)
    pygame.display.update()

    for event in GAME_EVENTS.get():
        if event.type == GAME_GLOBALS.QUIT:
            running = False

pygame.quit()
