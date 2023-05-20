import io
import os
import cv2
import time
import base64
import argparse
from config import *
import psutil as psu
import numpy as np
from PIL import Image
import random
	
import asyncio
import threading
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback

from src.process import main, start_stop_driver

global frame
frame = np.array([])

class IndexHandler(tornado.web.RequestHandler):
	'''
	Render index 
	'''
	def get(self):
		self.render('view/index.html', port=PORT)

class SystemMonitor(tornado.websocket.WebSocketHandler):
	'''
	Monitoring CPU, RAM device
	'''
	def get(self):
		system_monitor = {
			'cpu':psu.cpu_percent(),
			'memory':psu.virtual_memory().percent
		}
		self.write(system_monitor)

class WebSocket(tornado.websocket.WebSocketHandler):
	def on_message(self, message):
		'''
		Evaluates the function pointed to by json-rpc
		Start and infinite loop when this is called
		'''
		if message == 'read_camera':
			self.camera_loop = PeriodicCallback(self.loop, 10)
			self.camera_loop.start()
		else: print("Unsupported function: " + message)

	async def loop(self):
		'''
		Send camera image in infinite loop
		'''
		sio = io.BytesIO()
		global frame
		if frame is None: frame = np.array([])
		if not frame is None and frame.dtype == 'uint8':
			# ret, frame = camera.read()
			img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
			img.save(sio, "JPEG")
		else:
			DeviceCamera().start()
			camera = cv2.VideoCapture(CAMERA_URL['url'][0])
		# else:
			# camera.capture(sio, "jpeg", use_video_port=True)
		
		try:
			await self.write_message({
				"image": base64.b64encode(sio.getvalue()).decode('utf-8'),
				"infertil" : random.randint(1,9),
				"fertil": random.randint(1,9)
				})
		except tornado.iostream.StreamClosedError as e:
			print('StreamClosedError:', e)
			self.camera_loop.stop()
			pass
		except tornado.websocket.WebSocketClosedError as e:
			print('WebSocketClosedError:', e)
			self.camera_loop.stop()
			pass
		except KeyError as e:
			print('KeyError:', e)
			self.camera_loop.stop()
			pass

		time.sleep(0.01)

class WebServer(threading.Thread):
	'''
	Setup tornado serve
	'''
	print('Start Web Server')
	def run(self):
		asyncio.set_event_loop(asyncio.new_event_loop())
		
		with open(os.path.join(ROOT, "password.txt")) as in_file:
			PASSWORD = in_file.read().strip()

		handlers = [(r'/', IndexHandler),
					(r'/websocket', WebSocket),
					(r'/system_monitor', SystemMonitor),
					(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': ROOT+'/assets'})]
		application = tornado.web.Application(handlers, cookies_secret=PASSWORD)
		application.listen(PORT)
		# webbrowser.open(f'http://127.0.0.1:{PORT}', new=2)
		tornado.ioloop.IOLoop.instance().start()

class DeviceCamera(threading.Thread):
	'''
	Setup input camera using device machine
	Change resolution camera (high, medium, low)
	'''
	print('Start Process')
	def run(self):		
		# initialize the camera and grab a reference to the raw camera capture
		# self.camera = PiCamera()
		# self.camera.resolution = (480,368)
		# self.camera.framerate = 15
		# rawCapture = PiRGBArray(self.camera, size=(480,368))
		# time.sleep(1)
		
		# for frames in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		# 	frame = frames.array
		# 	cv2.imwrite('test.jpg', frame)
		# 	rawCapture.truncate(0)
		# 	key = cv2.waitKey(1) & 0xFF
		# 	if key == ord("q"):
		# 		self.stop_camera()
		# 		break

		# def stop_camera(self):
		# 	self.camera.stop_preview()
		# 	self.camera.close()

		# start conveyor
		while True:
			frame, classification = main()

class DriverStart(threading.Thread):
	print('Start Conveyor')
	def run(self):
		start_stop_driver()

if __name__ == '__main__':
	DeviceCamera().start()
	WebServer().start()
	DriverStart().start()