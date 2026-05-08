from config import game as g_config
import pygame
import os

def load_frames(path, frame_width, frame_height, num_frames):

    # cuts the sprite sheet into individual frames, makes black (0, 0, 0) transparent using colorkey and returns a list of pygame.Surface frames.
    
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(num_frames):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
        frame.set_colorkey((0, 0, 0))
        frames.append(frame)
    return frames

def load_frames_from_folder(path, scale_to_screen: bool):
    frames = []
    frame_files = sorted(os.listdir(path))
    for frame in frame_files:
        if frame.startswith('.'):
            continue
        if not frame.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            continue

        full_path = os.path.join(path, frame)

        image = pygame.image.load(full_path).convert_alpha()

        if scale_to_screen:
            image = pygame.transform.smoothscale(image, g_config["SCREEN_SIZE"])

        frames.append(image)

    return frames