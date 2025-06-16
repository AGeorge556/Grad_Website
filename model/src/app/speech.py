import math
import io
import os
from os import mkdir, path, remove
from subprocess import PIPE, Popen
from time import time
import wave
from concurrent.futures import ThreadPoolExecutor
from json import loads
from multiprocessing import cpu_count
from vosk import KaldiRecognizer as Recognizer, Model, GpuInit  # , BatchModel
from pydub import AudioSegment
from soundfile import SoundFile


# Load VOSK models
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../files/models/en')
MODEL_PATH = os.path.abspath(MODEL_PATH)
model = Model(MODEL_PATH)

def extract_audio(_bytes, file_info):
    # already and audio file
    if 'audio/wav' in file_info.mime:
        try:
            wave_file = SoundFile(io.BytesIO(_bytes))

            sample_rate = wave_file.samplerate
            bit_depth = wave_file.subtype
            channels = wave_file.channels

            wave_file.close()

            if sample_rate == 16000 and bit_depth == 'PCM_16' and channels == 1:
                return _bytes
        except Exception as e:  # audio file not matching training wav specs, fallback to conversion
            print(f'File format mismatch :{e}\nConverting...')
	
    tmp_dir = 'files/tmp'
    if not path.isdir(tmp_dir):
        mkdir(tmp_dir)
	
    file_path = f'files/tmp/{time()}'
    with open(file_path, 'wb') as file:
        file.write(_bytes)

    process = Popen(f'ffmpeg -i {file_path} -f wav -loglevel quiet -ac 1 -ar 16000 -sample_fmt s16 -vn -',
                    stdout=PIPE, shell=True)
    converted_bytes = process.communicate()[0]

    remove(file_path)
    return converted_bytes


def transcribe(audio_bytes):
    segments = split_audio(audio_bytes, cpu_count())

    with ThreadPoolExecutor(len(segments)) as pool:
        results = pool.map(transcribe_segment, segments)

        final_result = {'transcript': ''}
        for result in results:
            final_result['transcript'] += result['transcript']

        return final_result


def split_audio(audio_bytes, num_segments, minimum_segment_duration=60):
    audio_pydub = AudioSegment.from_wav(io.BytesIO(audio_bytes))
    total_seconds = audio_pydub.duration_seconds

    max_num_segments = math.floor(total_seconds / minimum_segment_duration)
    num_segments = max_num_segments if max_num_segments < num_segments else num_segments

    if num_segments <= 1:
        return [{
            'bytes': audio_bytes,
            'offset_seconds': 0
        }]

    segment_seconds = total_seconds / num_segments

    segments = []
    start_seconds = 0
    for i in range(num_segments):
        end_seconds = start_seconds + segment_seconds

        with io.BytesIO() as bytesio:
            audio_pydub_segment = \
                audio_pydub[start_seconds * 1000:end_seconds * 1000] if i < num_segments - 1 \
                    else audio_pydub[start_seconds * 1000:]

            audio_pydub_segment.export(bytesio, format='wav')
            bytesio.seek(0)
            segments.append({
                'bytes': bytesio.read(),
                'offset_seconds': start_seconds
            })

        start_seconds += segment_seconds

    return segments


def transcribe_segment(segment):
    rec = Recognizer(model, 16000)
    rec.SetWords(True)
    transcription = ''
    word_bounds = []
    with io.BytesIO(segment['bytes']) as bytesio, wave.open(bytesio, 'rb') as wav:
        while True:
            frames = wav.readframes(4000)
            no_more_frames = len(frames) == 0
            recognizer_result = None
            if no_more_frames:
                recognizer_result = rec.FinalResult()
            elif rec.AcceptWaveform(frames):
                recognizer_result = rec.Result()
            if recognizer_result:
                partial_transcript, partial_word_bounds = process_recognizer_result(recognizer_result)
                transcription += partial_transcript
                word_bounds += partial_word_bounds
            if no_more_frames:
                break

    return {'transcript': transcription}


def process_recognizer_result(result):
    result = loads(result)
    transcription = ''
    word_bounds = []
    if 'result' in result:
        transcription += result['text'] + " "
        word_bounds += result['result']

    return transcription, word_bounds
