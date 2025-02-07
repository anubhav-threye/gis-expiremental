# Get Bounding Box of an selected object

import bpy, bmesh
from bpy import context
from mathutils import Vector


def bbox(ob):
    return (Vector(b) for b in ob.bound_box)


def bbox_center(ob):
    return sum(bbox(ob), Vector()) / 8


def bbox_axes(ob):
    bb = list(bbox(ob))
    return tuple(bb[i] for i in (0, 4, 3, 1))


bm = bmesh.new()
ob = context.object
me = ob.data
bm.from_mesh(me)
print(bbox_axes(ob))
