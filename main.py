import sys, os, pygame, image

def test(**args):
	for item in args:
		print(item, args['a'])

test(a=1, b=2)
imageObj = image.imageClass(19)#arg1 is board side length
print("cheers")