import mido

def parse_midi_file(midi_file_path):
    """
    Parses a MIDI file and returns note data and track numbers.
    """
    note_data = []
    track_numbers = []

    # Load MIDI file
    mid = mido.MidiFile(midi_file_path)

    # Iterate through MIDI tracks
    min_note = 127
    max_note = 0
    tracklist = []
    tracknamelist = []
    for i, track in enumerate(mid.tracks):
        track_time = 0
        # Iterate through MIDI messages in track
        for msg in track:
            # Check if message is a note on or note off event
            # print(i, msg.time, msg.type)
            if msg.type == 'note_on' or msg.type == 'note_off':
                # this track has notes in it, add it to track list
                if i not in tracklist:
                    tracklist.append(i)
                    tracknamelist.append(track.name)

                # Extract note number, velocity, and time stamp
                note_number = msg.note
                velocity = msg.velocity
                time_stamp = track_time + msg.time

                if min_note > note_number:
                    min_note = note_number

                if max_note < note_number:
                    max_note = note_number

                # Add note data and track number to lists
                if msg.type == 'note_on':
                    note_data.append((time_stamp, "note_on", note_number, velocity, i))
                else:
                    note_data.append((time_stamp, "note_off", note_number, velocity, i))

            track_time += msg.time

    return note_data, min_note, max_note, tracklist, tracknamelist

def get_bpm_changes(midi_file_path):
    """
    Extracts BPM change messages from a MIDI file.
    """
    bpm_changes = []

    # Load MIDI file
    mid = mido.MidiFile(midi_file_path)

    # get ticks per beat
    ticks_per_beat = mid.ticks_per_beat

    # Iterate through MIDI tracks
    for track in mid.tracks:
        # Iterate through MIDI messages in track
        track_time = 0
        for msg in track:
            # Check if message is a tempo change event
            if msg.type == 'set_tempo':
                # Calculate BPM from tempo message and add to list
                tempo = msg.tempo
                bpm = mido.tempo2bpm(msg.tempo)
                bpm_changes.append((track_time + msg.time, "bpm", bpm, tempo))

            track_time += msg.time

    return bpm_changes, ticks_per_beat
