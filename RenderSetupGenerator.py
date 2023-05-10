###############################################################################
###############################################################################
##### Creates a 3-key lighting rig for selected object.
##### Select the mesh you want to render and hit 'Generate render setup for selected 
##### mesh' button. A light rig will be automatically generated.
###############################################################################
##### You can manipulate the light rig using 'Render Setup Generator' panel 
##### in the toolbar(press 'T' key while the cursor is on the 3D viewport 
##### to toggle toolbar). It is not recommended to manipulate the rig with 'G', 
##### 'R' and 'S' hotkeys. Keep in mind to make light distance values uniform 
##### for all axes.
###############################################################################
##### !! Do not change the name of elements of Light Rig !!
###############################################################################

bl_info = {
    "name" : "Render Setup Generator",
    "author" : "Efe Ulgen",
    "version" : (1, 0),
    "blender" : (3, 5),
    "location" : "View_3D > Tools",
    "description" : "Creates a 3-key studio lighting around selected object."
    }

import math
import mathutils
import bpy
import bmesh

class OBJECT_OT_generate_render_setup(bpy.types.Operator):
    bl_label = "Generate Render Setup"
    bl_idname = "mesh.generate_render_setup"
    
    def execute(self, context):
        if "Light Rig Root" in bpy.data.objects:
            raise Exception("There is already a light rig in your scene.")
        selected = bpy.context.active_object
        mesh_data = selected.data

        ##### get mesh height #########################
        max_x = min_x = max_y = min_y = max_z = min_z = 0
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

        ##### properties ##########################################################
        cam_dist = edge * 3
        key_light_dist = cam_dist
        fill_light_dist = cam_dist * 1.5
        back_light_dist = cam_dist * 0.75

        ##### camera #########################################################
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = "main_cam"
        cam.location[0] = selected.location[0] + cam_dist  # x position
        cam.location[1] = selected.location[1]                  # y position
        cam.location[2] = selected.location[2] # + (height / 3)   # z position
        cam.rotation_euler[2] = math.radians(90)
        cam.rotation_euler[0] = math.radians(90)
        cam.scale = (edge/2, edge/2, edge/2)
        
        bpy.ops.curve.primitive_bezier_circle_add() # camera local controller
        cam_local_ctrl = bpy.context.object
        cam_local_ctrl.name = "Camera Local Controller"
        cam_local_ctrl.location = cam.location
        cam.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        
        bpy.ops.curve.primitive_bezier_circle_add() # camera global controller
        cam_global_ctrl = bpy.context.object
        cam_global_ctrl.name = "Camera Global Controller"
        cam_global_ctrl.location = selected.location
        cam_global_ctrl.scale = (cam_dist, cam_dist, cam_dist)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        cam_local_ctrl.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        hypotenuse = math.sqrt(math.pow(cam_dist, 2) + math.pow(edge/2, 2))
        angle = math.radians(90) - (math.asin(cam_dist/hypotenuse))
        cam_global_ctrl.rotation_euler[1] = angle * -1

        ##### background #####################################################
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
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        ##### key light rig ############################################################
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
        key_light_global_ctrl.scale = (key_light_dist, key_light_dist, key_light_dist)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        key_light_local_ctrl.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        key_light_global_ctrl.rotation_euler[2] = math.radians(-45)

        ##### fill light rig ############################################################
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
        fill_light_global_ctrl.scale = (fill_light_dist, fill_light_dist, fill_light_dist)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        fill_light_local_ctrl.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        fill_light_global_ctrl.rotation_euler[2] = math.radians(45)

        ##### back light rig ############################################################
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
        back_light_global_ctrl.scale = (back_light_dist, back_light_dist, back_light_dist)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        back_light_local_ctrl.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        back_light_global_ctrl.rotation_euler[2] = math.radians(180)
        back_light_global_ctrl.rotation_euler[1] += math.radians(-80)
        
        ##### root ##########################################################
        bpy.ops.object.empty_add(location=selected.location)
        root = bpy.context.object
        root.name = "Light Rig Root"
        cam_global_ctrl.select_set(True)
        plane.select_set(True)
        key_light_global_ctrl.select_set(True)
        fill_light_global_ctrl.select_set(True)
        back_light_global_ctrl.select_set(True)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        

        for obj in bpy.context.scene.objects:
            obj.lock_location[0] = True
            obj.lock_location[1] = True
            obj.lock_location[2] = True
            obj.lock_rotation[0] = True
            obj.lock_rotation[1] = True
            obj.lock_rotation[2] = True
            obj.lock_scale[0] = True
            obj.lock_scale[1] = True
            obj.lock_scale[2] = True
        return {'FINISHED'}


####################################################################################################
####################################################################################################


class OBJECT_OT_reset_rig_transforms(bpy.types.Operator):
    bl_label = "Reset Light Rig Transformations"
    bl_idname = "mesh.reset_rig_transforms"
    
    def execute(self, context):
        context.scene.objects['Camera Global Controller'].scale = (1, 1, 1)
        context.scene.objects['Camera Global Controller'].rotation_euler = (0, math.radians(-9.46), 0)
        context.scene.objects['Camera Local Controller'].rotation_euler = (0, 0, 0)
        
        context.scene.objects['Background'].scale = (1, 1, 1)
        context.scene.objects['Background'].location = (0, 0, 0)
        
        context.scene.objects['Key Light Global Controller'].scale = (1, 1, 1)
        context.scene.objects['Key Light Global Controller'].rotation_euler = (0, 0, math.radians(-45))
        context.scene.objects['Key Light Local Controller'].rotation_euler =(0, 0, 0)
        
        context.scene.objects['Fill Light Global Controller'].scale = (1, 1, 1)
        context.scene.objects['Fill Light Global Controller'].rotation_euler = (0, 0, math.radians(45))
        context.scene.objects['Fill Light Local Controller'].rotation_euler = (0, 0, 0)
        
        context.scene.objects['Back Light Global Controller'].scale = (1, 1, 1)
        context.scene.objects['Back Light Global Controller'].rotation_euler = (0, math.radians(-80), math.radians(180))
        context.scene.objects['Back Light Local Controller'].rotation_euler = (0, 0, 0)
        return {'FINISHED'}

####################################################################################################
####################################################################################################


class OBJECT_OT_clear_render_setup(bpy.types.Operator):
    bl_label = "Clear Render Setup"
    bl_idname = "mesh.clear_render_setup"
    
    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj in bpy.context.scene.objects['Light Rig Root'].children:
                obj.select_set(True)
                if len(obj.children) > 0:
                    for child in obj.children:
                        child.select_set(True)
                        if len(child.children) > 0:
                            for grandchild in child.children:
                                grandchild.select_set(True)
            else:
                obj.select_set(False)
                
        bpy.context.scene.objects['Light Rig Root'].select_set(True)
        bpy.ops.object.delete()
        return {'FINISHED'}


####################################################################################################
####################################################################################################


class RenderSetupGeneratorPanel(bpy.types.Panel):
    """ Creates a render setup with 3-key lighting """
    bl_label = "Render Setup Generator"
    bl_idname = "SCENE_PT_renderSetup"
    bl_space_type = 'VIEW_3D' # PROPERTIES
    bl_region_type = 'TOOLS' # WINDOW
    bl_context = "objectmode" # scene
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Select a mesh and hit 'Generate Render Setup' to") 
        layout.label(text=" create a 3-key lighting rig.")
        layout.label(text="!! Do not change the names of elements in the rig !!")
        layout.label(text="")
        layout.operator(OBJECT_OT_generate_render_setup.bl_idname, text="Generate Render Setup") # for selected mesh
        
        if "Light Rig Root" not in bpy.data.objects:
            return
        
        layout.operator(OBJECT_OT_reset_rig_transforms.bl_idname, text="Reset Transformations")
        layout.operator(OBJECT_OT_clear_render_setup.bl_idname, text="Clear Render Setup")
        
        row = layout.row()
        row.label(text=("Camera Properties"))
        col = row.column(align=True)
        col.prop(context.scene.objects['Camera Global Controller'], "scale", text="Camera Distance")
        col.prop(context.scene.objects['Camera Global Controller'], "rotation_euler", text="Camera Global Rotation")
        col.prop(context.scene.objects['Camera Local Controller'], "rotation_euler", text="Camera Local Rotation")
        col.prop(context.scene.objects['main_cam'], "scale", text="Camera Size")
        
        layout.label(text="")
        row = layout.row()
        row.label(text="Background Properties")
        col = row.column(align=True)
        col.prop(context.scene.objects['Background'], "scale", text="Background Scale")
        col.prop(context.scene.objects['Background'], "location", text="Background Location")
        
        layout.label(text="")
        row = layout.row()
        row.label(text="Key Light Properties")
        col = row.column(align=True)
        col.prop(context.scene.objects['Key Light Global Controller'], "scale", text="Key Light Distance")
        col.prop(context.scene.objects['Key Light Global Controller'], "rotation_euler", text="Key Light Global Rotation")
        col.prop(context.scene.objects['Key Light Local Controller'], "rotation_euler", text="Key Light Local Rotation")
        col.prop(context.scene.objects['Key Light'], "scale", text="Key Light Size")
        
        layout.label(text="")
        row = layout.row()
        row.label(text="Fill Light Properties")
        col = row.column(align=True)
        col.prop(context.scene.objects['Fill Light Global Controller'], "scale", text="Fill Light Distance")
        col.prop(context.scene.objects['Fill Light Global Controller'], "rotation_euler", text="Fill Light Global Rotation")
        col.prop(context.scene.objects['Fill Light Local Controller'], "rotation_euler", text="Fill Light Local Rotation")
        col.prop(context.scene.objects['Fill Light'], "scale", text="Fill Light Size")
        
        layout.label(text="")
        row = layout.row()
        row.label(text="Back Light Properties")
        col = row.column(align=True)
        col.prop(context.scene.objects['Back Light Global Controller'], "scale", text="Back Light Distance")
        col.prop(context.scene.objects['Back Light Global Controller'], "rotation_euler", text="Back Light Global Rotation")
        col.prop(context.scene.objects['Back Light Local Controller'], "rotation_euler", text="Back Light Local Rotation")
        col.prop(context.scene.objects['Back Light'], "scale", text="Back Light Size")


####################################################################################################
####################################################################################################


def register():
    bpy.utils.register_class(OBJECT_OT_generate_render_setup)
    bpy.utils.register_class(OBJECT_OT_reset_rig_transforms)
    bpy.utils.register_class(OBJECT_OT_clear_render_setup)
    bpy.utils.register_class(RenderSetupGeneratorPanel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_generate_render_setup)
    bpy.utils.unregister_class(OBJECT_OT_reset_rig_transforms)
    bpy.utils.unregister_class(OBJECT_OT_clear_render_setup)
    bpy.utils.unregister_class(RenderSetupGeneratorPanel)
    
if __name__ == "__main__":
    register()
