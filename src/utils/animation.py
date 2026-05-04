

class Animation:

    # steps through a list of frames, calls update(dt) each frame, then call get_image() for the current frame.

    def __init__(self, frames, fps=8, loop=True):
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.timer = 0.0
        self.index = 0
        self.finished = False  # only meaningful when loop=False

    def get_image(self):
        return self.frames[self.index]

    def update(self, dt):
        if self.finished:
            return

        self.timer += dt
        if self.timer >= 1.0 / self.fps:
            self.timer = 0.0
            self.index += 1

            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1
                    self.finished = True

    def reset(self):
        self.timer = 0.0
        self.index = 0
        self.finished = False