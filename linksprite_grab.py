# linksprite_grab.py
# grabs photo from linksprite LS-Y201 camera
#
# Jon Klein, 8/26/11
# kleinjt@ieee.org
# MIT License
#
# usage: python linksprite_grab picture.jpg

import serial, time, sys

def a2s(arr):
	return ''.join(chr(b) for b in arr)

LK_RESET 		= a2s([0x56, 0x00, 0x26, 0x00])
LK_RESET_RE 		= a2s([0x76, 0x00, 0x26, 0x00, 0x00])
LK_PICTURE 		= a2s([0x56, 0x00, 0x36, 0x01, 0x00])
LK_PICTURE_RE		= a2s([0x76, 0x00, 0x36, 0x00, 0x00])
LK_JPEGSIZE 		= a2s([0x56, 0x00, 0x34, 0x01, 0x00])
LK_JPEGSIZE_RE		= a2s([0x76, 0x00, 0x34, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00]) # then XH XL
LK_STOP			= a2s([0x56, 0x00, 0x36, 0x01, 0x03])
LK_STOP_RE		= a2s([0x76, 0x00, 0x36, 0x00, 0x00])

LK_READPICTURE		= [0x56, 0x00, 0x32, 0x0C, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00];
LK_PICTURE_TIME		= [0x00, 0x0A] # .1 ms
LK_READPICTURE_RE 	= a2s([0x76, 0x00, 0x32, 0x00, 0x00])
JPEG_START 		= a2s([0xFF, 0xD8])
JPEG_END 		= a2s([0xFF, 0xD9])

def init_serial():
	return serial.Serial('/dev/ttyUSB0', '38400', timeout=1)

def main():
	s = init_serial()
	
	link_reset(s)
	take_picture(s)
	size = check_picturesize(s)	
	picture = grab_picture(s, size)	

	filename = 'test.jpg'	
	if(len(sys.argv) > 1):
		filename = sys.argv[1]
	file = open(filename,'wb')
	file.write(picture)
	file.close()	
	s.close()

def grab_picture(s, size):
	s.flushInput()
	s.write(a2s(LK_READPICTURE + size + LK_PICTURE_TIME))
	re = s.read(len(LK_READPICTURE_RE))
	if(re != LK_READPICTURE_RE):
		print 'read picture response failed'
	
	picture = s.read(2)
	if(picture != JPEG_START):
		print 'picture start incorrect'
 	
	while(picture[-2:] != JPEG_END):
		picture = picture + s.read(2);
	
	return picture
	
def link_reset(s):
	s.flushInput()
	s.write(LK_RESET)
	re = s.read(len(LK_RESET_RE))
	if(re != LK_RESET_RE):
		print "reset response failed"	 
	time.sleep(.5)

def take_picture(s):
	s.flushInput();
	s.write(LK_PICTURE)
	re = s.read(len(LK_PICTURE_RE))
	if(re != LK_PICTURE_RE):
		print "picture response failed"
	time.sleep(.1)

def check_picturesize(s):
	s.flushInput()
	s.write(LK_JPEGSIZE)
	re = s.read(len(LK_JPEGSIZE_RE))
	return [ord(re[-2]), ord(re[-1])]

if __name__ == "__main__":
    main()
