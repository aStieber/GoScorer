import pygame, sys, os, time, math
from pygame.locals import *

class line(object):
	def __init__(self, _start, _end, _m=None):
		#y = mx + b
		self.start = _start
		self.end = _end
		if (not _m):
			self.m = (self.start[1] - self.end[1])/(self.start[0] - self.end[0])
		else:
			self.m = _m
		self.b = -(self.m * self.start[0]) + self.start[1]

	def draw(self, surf):
		RED = (255, 0, 0)
		pygame.draw.line(surf, RED, self.start, self.end, 2)

	def print_values(self):
		print("Start = ", self.start, "\nEnd = ", self.end, "\nm = ", self.m, "\nb = ", self.b)

class imageClass(object):
	def __init__(self, arg1):#arg1 is board side length
		super(imageClass, self).__init__()
		#load image
		self.loadedImage = pygame.image.load('images/1.png')
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
		#for testing
		# self.screen.blit(self.quantizedImage, (0, 0))
		# pygame.display.flip()
		# time.sleep(10)

	#http://void.printf.net/~mad/Perspective/
	def discoverBoard(self):
		
		discoveredOverlay = pygame.Surface(self.imageSize)
		discoveredOverlay.set_colorkey((0, 0, 0))

		#boardLines[0] is top, increasing clockwise
		boardLines = self.get_corners()

		for l in boardLines:
			l.draw(discoveredOverlay)

		x1 = (boardLines[2].b - boardLines[0].b) / (boardLines[0].m - boardLines[2].m)
		y1 = boardLines[0].m * x1 + boardLines[0].b

		x2 = (boardLines[1].b - boardLines[3].b) / (boardLines[3].m - boardLines[1].m)
		y2 = boardLines[3].m * x1 + boardLines[3].b

		
		leveledHorizon = line(boardLines[0].start, boardLines[0].end, line((x1, y1), (x2, y2)).m)
		leveledHorizon.print_values()
		leveledHorizon.draw(discoveredOverlay)




		self.screen.blit(discoveredOverlay, (0, 0))
		pygame.display.flip()
		time.sleep(10)



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
			lines[z] = line(corners[z], corners[(z+1)%4])

		return(lines)

