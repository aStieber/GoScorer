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
		
		#0 division check
		if (tmp.start[0] == tmp.end[0]): tmp.start[0] += 1

		tmp.m = (tmp.start[1] - tmp.end[1])/(tmp.start[0] - tmp.end[0])
		tmp.point = ((tmp.start[0] + tmp.end[0]) / 2, (tmp.start[1] + tmp.end[1]) / 2)

		tmp.b = self.findB(tmp)


		return(tmp)

	#line object creator
	def fromSlope(self, _m, _point):
		tmp = line()
		tmp.m = _m
		tmp.point = _point

		tmp.b = self.findB(tmp)

		#generate start and end for line. 
		tmp.start = (0, tmp.b)
		tmp.end = (imageClass.imageSize[0], imageClass.imageSize[0] * tmp.m + tmp.b)
		
		return(tmp)

	def findB(self, line=None):
		if not line: line = self
		x = math.fabs(line.point[1] - (line.m * line.point[0]))
		return(x)

	def draw(self, surf, color=(255, 0, 0)):
		pygame.draw.line(surf, color, self.start, self.end, 2)

	def print_values(self):
		print("Start = ", self.start, "\nEnd = ", self.end, "\nm = ", self.m, "\nb = ", self.b, "\npoint = ", self.point)

class imageClass(object):
	def __init__(self, arg1):#arg1 is board side length
		#load image
		self.loadedImage = pygame.image.load('images/3.png')
		imageClass.imageSize = self.loadedImage.get_size()
		#quantized image
		self.quantizedImage = self.loadedImage.copy()


		self.boardSize = arg1

		self.screen = pygame.display.set_mode(self.imageSize)
		pygame.display.set_caption('baduk, yo')

		self.screen.blit(self.loadedImage, (0, 0))
		pygame.display.flip()
		#time.sleep(10)

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

		# self.screen.blit(self.quantizedImage, (0, 0))
		# pygame.display.flip()

	#http://void.printf.net/~mad/Perspective/
	def discoverBoard(self):
		discoveredOverlay = pygame.Surface(self.imageSize)
		discoveredOverlay.set_colorkey((0, 0, 0)) #makes overlay transparent

		#Variable initialization
		sideIntersect = [None, None]
		horizonIntersect = [None, None, None, None]
		subLineArray = [None, None]


		#boardLines[0] is top, increasing clockwise
		bL = self.get_corners()
		#testing
		for l in bL:
			l.draw(discoveredOverlay)


		for x in range(2):
			sideIntersect[x] = self.get_intersection(bL[x], bL[x+2])
		
		horizon = line().fromEndpoints(_start=sideIntersect[0], _end=sideIntersect[1])

		#horizon's  location
		leveledHorizon = line().fromSlope(_m=-horizon.m, _point=self.find_lowest_corner(bL))
		
		leveledHorizon.draw(discoveredOverlay, (0, 255, 0))

		#find intersections with the leveledHorizon
		for x in range(4):
			horizonIntersect[x] = self.get_intersection(bL[x], leveledHorizon)
			print("line: ", x, "horizon intersection: ", horizonIntersect[x])

		for y in range(2):
			subLineArray[y] = self.subdivide(line().fromEndpoints(_start=horizonIntersect[y], _end=horizonIntersect[y+2]), sideIntersect[y])

		for z in subLineArray:
			for t in z:
				#t.print_values()
				t.draw(discoveredOverlay, (0, 0, 255))

		print(self.get_intersection(subLineArray[0][18], leveledHorizon))

		self.screen.blit(discoveredOverlay, (0, 0))
		pygame.display.flip()
		self.waitForExit()

	def get_intersection(self, line1, line2):
		if line1.m == line2.m:
			return false
		x = (line2.b - line1.b) / (line1.m - line2.m)
		y = (line2.m * x) + line2.b

		return((x, y))

	def subdivide(self, line1, horizonpoint):
		#http://media.wiley.com/Lux/21/438821.image1.jpg
		lineArray = []
		x = self.boardSize - 1
		for z in range(self.boardSize):
			tmpx = line1.start[0] + z*(line1.end[0] - line1.start[0]) / x
			tmpy = line1.start[1] + z*(line1.end[1] - line1.start[1]) / x
			lineArray.append(line().fromEndpoints(_start=(tmpx, tmpy), _end=horizonpoint))

		return(lineArray)

	def get_corners(self):
		corners = [None, None, None, None]
		lines = [None, None, None, None]

		counter = 0

		print("click each corner of the board, moving in a circle")
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
		# HIJACK = [(98, 132), (381, 135), (422, 404), (30, 388)]
		# corners = HIJACK
		for z in range(4):
			lines[z] = line().fromEndpoints(_start=corners[z], _end=corners[(z+1)%4])

		return(lines)

	def find_lowest_corner(self, boardLines):
		tmpmax = boardLines[0]
		for x in range(1, 4):
			#if bL[0]'s start's y is larger than that of tmpmax. Note: larger, because pygame's y is down
			if boardLines[x].start[1] > tmpmax.start[1]:
				tmpmax = boardLines[x]

		return (tmpmax.start)