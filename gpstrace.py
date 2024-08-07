from staticmap import StaticMap, Line, IconMarker
from io import BytesIO
from PIL import Image

icon = open("./icon.png", "rb")

class ramIcon(IconMarker):
    def __init__(self, coord, image, offset_x, offset_y):
        self.coord = coord
        self.img = image # do not load img from disk
        self.offset = (offset_x, offset_y)

def makeTrace(points):
    coordinates = [(point["lng"], point["lat"]) for point in points]
    m = StaticMap(1024, 512, 8, 8)

    line = Line(coordinates, "green", 3)
    m.add_line(line)
    newImg = Image.open(icon)
    newImg = newImg.rotate(90-points[0]['hd'], expand=True)
    print(newImg.size[0]/2)
    marker = ramIcon(coordinates[0], newImg, newImg.size[0]>>1,newImg.size[1]>>1)
    # marker = IconMarker(coordinates[0], "./icon.png", 0,0)
    m.add_marker(marker)

    image = m.render()
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer