###############################################
###### Random City Generator ##################
###### author : Efe Ulgen #####################
###############################################

import bpy
import random

scene = bpy.context.scene

city_size = 20
plane_x_pos = 0
plane_y_pos = 0
plane_max_size = 4
plane_min_size = 3
min_street_size = 1

max_building_height = 15
min_building_height = 5
building_height = 0
building_size = 0

for i in range(city_size):
    plane_x_pos = 0
    for t in range(city_size):
        building_size = random.randint(plane_min_size, plane_max_size)
        bpy.ops.mesh.primitive_plane_add(size = building_size, location=(plane_x_pos, plane_y_pos, 0))
        bpy.context.active_object.name = "Building_" + str((i*city_size) + t + 1)
        bpy.ops.object.editmode_toggle()
        building_height = random.randint(min_building_height, max_building_height)
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, building_height)})
        ##### randomly generate roof tops #####
        if random.randint(0, 2) == 0:
            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 1 - (1/building_size))})
            bpy.ops.transform.resize(value=(0.75, 0.75, 0.75))
            ##### creates antennas #####
            if random.randint(0, 1) == 0 and building_height >= max_building_height - 1:
                bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 0)})
                bpy.ops.transform.resize(value=(1/(10 * building_size), 1/(10 * building_size), 1/(10 * building_size)))
                bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, building_height / 7)}) 
        bpy.ops.object.editmode_toggle()
        ####
        plane_x_pos += (plane_max_size + min_street_size)
    plane_y_pos += (plane_max_size + min_street_size)
