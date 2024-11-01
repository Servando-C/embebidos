#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ## #############################################################
#
# Author: Mauricio Matamoros
# Date:
#
# ## ############################################################
import smbus2
import magic
import os
import struct
import time
import traceback
import matplotlib.pyplot as plot
import numpy
import _thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# Arduino's I2C device address
SLAVE_ADDR = 0x0A # I2C Address of Arduino 1

# Name of the file in which the log is kept
LOG_FILE = './temp.log'

# Initialize the I2C bus;
# RPI version 1 requires smbus.SMBus(0)
i2c = smbus2.SMBus(1)

#HIstorics
temp_array = []
time_array = []
initial_time = time.time()
c = 0;

class WebServer(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self._serve_ui_file()
    
	def _serve_ui_file(self):
		if not os.path.isfile("index.html"):
			err = "index.html not found."
			self.wfile.write(bytes(err, "utf-8"))
			print(err)
			return
		try:
			with open("index.html", "r") as f:
				print(f)
				content = "\n".join(f.readlines())
		except:
			content = "Error reading index.html"
		self.wfile.write(bytes(content, "utf-8"))

def readTemperature():
	try:
		msg = smbus2.i2c_msg.read(SLAVE_ADDR, 4)
		i2c.i2c_rdwr(msg)  # Performs write (read request)
		data = list(msg)   # Converts stream to list
		# list to array of bytes (required to decode)
		ba = bytearray()
		for c in data:
			ba.append(int(c))
		temp = struct.unpack('<f', ba)
		print('Received temp: {} = {}'.format(data, temp))
		return temp
	except:
		return None

def log_temp(temperature):
	global c
	global temp_array
	global time_array
	time_val = time.time()
	
	try:
		with open(LOG_FILE, 'a+') as fp:
			fp.write('{} {}°C\n'.format(
				time.time(),
				temperature
			))
	except:
		return
	file = open('temp.log')
	lineas = file.readlines()
	for linea in lineas:
		linea_text = linea.split('(')
		if len(linea_text) > 1:
			linea_text = linea_text[1]
			linea_text=float(linea_text[:5])
			temp_array.append(linea_text)
			c = c+1
			time_array.append(c)
	file.close()

	plot.plot(time_array, temp_array, label = "Relacion temperatura [°C]  y Tiempo [s]")
	plot.xlabel("Tiempo [s]")
	plot.ylabel("Temperatura [°C]")
	plot.title("Relacion temperatura [°C]  y Tiempo [s]")
	plot.savefig("grafico.png")
	plot.clf()
	plot.cla()
	c=0
	temp_array = []
	time_array = []
		
def update_temp ():
	while True:
		try:
			Temp=readTemperature()
			log_temp(Temp)
			time.sleep(1)
		except KeyboardInterrupt:
			return
	
def main():
	webServer = HTTPServer(("192.168.2.254", 8080), WebServer)
	print("Servidor iniciado")
	print ("\tAtendiendo solicitudes entrantes")
	try:
		_thread.start_new_thread(update_temp,())
		while True:
			try:
				webServer.serve_forever()
			except KeyboardInterrupt:
				return
	except KeyboardInterrupt:
		pass
	webServer.server_close()
	print("Server stopped.")

if __name__ == '__main__':
	main()
