import io
from subprocess import CalledProcessError

import fleep
from flask import Blueprint, jsonify, request, send_file
from objsize import get_deep_size
from requests import post
import os
import tempfile
from moviepy.editor import VideoFileClip
import whisper
from transformers import pipeline
import torch

from src.app.TTS import text_to_speech
from src.app.speech import transcribe, extract_audio
from src.app.summarizer import summarize_text
from src.exceptions import error_to_json

speech_blueprint = Blueprint('speech', __name__)

ALLOWED_EXTENSIONS = ['mp4', 'mp3', 'wav']

MAX_FILE_LIMIT = min(500 * 1024, 512000) * 1024


@speech_blueprint.route('/api/extract', methods=['POST'])
def transcription():
    speech_file = request.get_data()
    if not speech_file:
        return error_to_json(
            error="file_not_found",
            description="No file was detected in the body request. "
                        "Please make sure to include a binary file in body request."
        ), 400

    file_size = get_deep_size(speech_file)
    if file_size > MAX_FILE_LIMIT:
        return error_to_json(
            error="invalid_file_size",
            description="The uploaded file is greater than the maximum file length accepted."
        ), 413
    
    file_info = fleep.get(speech_file)
    try:
        # non audio/video file detected
        if file_info.type[0] not in ['video', 'audio']:
            return error_to_json(
                error="ivalid_file_extension",
                description=f"The file format {file_info.extension[0]} is not supported. "
                            f"Supported file formats are : "
                            f'{", ".join(ALLOWED_EXTENSIONS)}'
            ), 400
    except Exception as e:
        return error_to_json(
            error="invalid_file",
            description=f"The file uploaded seems to be corrupted or not in the supported "
                        f'formats : {",".join(ALLOWED_EXTENSIONS)}.'
        ), 400

    try:
        result = transcribe(
            extract_audio(
                speech_file,
                file_info
            )
        )
    except CalledProcessError:
        return error_to_json(
            error="ivalid_file_extension",
            description=f"The file format {file_info.extension[0]} is not supported. "
                        f"Supported file formats are : "
                        f'{", ".join(ALLOWED_EXTENSIONS)}'
        ), 400
    
    transcript = result['transcript']
    summary = summarize_text(transcript)
    
    # return jsonify({
    #     'transcript': transcript,
    #     'summary': summary
    # })

    TTS_result = text_to_speech(summary)

    return send_file(
        TTS_result,
        as_attachment=False,
        mimetype='audio/mpeg'
    )
