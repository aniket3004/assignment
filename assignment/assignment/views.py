from django.shortcuts import render
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2,urllib.request
import threading
import numpy as np

@gzip.gzip_page
def Home(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam),content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request,"myapp/index.html")

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed,self.frame) = self.video.read()
        threading.Thread(target=self.update,args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed,self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'r\n\r\n')

def IPWebCam(object):
    def __init__(self):
        self.url = "http://192.168.1.2:8080/"

    def __del__(self):
        cv2.destroyAllWindows()

    def get_frame(self):
        imgResp = urllib.request.urlopen(self.url)
        imgNp = np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img= cv2.imdecode(imgNp,1)
        resize = cv2.resize(img,(640,480), interpolation=cv2.INTER_LINEAR)
        frame_flip = cv2.flip(resize,1)
        jpeg = cv2.imencode('.jpg',frame_flip)
        return jpeg.tobytes()


def webcam_feed(request):
    return StreamingHttpResponse(gen(IPWebCam(object)),content_type='multipart/x-mixed-replace;boundary=frame')