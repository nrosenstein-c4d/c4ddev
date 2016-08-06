"""
'Python Draw Helper' written by Niklas Rosenstein.

Copyright by Niklas Rosenstein, 2011.
All rights reserved.                                """

import  c4d
from    c4d     import Vector

def main():
    bd.SetMatrix_Matrix(op, bh.GetMg())

    bd.SetTransparency(1)
    points      = (
        Vector(100, 0, 0),
        Vector(0, 100, 0),
        Vector(0, 0, 100),
    )
    colors      = (
        Vector(1,0,0),
        Vector(0,1,0),
        Vector(0,0,1),
    )
    bd.DrawPolygon(points, colors)

main()
