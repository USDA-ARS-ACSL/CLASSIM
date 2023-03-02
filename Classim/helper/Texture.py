from shapely.geometry import Point, Polygon
'''
Function to classify a soil in the triangle based on sand and clay %
Reference: http://nowlin.css.msu.edu/software/triangle_form.html
'''
class Texture:
    def __init__(self,sand,clay):
        self.sand = sand
        self.clay = clay
    

    def whatTexture(self):
        # Initialize polygons
        silt_loam = Polygon([(0,12),(0,27),(23,27),(50,0),(20,0),(8,12)])
        sand = Polygon([(85,0),(90,10),(100,0)])
        silty_clay_loam = Polygon([(0,27),(0,40),(20,40),(20,27)])
        loam = Polygon([(43,7),(23,27),(45,27),(52,20),(52,7)])
        clay_loam = Polygon([(20,27),(20,40),(45,40),(45,27)])
        sandy_loam = Polygon([(50,0),(43,7),(52,7),(52,20),(80,20),(85,15),(70,0)])
        silty_clay = Polygon([(0,40),(0,60),(20,40)])
        sandy_clay_loam = Polygon([(52,20),(45,27),(45,35),(65,35),(80,20)])
        loamy_sand = Polygon([(70,0),(85,15),(90,10),(85,0)])
        clay = Polygon([(20,40),(0,60),(0,100),(45,55),(45,40)])
        silt = Polygon([(0,0),(0,12),(8,12),(20,0)])
        sandy_clay = Polygon([(45,35),(45,55),(65,35)])

        # Define point
        p = Point(self.sand,self.clay)

        texture = ''

        # Find polygon(s) where the point is.
        if self.sand >= 0 and self.clay >= 0:
            if silt_loam.contains(p):
                texture += '/silt loam'
            if sand.contains(p):
                texture += '/sand'
            if silty_clay_loam.contains(p):
                texture += '/silty clay loam'
            if loam.contains(p):
                texture += '/loam'
            if clay_loam.contains(p):
                texture += '/clay loam'
            if sandy_loam.contains(p):
                texture += '/sandy loam'
            if silty_clay.contains(p):
                texture += '/silty clay'
            if sandy_clay_loam.contains(p):
                texture += '/sandy clay loam'
            if loamy_sand.contains(p):
                texture += '/loamy sand'
            if clay.contains(p):
                texture += '/clay'
            if silt.contains(p):
                texture += '/silt'
            if sandy_clay.contains(p):
                texture += '/sandy clay'

        if texture == '':
            texture='silt loam'

        return texture





