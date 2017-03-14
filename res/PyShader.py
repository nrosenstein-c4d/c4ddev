import c4d

def Message(sh, msg, data):
    return True

def InitRender(sh, irs, customdata):
    return c4d.INITRENDERRESULT_OK

def FreeRender(sh, customdata):
    pass

def Output(sh, cd, customdata, once):
    return c4d.Vector(0.0, 0.0, 0.0)
