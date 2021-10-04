from scipy.io import wavfile


def get_duration(fname):
    sr, samples = wavfile.read(fname)
    return len(samples) / sr


config = {
    'n_stims': 40,
    'audio_files': [
        'white_sine_2s_ramped.wav',
        # 'low_freq_sequence.wav',
    ],
    'audio_volumes': [
        -30,
        # -40,
    ],
    'pulse_durations': [  # Length of the ttl pulse associated with each sound (ms)
        25,
        # 50,
    ],
    # Implemented below to avoid circular reference
    # 'audio_durations': [get_duration(fname) for fname in config['audio_files']],
    'delays': [  # size should be len(audio)
        62.5,
        # 20,
    ],
    # Amount of time between the end of one audio and the start of the next
    # The last element in this list is the amount of time between consecutive trials
    
    'warnings': [5],
}

config['audio_durations'] = [get_duration(fname) for fname in config['audio_files']]
