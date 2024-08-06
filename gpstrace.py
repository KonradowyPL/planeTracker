from staticmap import StaticMap, Line
from io import BytesIO



def makeTrace(points):
    coordinates = [(point['lat'],point['lng']) for point in points] 
    m = StaticMap(512, 512, 32, 32) 

    line = Line(coordinates, 'green', 3) 
    m.add_line(line)

    image = m.render()
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer