import pygame

def makeframe(alpha=255):
	bg = (200,200,200)
	fg = (150,150,150)
	black = (50,50,50)

	ctrlr = pygame.Surface((250,110))
	ctrlr.fill((0,0,0))
	ctrlr.set_colorkey((0,0,0))
	ctrlr.set_alpha(alpha)

	pygame.font.init()
	bold = pygame.font.Font(None,12)
	bold.set_bold(True)
	italic = pygame.font.Font(None,8)
	italic.set_italic(True)
	logo = pygame.font.Font(None,16)
	logo.set_italic(True)
	logo.set_underline(True)

	#frame
	pygame.draw.circle(ctrlr, bg, (55,55), 50)
	pygame.draw.rect(ctrlr, bg, (55,5,140,90))
	pygame.draw.circle(ctrlr, bg, (195,55), 50)
	pygame.draw.circle(ctrlr, fg, (55,55), 25, 1)
	pygame.draw.circle(ctrlr, fg, (195,55), 45)

	#dpad center
	pygame.draw.circle(ctrlr, black, (55,55), 7)

	#bayx outlines
	pygame.draw.line(ctrlr, bg, (195,74), (220,54), 21)
	pygame.draw.circle(ctrlr, bg, (195,75), 10)
	pygame.draw.circle(ctrlr, bg, (220,55), 10)
	pygame.draw.line(ctrlr, bg, (172,54), (195,36), 21)
	pygame.draw.circle(ctrlr, bg, (172,55), 10)
	pygame.draw.circle(ctrlr, bg, (195,35), 10)

	#text
	ctrlr.blit(logo.render('SUPEROPTI', True, black), (85,10))
	ctrlr.blit(italic.render('SELECT', True, black), (94,75))
	ctrlr.blit(italic.render('START', True, black), (122,75))
	ctrlr.blit(bold.render('Y', True, bg), (155,65))
	ctrlr.blit(bold.render('B', True, bg), (176,84))
	ctrlr.blit(bold.render('X', True, bg), (209,21))
	ctrlr.blit(bold.render('A', True, bg), (230,40))

	return ctrlr

def drawbuttons(frame, pad):
	B,Y,Se,St,Up,Down,Left,Right,A,X,L,R = [pad & (1<<i) for i in xrange(12)]

	bg = (200,200,200)
	fg = (150,150,150)
	black = (50,50,50)

	red = (100,0,150)
	yellow = red
	blue = (150,50,200)
	green = blue
	#red = (200,50,0)
	#yellow = (250,200,0)
	#blue = (0,0,200)
	#green = (50,200,0)

	ctrlr = frame.copy()

	#dpad
	if Up:    pygame.draw.rect(ctrlr, black, (47,35,15,20))
	if Down:  pygame.draw.rect(ctrlr, black, (47,55,15,20))
	if Left:  pygame.draw.rect(ctrlr, black, (35,47,20,15))
	if Right: pygame.draw.rect(ctrlr, black, (55,47,20,15))

	#select/start
	if Se: pygame.draw.line(ctrlr, black, (100,67), (110,60), 10)
	if St: pygame.draw.line(ctrlr, black, (125,67), (135,60), 10)

	#ba
	if B: pygame.draw.circle(ctrlr, yellow, (195,75), 8)
	if A: pygame.draw.circle(ctrlr, red, (220,55), 8)

	#yx
	if Y: pygame.draw.circle(ctrlr, green, (172,55), 8)
	if X: pygame.draw.circle(ctrlr, blue, (195,35), 8)

	#lr
	if L:
		pygame.draw.lines(ctrlr, bg, True, ((30,9), (48,3), (80,3)), 2)
		pygame.draw.lines(ctrlr, fg, False, ((30,11), (48,5), (80,5)), 1)
	if R:
		pygame.draw.lines(ctrlr, bg, True, ((168,3), (200,3), (220,9)), 2)
		pygame.draw.lines(ctrlr, fg, False, ((168,5), (200,5), (220,11)), 1)

	return ctrlr
