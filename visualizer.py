import sdl2.ext.compat
from sdl2 import *
from sdl2.sdlttf import *

def drawRect(renderer, x0, y0, w, h, clr=(255, 255, 255, 255)):
    SDL_SetRenderDrawColor(renderer, clr[0], clr[1], clr[2], clr[3])
    rectangle = SDL_Rect(x0, y0, w, h)
    SDL_RenderFillRect(renderer, rectangle)

class NoteLight:
    def __init__(self, renderer, idx, x, y, w, h, color=(1, 1, 1)):
        self.active = False
        self.brightness = 0
        self.renderer = renderer
        self.idx = idx
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def render_self(self):
        if self.active:
            drawRect(self.renderer, self.x, self.y, self.w, self.h, (int(self.brightness * self.color[0]),
                                                                     int(self.brightness * self.color[1]),
                                                                     int(self.brightness * self.color[2]),
                                                                     self.brightness))
        else:
            drawRect(self.renderer, self.x, self.y, self.w, self.h, (0, 0, 0, 0))

class Visualizer:
    def __init__(self, renderer, x, y, width, height, notecount, tracknums, tracknames,
                 horizontal_spacing, vertical_spacing, lowest_note, font, colors=[]):
        self.renderer = renderer
        self.x = x # leftmost x
        self.y = y # topmost y
        self.width = width
        self.height = height
        self.notecount = notecount
        self.tracknums = tracknums
        self.tracknames = tracknames
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing
        self.lowest_note = lowest_note
        self.colors = colors
        self.font = font

        self.trackcount = len(tracknums)
        self.rect_x = int(self.width / (self.notecount + self.horizontal_spacing))
        self.rect_y = int(self.height / (self.trackcount + self.vertical_spacing))

        # y positions of tracks
        self.track_ys = {}
        for idx_t in range(self.trackcount):
            tracknum = self.tracknums[idx_t]
            self.track_ys[tracknum] = self.y + idx_t * (self.rect_y + self.vertical_spacing)

        # x positions of notes
        self.note_xs = {}
        for idx_n in range(self.notecount):
            notenum = self.lowest_note + idx_n
            self.note_xs[notenum] = self.x + idx_n * (self.rect_x + self.horizontal_spacing)

        self.notelights = self.generate_notelights()

    def generate_notelights(self):
        notelights = {}
        for idx_t in range(len(self.track_ys)):
            key_t = list(self.track_ys.keys())[idx_t]
            t = list(self.track_ys.values())[idx_t]
            if self.colors:
                t_clr = self.colors[idx_t]
            else:
                t_clr = [1, 1, 1]
            for idx_n in range(len(self.note_xs)):
                key_n = list(self.note_xs.keys())[idx_n]
                n = list(self.note_xs.values())[idx_n]
                idx_nl = str(key_t) + "v" + str(key_n)
                notelights[idx_nl] = NoteLight(self.renderer, idx_nl, n, t, self.rect_x, self.rect_y, t_clr)

        return notelights

    def note_on(self, note_num, velocity, track_num):
        if velocity == 0:
            self.note_off(note_num, track_num)
        else:
            idx_nl = str(track_num) + "v" + str(note_num)
            self.notelights[idx_nl].active = True
            self.notelights[idx_nl].brightness = int(velocity / 100 * 255)

    def note_off(self, note_num, track_num):
        idx_nl = str(track_num) + "v" + str(note_num)
        self.notelights[idx_nl].active = False
        self.notelights[idx_nl].brightness = 0

    def stop_track(self, track_num):
        for n in self.notelights.values():
            if n.idx.startswith(str(track_num) + "v"):
                n.active = False
                n.brightness = 0

    def stop_all(self):
        for n in self.notelights.values():
            n.active = False

    def render(self):
        for i in self.notelights.values():
            i.render_self()

        # render track labels
        idx_c = 0
        for tracknum in self.tracknums:
            label_str = "Track " + str(tracknum) + ": " + self.tracknames[idx_c]
            label = sdl2.ext.compat.byteify(label_str)

            label_y = self.track_ys[tracknum]
            label_x = 20
            rect_w = 240
            rect_h = self.rect_y
            rect = SDL_Rect(label_x, label_y, rect_w, rect_h)

            if self.colors:
                pycolor = self.colors[idx_c]
            else:
                pycolor = (1, 1, 1)

            label_fg = SDL_Color(int(pycolor[0] * 255), int(pycolor[1] * 255), int(pycolor[2] * 255), 255)
            label_bg = SDL_Color(40, 40, 40, 40)

            label_surf = TTF_RenderText(self.font, label, label_fg, label_bg)
            label_texture = SDL_CreateTextureFromSurface(self.renderer, label_surf)
            SDL_RenderCopy(self.renderer, label_texture, None, rect)

            idx_c += 1
