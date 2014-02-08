"""
Monochromatic bitmap with support for replacement of regions with another
bitmap. Supports storage of bit in row- or column-major order.
"""
from bitarray import bitarray

class Bitmap:
    def __init__(self, width, height, major_axis = 'x'):
        self.width = width
        self.height = height
        self.data = (width * height) * bitarray('0', endian='little')
        self._major_axis = major_axis

    def _get_rows(self):
        height = self.height
        width = self.width
        if self._major_axis == 'y':
            (width, height) = (height, width)
        if self._major_axis == 'x':
            for y in range(height):
                yield self.data[(width * y):(width * y) + width]
        else:
            for y in range(self.height):
                yield self.data[ y:(self.width * self.height):self.height]

    rows = property(_get_rows, None, None)

    def _get_cols(self):
        height = self.height
        width = self.width
        if self._major_axis == 'y':
            for y in range(width):
                yield self.data[(height * y):(height * y) + height]
        else:
            for y in range(width):
                yield self.data[y:(height * width):width]

    cols = property(_get_cols, None, None)

    major_axis = property(lambda self: self._major_axis)
    bytes = property(lambda self: self._data.tobytes())

#    def getColAsByte(self, page, col):
#        #Used if bits are stored as sequential rows
#        return self.data[(page * self.width * 8) + col:8 * self.width:128]
    
#     def transformToColBytes(self):
#        #Transforms to the format needed by the display memory of the ssd1306 controller
#        data = bitarray()
#        for page in range(self.height / 8):
#            for col in range(self.width):
#               # print page, col
#                #print page * self.width * 8 + col, 8 * self.width
#                #print self.data[(page * self.width * 8) + col:((page + 1)  *
#                #                 self.width * 8) - 1:self.width]
#                data.extend(self.data[(page * self.width * 8) + col:((page + 1)  *
#                                 self.width * 8) - 1:self.width])
#        return data
        
    def replace_rect(self, x, y, bitmap):
        height = self.height
        width = self.width
        bheight = bitmap.height
        bwidth = bitmap.width
        if self._major_axis == 'y':
            (x,y) = (y,x)
            (width, height) = (height, width)
            (bheight, bwidth) = (bwidth, bheight)
        count = 0
        if self._major_axis == 'x':
            for row in bitmap.rows:
                self.data[((count + y) * width) + x:((count + y) * width) + x +
                           len(row)] \
                    = row
                count += 1
        if self._major_axis == 'y':
            for col in bitmap.cols:
                self.data[((count + y) * width) + x:((count + y) * width) + x +
                          len(col)] \
                    = col
                count += 1

    def draw_pixel(self, x, y, on=True):
        height = self.height
        width = self.width
        if self._major_axis == 'y':
            (x,y) = (y,x)
            (width, height) = (height, width)
        self.data[(y * width) + x] = on

    # returns the width in pixels of the string allowing for kerning & interchar-spaces
    def text_width(self, string, font):
        x = 0
        prev_char = None
        for c in string:
            if (c<font.start_char or c>font.end_char):
                if prev_char != None:
                    x += font.space_width + prev_width + font.gap_width
                prev_char = None
            else:
                pos = ord(c) - ord(font.start_char)
                (width,offset) = font.descriptors[pos]
                if prev_char != None:
                    x += font.kerning[prev_char][pos] + font.gap_width
                prev_char = pos
                prev_width = width
                
        if prev_char != None:
            x += prev_width
            
        return x

    def draw_text(self, x, y, string, font):
        height = font.char_height
        prev_char = None

        for c in string:
            if (c<font.start_char or c>font.end_char):
                if prev_char != None:
                    x += font.space_width + prev_width + font.gap_width
                prev_char = None
            else:
                pos = ord(c) - ord(font.start_char)
                (width,offset) = font.descriptors[pos]
                if prev_char != None:
                    x += font.kerning[prev_char][pos] + font.gap_width
                prev_char = pos
                prev_width = width
                
                bytes_per_row = (width + 7) / 8
                for row in range(0,height):
                    py = y + row
                    mask = 0x80
                    p = offset
                    for col in range(0,width):
                        px = x + col
                        if (font.bitmaps[p] & mask):
                            self.draw_pixel(px,py,1)  # for kerning, never draw black
                        mask >>= 1
                        if mask == 0:
                            mask = 0x80
                            p+=1
                    offset += bytes_per_row
          
        if prev_char != None:
            x += prev_width

        return x

    def clear(self):
        self.data = self.width * self.height * bitarray('0')

    def clear_block(self, x, y, blockWidth, blockHeight):
        height = self.height
        width = self.width
        if self._major_axis == 'y':
            (x,y) = (y,x)
            (width, height) = (height, width)
        if self._major_axis == 'x':
            for row in range(blockHeight):
                self.data[((row + y) * width) + x:((row + y) * width) + x +
                           blockWidth] \
                    = blockWidth * bitarray('0')
        if self._major_axis == 'y':
            for col in range(blockWidth):
                self.data[((col + y) * width) + x:((col + y) * width) + x +
                          blockHeight] \
                    = blockWidth * bitarray('0')

    def dump(self):
        for row in self.rows:
            str = ""
            for bit in row:
                if bit:
                    str = str + "*"
                else:
                    str = str + " "
            print str

if __name__ == "__main__":
    import time
    bmp = Bitmap(32, 16, major_axis = 'x')
    #for i in range(16):
    #    bmp.drawPixel(15, i)
    #bmp.drawPixel(15, 14)
    #bmp.dump()
    #print "-------"
    bmp2 = Bitmap(32, 8, major_axis = 'x')
    bmp2.data = (32 * 8) * bitarray('1')
    #for col in bmp2.cols:
    #    print col
    #print "---"
    #t1 = time.time()
    #for i in range(1000):
    #    bmp.replaceRect(0,13,bmp2)
    #    bmp.transformToColBytes()
    #print (time.time() - t1) / 1000
    bmp.replace_rect(0,1,bmp2)
    #bmp2.dump()
    bmp.dump()
