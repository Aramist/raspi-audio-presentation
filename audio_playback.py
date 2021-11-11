import sched
import time

import numpy as np
import pyaudio
import RPi.GPIO as io
from scipy.io import wavfile

import audio_config


# Generate Pyaudio instance
pa = pyaudio.PyAudio()
# Load in config
config = audio_config.config
n_stims = config['n_stims']
audio_fnames = config['audio_files']
_read_audio = [wavfile.read(fname) for fname in audio_fnames]
audio_fs = [a[0] for a in _read_audio]
audio_samples = [a[1] for a in _read_audio]
# audio_vols = config['audio_volumes']
audio_durations = config['audio_durations']
total_audio = sum(audio_durations)
delays = config['delays']
delays.insert(0, 0)  # Makes writing the loop easier
total_delay = sum(delays)
pulse_lens = config['pulse_durations']
warnings = config['warnings']

prepared_stream = None


io_pin = 17
scheduler = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)

# Setup gpio pin
io.setmode(io.BCM)
io.setup(io_pin, io.OUT)


def pulse_ms(length_ms):
    io.output(io_pin, io.HIGH)
    time.sleep(length_ms/1000)
    io.output(io_pin, io.LOW)


def prepare_stream(audio_index):
    fs = audio_fs[audio_index]
    global prepared_stream
    print(fs)
    dtype = audio_samples[audio_index].dtype
    if dtype == np.int16:
        prepared_stream = pa.open(format=pyaudio.paInt16, channels=1, rate=fs, output=True, output_device_index=0)
    elif dtype == np.int32:
        prepared_stream = pa.open(format=pyaudio.paInt32, channels=1, rate=fs, output=True, output_device_index=0)
    else:
        print('Bad audio format. Check bitrate and dtype')


def play_sound(audio_idx, chunk_size=1024):
    global prepared_stream
    if prepared_stream is None:
        return
    samples = audio_samples[audio_idx]
    fs = audio_fs[audio_idx]

    chunk_idx = np.arange(chunk_size, samples.shape[0], chunk_size)
    chunks = np.split(samples, chunk_idx)
    pulse_ms(pulse_lens[audio_idx])
    for chunk in chunks:
        if len(chunk) == 0:
            continue
        b = chunk.tobytes()
        prepared_stream.write(b, num_frames=len(chunk))
    prepared_stream.stop_stream()
    prepared_stream.close()
    prepared_stream = None


def print_stim_count(i):
    for _ in range(10):  # New on 2021-09-07: clear the screen before printing
        print()
    print('Stim {}/{}'.format(i + 1, n_stims))


def heads_up(count):
    print('{} seconds until the next stimulus'.format(count))


def print_est_time(est_time):
    hours = int(est_time // 3600)
    minutes = int(est_time // 60 - hours * 60)
    seconds = int(est_time % 60)
    if hours <= 0:
        print('Estimated time remaining: {:d}:{:0>2d}'.format(minutes, seconds))
    else:
        print('Estimated time remaining: {:d}:{:0>2d}:{:0>2d}'.format(hours, minutes, seconds))


print('Registering stim play times:')
first_stim_time = time.time() + 1  # Give 1 second just to make sure all of the events are registered before the first sound needs to play
# Really shouldn't need more than a few ms

for i in range(n_stims):
    # The amount of time between the onset of each AM sound * the stim number
    offset = (total_delay + total_audio) * i
    
    # The AM starts right on the offset
    # Use enterabs instead of enter to avond any drift from this loop's runtime
    # Shouldn't be much, but worth taking into account
    first = True

    for audio_idx, pre_delay in enumerate(delays[:-1]):
        if first:  # Print which stim is being played
            first = False
            scheduler.enterabs(
                first_stim_time + offset - 0.5,  # Prevent any interference between the print function and the play command
                1,  # priority 1 to ensure it prints before the audio ends
                print_stim_count,
                argument=(i,)
            )
            # Estimate the remaining time
            remaining_trials = n_stims - i
            est_time = total_audio * remaining_trials + total_delay * (remaining_trials - 1)
            scheduler.enterabs(
                first_stim_time + offset,
                2,
                print_est_time,
                argument=(est_time,)
            )

        # Register sounds
        scheduler.enterabs(
            first_stim_time + offset + sum(delays[:audio_idx + 1]) + sum(audio_durations[:audio_idx]) - 1,
            1,
            prepare_stream,
            argument=(audio_idx,)
        )

        scheduler.enterabs(
            first_stim_time + offset + sum(delays[:audio_idx + 1]) + sum(audio_durations[:audio_idx]),
            3,
            play_sound,
            argument=(audio_idx,)
        )
    
    if i == n_stims - 1:
        break  # No need to add heads up after the last stim has already played

    for countdown in warnings:
        scheduler.enterabs(
                first_stim_time + offset + total_delay + total_audio - countdown,
                2,
                heads_up,
                argument=(countdown,))
    # Everything is scheduled, now just let it run.
    # the call to run blocks the interpreter so there is no need to add a sleep here
print('Registration done, running scheduler')
scheduler.run(blocking=True)
pa.terminate()
io.cleanup()
