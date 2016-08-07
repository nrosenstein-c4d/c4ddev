import  c4d
from c4d import Vector

def main(op, drawpass, bd, bh):
    if drawpass != c4d.DRAWPASS_OBJECT:
        return
    bd.SetMatrix_Matrix(op, bh.GetMg())
    bd.SetTransparency(1)
    points = (
        Vector(100, 0, 0),
        Vector(0, 100, 0),
        Vector(0, 0, 100),
    )
    colors = (
        Vector(1,0,0),
        Vector(0,1,0),
        Vector(0,0,1),
    )
    bd.DrawPolygon(points, colors)
