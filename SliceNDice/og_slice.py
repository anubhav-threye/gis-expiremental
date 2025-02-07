import bpy, bmesh
from bpy import context
from mathutils import Vector

terrain_bbox = (
    Vector((-7999.9990234375, -8000.00048828125, 1.1619997024536133)),
    Vector((8000.0, -8000.00048828125, 1.1619997024536133)),
    Vector((-7999.9990234375, 8000.0, 1.1619997024536133)),
    Vector((-7999.9990234375, -8000.00048828125, 1516.095703125)),
)


# bounding box helper methods
def bbox(ob):
    return (Vector(b) for b in ob.bound_box)


def bbox_center(ob):
    return sum(bbox(ob), Vector()) / 8


def bbox_axes(ob):
    bb = list(bbox(ob))
    return tuple(bb[i] for i in (0, 4, 3, 1))


def slice(bm, start, end, segments):
    if segments == 1:
        return

    def geom(bm):
        return bm.verts[:] + bm.edges[:] + bm.faces[:]

    planes = [start.lerp(end, f / segments) for f in range(1, segments)]
    # p0 = start
    plane_no = (end - start).normalized()
    while planes:
        p0 = planes.pop(0)
        ret = bmesh.ops.bisect_plane(bm, geom=geom(bm), plane_co=p0, plane_no=plane_no)
        bmesh.ops.split_edges(
            bm, edges=[e for e in ret["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        )


bm = bmesh.new()
ob = context.object
me = ob.data
bm.from_mesh(me)

# o, x, y, z = bbox_axes(ob)
o, x, y, z = terrain_bbox

x_segments = 16
y_segments = 16
z_segments = 1

slice(bm, o, x, x_segments)
slice(bm, o, y, y_segments)
slice(bm, o, z, z_segments)
bm.to_mesh(me)

# todo - rename the selected mesh (add .000 as suffix)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set()
