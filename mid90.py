import mido
import sdl2.ext.compat
from sdl2 import *
from sdl2.sdlttf import *
import time
import ctypes
import sys

from reader import *
from visualizer import *

def visualize_midi(midi_file_path):
    try:
        note_data, min_note, max_note, tracklist, tracknamelist = parse_midi_file(midi_file_path)
    except FileNotFoundError:
        print("MIDI file " + midi_file_path + " not found.")
        start()

    notecount = max_note - min_note + 2
    bpm_changes, ticks_per_beat = get_bpm_changes(midi_file_path)
    events = note_data + bpm_changes

    # sort by time stamp
    events = sorted(events)

    # - - - INITIALIZE GRAPHICS - - -
    SDL_Init(SDL_INIT_VIDEO)
    window_title = sdl2.ext.compat.byteify("MIDIterranean 90 - " + midi_file_path)
    window = SDL_CreateWindow(window_title,
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              1280, 720, SDL_WINDOW_SHOWN)
    renderer = SDL_CreateRenderer(window, -1, 0)

    icon = sdl2.ext.load_img("mid90.png")
    SDL_SetWindowIcon(window, icon)

    TTF_Init()
    font_path = sdl2.ext.compat.byteify("data/fonts/DigitalDreamNarrow.ttf")
    default_font = TTF_OpenFont(font_path, 48)

    viscolors = [(0, 1, 0),
                 (0, 0.5, 1),
                 (1, 0, 0),
                 (1, 0, 1),
                 (1, 1, 0),
                 (0.5, 1, 0.5),
                 (0, 0, 1),
                 (1, 0.5, 0),
                 (1, 1, 0),
                 (1, 1, 1),
                 (0, 1, 0),
                 (0, 0.5, 1),
                 (1, 0, 0),
                 (1, 0, 1),
                 (0, 0, 1),
                 (0, 1, 0)]

    # - - - INITIALIZE VISUALIZER - - -
    # renderer, x, y, width, height, notecount, tracknums,
    # horizontal_spacing, vertical_spacing, lowest_note, colors
    vis = Visualizer(renderer, 280, 30, 840, 700, notecount, tracklist, tracknamelist,
                     2, 16, (min_note - 1), default_font, viscolors)

    # initialize variables
    playback_bpm = 0
    playback_tempo = 0
    dt = 0
    playback_time = 0
    running = True
    event = SDL_Event()
    while running:
        cycle_start = time.perf_counter()

        # request quit?
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break

        # print("\nTime:", playback_time)
        while len(events) and events[0][0] <= playback_time:
            # bpm change
            if events[0][1] == "bpm":
                playback_bpm = events[0][2]
                playback_tempo = events[0][3]

            # note on
            # time, "note_on", note_number, note_velocity, track
            elif events[0][1] == "note_on":
                try:
                    vis.note_on(events[0][2], events[0][3], events[0][4])
                except KeyError:
                    pass

            # note off
            # time, "note_off", note_number, note_velocity, track
            elif events[0][1] == "note_off":
                try:
                    vis.note_off(events[0][2], events[0][4])
                except KeyError:
                    pass

            del events[0]

        SDL_SetRenderDrawColor(renderer, 40, 40, 40, 40)
        SDL_RenderClear(renderer)
        vis.render()
        SDL_RenderPresent(renderer)

        playback_time += mido.second2tick(dt, ticks_per_beat, playback_tempo)
        dt = time.perf_counter() - cycle_start

    TTF_Quit()
    SDL_DestroyWindow(window)
    SDL_Quit()

def start(args=None):
    if args and len(args) > 1:
        midipath = args[1]
    else:
        midipath = input("Midi path:")

    visualize_midi(midipath)


start(sys.argv)
