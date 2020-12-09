# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask   import render_template, request, Response, jsonify;
from jinja2  import TemplateNotFound

import cv2

from app.camera import VideoCamera
from app.ml.mask_model_inference import detect_and_predict_mask

# App modules
from app import app

video_camera = None
global_frame = None

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):

    try:

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( path, segment=segment )
    
    except TemplateNotFound:
        return render_template('page-404.html'), 404


@app.route('/track/<int:camera_id>', methods=['POST'])
def tracking_status(camera_id):
    global video_camera
    print(video_camera)
    if video_camera == None:
        video_camera = VideoCamera()
    print("video_camera after init", video_camera)
    json = request.get_json()
    print("json value = ", json)
    status = json['status']
    print("status = ", status)
    if status == "true":
        print("status is true")
        video_camera.start_tracking()
        return jsonify(result="started")
    else:
        video_camera.stop_tracking()
        return jsonify(result="stopped")


def video_stream():
    global video_camera
    global global_frame
    if video_camera == None:
        video_camera = VideoCamera()

    while True:
        frame = video_camera.get_frame()

        if video_camera.is_record:
            # perform the inference and change the frame
            frame = detect_and_predict_mask(frame)

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        # else:
        #     yield (b'--frame\r\n'
        #            b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None    
