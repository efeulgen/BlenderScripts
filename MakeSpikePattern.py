###########################################################################
##### Make Spike Pattern ##################################################
##### author : Efe Ulgen ##################################################
###########################################################################

import bpy
import bmesh

#primitive_type = input("Enter primitive type: ")
#if primitive_type == "Cube":
#    bpy.ops.mesh.primitive_cube_add()
#elif primitive_type == "Sphere":
#    bpy.ops.mesh.primitive_uv_sphere_add()
#elif primitive_type == "IcoSphere":
#    bpy.ops.mesh.primitive_ico_sphere_add()
#elif primitive_type == "Torus":
#    bpy.ops.mesh.primitive_torus_add()

mesh = bpy.context.active_object
#subsurf_level = int(input("Enter subsurf level: "))
subsurf_level = 2

bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_all(action='DESELECT')

bm = bmesh.from_edit_mesh(mesh.data)
bm.faces.ensure_lookup_table()

for f in bm.faces:
    f.select = True

bpy.ops.mesh.extrude_faces_move(TRANSFORM_OT_shrink_fatten={'value':0.1}) # TRANSFORM_OT_translate={'value':(0, 0, 1)},

selected_faces = []
for f in bm.faces:
    if f.select == True:
        selected_faces.append(f)
        
bpy.ops.mesh.select_all(action='DESELECT')

for f in selected_faces:
    f.select = True
    bpy.ops.mesh.merge(type='CENTER')
    bpy.ops.mesh.select_all(action='DESELECT')
    
bpy.ops.object.editmode_toggle()

##### add subsurf ####################
if subsurf_level > 0:
    new_mod = mesh.modifiers.new("mod", 'SUBSURF')
    new_mod.levels = subsurf_level
