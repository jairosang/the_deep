import pygame

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