#!/usr/bin/env python
import os
from importlib import import_module
from pathlib import Path
from typing import Generator
import logging

from flask import Flask, Response, redirect, jsonify, url_for, request
from flask_cors import CORS

logging.basicConfig(format='[%(asctime)s] [CameraPi] [%(levelname)s] %(message)s', level=logging.DEBUG)

provider = Flask(__name__)
CORS(provider)

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('lib.camera_' + os.environ['CAMERA']).Camera
else:
    from lib.camera_base import Camera

camera = Camera()

current_path = Path(__file__).parent.parent
with open(os.path.join(current_path, '.password')) as password_file:
    password = password_file.read()
password = password.strip()


def get_base_path() -> str:
    """

    Returns:
        str: The base url path used during routing, i.e. the location in the nginx server.

    """
    return '/camerapi/'


def get_stream_path() -> str:
    """

    Returns:
        str: The path to the actual camera stream.

    """
    return get_base_path() + 'stream/'


def video_feed_generator(camera) -> Generator[str, None, None]:
    """
    
    Returns:
        Generator[str, None, None]: JPG camera images encoded as bitstring.
    """
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@provider.route(get_stream_path())
def video_feed() -> Response:
    global camera
    camera = Camera()

    """

    Returns:
        Response: JPG camera images encoded as HTML response for streaming to the web.
    """
    return Response(video_feed_generator(camera), mimetype='multipart/x-mixed-replace; boundary=frame')


@provider.route('/')
def root() -> Response:
    """

    Returns:
        Response: Endpoint for the landing page.
    """
    logging.info('Redirecting from / to stream')
    return redirect(get_stream_path())


@provider.route(get_base_path())
def index() -> Response:
    """

    Returns:
        Response: Endpoint for the video stream.
    """
    logging.info('Redirecting from ' + get_base_path() + ' to stream')
    return redirect(get_stream_path())


def get_password() -> str:
    data = request.get_json()
    if data is None:
        return ''

    if 'password' not in data:
        return ''

    logging.info('Password received')
    return str(data['password']).strip()


@provider.route(get_base_path() + 'start_recording', methods=['POST'])
def start_recording() -> Response:
    global camera
    """

    Starts the recording of the camera to disk on the server.

    Returns:
        Response: Endpoint for the video stream.
    """
    global password
    logging.info('Start recording requested')
    if get_password() != password:
        logging.info('Password incorrect')
        return jsonify({'success': False})

    logging.info('Password correct')
    camera.record()
    return jsonify({'success': True})


@provider.route(get_base_path() + 'stop_recording', methods=['POST'])
def stop_recording() -> Response:
    """

    Stops the recording of the camera to disk on the server.

    Returns:
        Response: Endpoint for the video stream.
    """
    global password
    logging.info('Stop recording requested')
    if get_password() != password:
        logging.info('Password incorrect')
        return jsonify({'success': False})
    
    logging.info('Password correct')
    camera.stop_recording()
    return jsonify({'success': True})


@provider.route(get_base_path() + 'is_recording', methods=['GET'])
def is_recording() -> Response:
    """

    Stops the recording of the camera to disk on the server.

    Returns:
        Response: Endpoint for the video stream.
    """
    logging.info('Is recording requested')
    return jsonify({'success': camera.is_recording()})


@provider.route(get_base_path() + 'start_streaming')
def start_streaming() -> Response:
    """

    Enables streaming of the live camera image to the web.

    Returns:
        Response: Endpoint for the video stream.
    """
    logging.warning("Start streaming not implemented")
    return Response("Start streaming not yet implemented", 404)


@provider.route(get_base_path() + 'stop_streaming')
def stop_streaming() -> Response:
    """

    Disables streaming of the live camera image to the web.

    Returns:
        Response: Endpoint for the video stream.
    """
    logging.warning("Stop streaming not implemented")
    return Response("Stop streaming not yet implemented", 404)
