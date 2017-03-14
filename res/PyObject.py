import c4d
from c4d import Vector

def Message(op, msg, data):
    return True

def AddToExecution(op, list):
    return False

def Execute(op, doc, bt, prority, flags):
    return c4d.EXECUTIONRESULT_OK

def Draw(op, drawpass, bd, bh):
    if drawpass == c4d.DRAWPASS_OBJECT:
        bd.SetMatrix_Matrix(op, bh.GetMg())
        bd.SetTransparency(1)
        V = c4d.Vector
        points = [V(100, 0, 0), V(0, 100, 0), V(0, 0, 100)]
        colors = [V(1,0,0),     V(0,1,0),     V(0,0,1)]
        bd.DrawPolygon(points, colors)
    return True

def GetVirtualObjects(op, hh):
    return c4d.BaseObject(c4d.Onull)
