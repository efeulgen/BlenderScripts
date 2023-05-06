###############################################################################
##### Render Setup Generator ##################################################
##### author : Efe Ulgen ######################################################
###############################################################################

import math
import mathutils
import bpy
import bmesh

max_x = min_x = max_y = min_y = max_z = min_z = 0
width = length = height = 0

#selected = bpy.data.objects[input("Enter name of mesh to be rendered: ")]
selected = bpy.context.active_object
mesh_data = selected.data

##### get mesh height #########################
for vert in mesh_data.vertices:
    co_world = selected.matrix_world @ vert.co
    min_x = min(min_x, co_world.x)
    max_x = max(max_x, co_world.x)
    min_y = min(min_y, co_world.y)
    max_y = max(max_y, co_world.y)
    min_z = min(min_z, co_world.z)
    max_z = max(max_z, co_world.z)
width = max_y - min_y
length = max_x - min_x
height = max_z - min_z
edge = max([width, length, height])
cam_dist = edge * 3

##################################################
##### camera #####################################
cam_data = bpy.data.cameras.new(name="Camera")
cam = bpy.data.objects.new(name="Camera", object_data=cam_data)
cam.name = "main_cam"
cam.location[0] = selected.location[0] + cam_dist     # x position
cam.location[1] = selected.location[1]                # y position
cam.location[2] = selected.location[2] + (height / 3) # z position
cam.rotation_euler[2] = math.radians(90)
cam.rotation_euler[0] = math.radians(90)
cam.scale = (edge/2, edge/2, edge/2)
hypotenuse = math.sqrt(math.pow(cam.location[0], 2) + math.pow(cam.location[2], 2))
angle = math.radians(90) - (math.asin(cam.location[0]/hypotenuse))
cam.rotation_euler[0] -= angle
bpy.context.scene.collection.objects.link(cam)

##################################################
##### background #################################
bpy.ops.mesh.primitive_plane_add()
plane = bpy.context.active_object
plane.name = "Background"
plane.dimensions = (edge * 2 , edge * 3, 0)
plane.location = selected.location - mathutils.Vector((0, 0, height / 2 + height / 10))
bpy.ops.object.editmode_toggle()
bpy.ops.mesh.select_all(action='DESELECT')
bm_plane = bmesh.from_edit_mesh(plane.data)
bm_plane.edges.ensure_lookup_table()
bm_plane.edges[0].select = True
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, edge * 2)})
bpy.ops.object.editmode_toggle()
new_bevel_mod = plane.modifiers.new("bevel_mod", 'BEVEL')
new_bevel_mod.offset_type = 'PERCENT'
new_bevel_mod.width_pct = 20
new_bevel_mod.segments = 10
bpy.ops.object.shade_smooth()

##################################################
##### 3-key lighting #############################

##### key light rig ####################
bpy.ops.object.light_add(type='AREA') # key light
key_light = bpy.context.active_object
key_light.name = "Key Light"
key_light.location = selected.location
key_light.rotation_euler[1] = math.radians(90)
key_light.scale = (edge, edge, edge)
key_light_strength = key_light.scale[0] * pow((edge*3), 2) # * 100 # (edge*3) * 36 # TODO: debug
key_light.data.energy = key_light_strength

bpy.ops.curve.primitive_bezier_circle_add() # key light local controller
key_light_local_ctrl = bpy.context.active_object
key_light_local_ctrl.name = "Key Light Local Controller"
key_light_local_ctrl.location = selected.location
key_light.select_set(True)
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
key_light_local_ctrl.location[0] = cam.location[0] # translate func. ?

bpy.ops.curve.primitive_bezier_circle_add() # key light global controller
key_light_global_ctrl = bpy.context.active_object
key_light_global_ctrl.name = "Key Light Global Controller"
key_light_global_ctrl.location = selected.location
key_light_global_ctrl.scale = (cam_dist, cam_dist, cam_dist)
key_light_local_ctrl.select_set(True)
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
key_light_global_ctrl.rotation_euler[2] = math.radians(-45)

##### fill light rig ####################
bpy.ops.object.light_add(type='AREA') # fill light
fill_light = bpy.context.active_object
fill_light.name = "Fill Light"
fill_light.location = selected.location
fill_light.rotation_euler[1] = math.radians(90)
fill_light.scale = (edge*3, edge*3, edge*3)
fill_light_strength = key_light_strength * 3 / 2
fill_light.data.energy = fill_light_strength

bpy.ops.curve.primitive_bezier_circle_add() # fill light local controller
fill_light_local_ctrl = bpy.context.active_object
fill_light_local_ctrl.name = "Fill Light Local Controller"
fill_light_local_ctrl.location = selected.location
fill_light.select_set(True)
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
fill_light_local_ctrl.location[0] = cam_dist * 1.5

bpy.ops.curve.primitive_bezier_circle_add() # fill light global controller
fill_light_global_ctrl = bpy.context.active_object
fill_light_global_ctrl.name = "Fill Light Global Controller"
fill_light_global_ctrl.location = selected.location
fill_light_global_ctrl.scale = (cam_dist * 1.5, cam_dist * 1.5, cam_dist * 1.5)
fill_light_local_ctrl.select_set(True)
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
fill_light_global_ctrl.rotation_euler[2] = math.radians(45)

##### back light rig ####################
bpy.ops.object.light_add(type='AREA') # back light
back_light = bpy.context.active_object
back_light.name = "Back Light"
back_light.location = selected.location
back_light.rotation_euler[1] = math.radians(90)
back_light.scale = (edge, edge, edge)

bpy.ops.curve.primitive_bezier_circle_add() # back light local controller
back_light_local_ctrl = bpy.context.active_object
back_light_local_ctrl.name = "Back Light Local Controller"
back_light_local_ctrl.location = selected.location
back_light.select_set(True)
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
back_light_local_ctrl.location[0] = cam_dist

bpy.ops.curve.primitive_bezier_circle_add() # back light global controller
back_light_global_ctrl = bpy.context.active_object
back_light_global_ctrl.name = "Back Light Global Controller"
back_light_global_ctrl.location = selected.location
back_light_global_ctrl.scale = (cam_dist*0.75, cam_dist*0.75, cam_dist*0.75)
back_light_local_ctrl.select_set(True)
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
back_light_global_ctrl.rotation_euler[2] = math.radians(180)
back_light_global_ctrl.rotation_euler[1] += math.radians(-80)