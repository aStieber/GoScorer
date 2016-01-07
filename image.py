import pygame, sys, os, time, math
from pygame.locals import *

class line(object):
	def __init__(self): #y = mx + b
		
		#variable declaration
		self.start, self.end, self.m, self.b, self.point = (None,)*5

	#line object creator
	def fromEndpoints(self, _start, _end):
		tmp = line()
		tmp.start = _start
		tmp.end = _end
		
		tmp.m = (tmp.start[1] - tmp.end[1])/(tmp.start[0] - tmp.end[0])
		tmp.point = ((tmp.start[0] + tmp.end[0]) / 2, (tmp.start[1] + tmp.end[1]) / 2)

		tmp.b = self.genB(tmp)


		return(tmp)

	#line object creator
	def fromSlope(self, _m, _point):
		tmp = line()
		tmp.m = _m
		tmp.point = _point

		tmp.b = self.genB(tmp)

		lowx = -(tmp.point[0] * 10)
		highx = tmp.point[0] * 10
		tmp.start = (lowx, lowx * tmp.m + tmp.b)
		tmp.end = (highx, highx * tmp.m + tmp.b)

		return(tmp)

	def genB(self, line):
		x = math.fabs(line.point[1] - (line.m * line.point[0]))
		return(x)


	def draw(self, surf, color=(255, 0, 0)):
		#pygame needs a start and end point, so we have to generate them if they don't exist. This is only needed for drawing, a y=mx+b model suits the rest of the math better
		pygame.draw.line(surf, color, self.start, self.end, 2)

	def print_values(self):
		print("Start = ", self.start, "\nEnd = ", self.end, "\nm = ", self.m, "\nb = ", self.b, "\npoint = ", self.point)

class imageClass(object):
	def __init__(self, arg1):#arg1 is board side length
		#load image
		self.loadedImage = pygame.image.load('images/4.png')
		self.imageSize = self.loadedImage.get_size()
		#quantized image
		self.quantizedImage = self.loadedImage.copy()


		self.boardSize = arg1

		self.screen = pygame.display.set_mode(self.imageSize)
		pygame.display.set_caption('baduk, yo')

		self.screen.blit(self.loadedImage, (0, 0))
		pygame.display.flip()
		#time.sleep(10)

		self.quantize()
		self.discoverBoard()

	def waitForExit(self):
		while(True):
			for event in pygame.event.get():
				if (event.type == QUIT):
					sys.exit()

	def quantize(self):
		BROWN = (165, 130, 100)
		WHITE = (200, 200, 200)
		BLACK = (20, 20, 20)
		for x in range(self.imageSize[0]):
			for y in range(self.imageSize[1]):
				#for each pixel
				pixel = self.loadedImage.get_at((x, y)) 
				#calculate euclidian distance for each color
				brownDist = (math.sqrt((BROWN[0] - pixel[0])**2 + (BROWN[1] - pixel[1])**2 + (BROWN[2] - pixel[2])**2), BROWN)
				whiteDist = (math.sqrt((WHITE[0] - pixel[0])**2 + (WHITE[1] - pixel[1])**2 + (WHITE[2] - pixel[2])**2), WHITE)
				blackDist = (math.sqrt((BLACK[0] - pixel[0])**2 + (BLACK[1] - pixel[1])**2 + (BLACK[2] - pixel[2])**2), BLACK)

				maximum = brownDist
				if whiteDist[0] < maximum[0]:
					maximum = whiteDist
				if blackDist[0] < maximum[0]:
					maximum = blackDist

				self.quantizedImage.set_at((x, y), maximum[1])

	#http://void.printf.net/~mad/Perspective/
	def discoverBoard(self):
		
		discoveredOverlay = pygame.Surface(self.imageSize)
		discoveredOverlay.set_colorkey((0, 0, 0))

		#boardLines[0] is top, increasing clockwise
		bL = self.get_corners()
		#testing
		for l in bL:
			l.draw(discoveredOverlay)

		int1 = self.get_intersection(bL[0], bL[2])
		int2 = self.get_intersection(bL[1], bL[3])
		horizon = line().fromEndpoints(_start=int1, _end=int2)
		
		leveledHorizon = line().fromSlope(_m=horizon.m, _point=(25, 25))

		#find intersections with the leveledHorizon

		horint0 = self.get_intersection(bL[0], leveledHorizon)
		horint2 = self.get_intersection(bL[2], leveledHorizon)

		subLineArray = self.subdivide(line().fromEndpoints(_start=horint0, _end=horint2), int1)

		for z in subLineArray:
			z.draw(discoveredOverlay, (0, 0, 255))

		self.screen.blit(discoveredOverlay, (0, 0))
		pygame.display.flip()
		self.waitForExit()

	def get_intersection(self, line1, line2):
		x = (line2.b - line1.b) / (line1.m - line2.m)
		y = (line2.m * x) + line2.b

		return((x, y))

	def subdivide(self, line1, horizonpoint):
		lineArray = []
		deltax = math.fabs((line1.start[0] - line1.end[0]) / (self.boardSize - 1))

		for z in range(self.boardSize):
			tmpx = line1.start[0] + (deltax * z)
			tmpy = tmpx * line1.m + line1.b
			subint = (tmpx, tmpy)
			lineArray.append(line().fromEndpoints(_start=subint, _end=horizonpoint))

		return(lineArray)

	def get_corners(self):
		corners = [None, None, None, None]
		lines = [None, None, None, None]

		counter = 0

		print("click each corner of the board. Start at top left and move clockwise.")
		happening = True
		while (happening):
			for event in pygame.event.get():
				if counter >= 4:
					happening = False
					break

				if (event.type == MOUSEBUTTONDOWN):
					corners[counter] = (event.pos[0], event.pos[1])
					counter += 1
					print(counter, "clicked.")
				elif (event.type == QUIT):
					sys.exit()
		#end of while
		for z in range(4):
			lines[z] = line().fromEndpoints(_start=corners[z], _end=corners[(z+1)%4])

		return(lines)