from gtts import gTTS
import io


def text_to_speech(text):
    audio_io = io.BytesIO()
    tts = gTTS(text)
    tts.write_to_fp(audio_io)
    audio_io.seek(0)

    return audio_io