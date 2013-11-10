# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Script copyright (C) Campbell Barton, Bastien Montagne


import datetime
import math
import os
import time

import bpy
from mathutils import Vector, Matrix

from . import encode_bin


# for convenience
E = encode_bin.FBXElem


# "Constants"
FBX_HEADER_VERSION = 1003
FBX_VERSION = 7300


# Helpers to generate standard FBXProperties70 properties...
# XXX Looks like there can be various variations of formats here... Will have to be checked ultimately!
def elem_props_set_bool(elem, name, value):
    p = E(b"P")
    p.add_string(name)
    p.add_string(b"bool")
    p.add_string(b"")
    p.add_string(b"")
    p.add_bool(value)
    elem.elems.append(p)


def elem_props_set_integer(elem, name, value):
    p = E(b"P")
    p.add_string(name)
    p.add_string(b"int")
    p.add_string(b"Integer")
    p.add_string(b"")
    p.add_int32(value)
    elem.elems.append(p)


def elem_props_set_enum(elem, name, value):
    p = E(b"P")
    p.add_string(name)
    p.add_string(b"enum")
    p.add_string(b"")
    p.add_string(b"")
    p.add_int32(value)
    elem.elems.append(p)


def elem_props_set_number(elem, name, value):
    p = E(b"P")
    p.add_string(name)
    p.add_string(b"double")
    p.add_string(b"Number")
    p.add_string(b"")
    p.add_float64(value)
    elem.elems.append(p)


def elem_props_set_color_rgb(elem, name, value):
    p = E(b"P")
    p.add_string(name)
    p.add_string(b"ColorRGB")
    p.add_string(b"Color")
    p.add_string(b"")
    p.add_float64(value[0])
    p.add_float64(value[1])
    p.add_float64(value[2])
    elem.elems.append(p)


def elem_props_set_string_ex(elem, name, value, subtype):
    p = E(b"P")
    p.add_string(name)
    p.add_string(b"KString")
    p.add_string(subtype)
    p.add_string(b"")
    p.add_string_unicode(value)
    elem.elems.append(p)


def elem_props_set_string(elem, name, value):
    elem_props_set_string_ex(elem, name, value, b"")


def elem_props_set_string_url(elem, name, value):
    elem_props_set_string_ex(elem, name, value, b"Url")


def elem_props_set_timestamp(elem, name, value):
    p = E(b"P")
    p.add_string(name)
    p.add_string(b"KTime")
    p.add_string(b"Time")
    p.add_string(b"")
    p.add_int64(value)
    elem.elems.append(p)


# Various FBX parts generators.
def fbx_header_elements(root, time=None):
    """
    Write boiling code of FBX root.
    time is expected to be a datetime.datetime object, or None (using now() in this case).
    """
    ##### Start of FBXHeaderExtension element.
    header_ext = E(b"FBXHeaderExtension")

    elem = E(b"FBXHeaderVersion")
    elem.add_int32(FBX_HEADER_VERSION)
    header_ext.elems.append(elem)

    elem = E(b"FBXVersion")
    elem.add_int32(FBX_VERSION)
    header_ext.elems.append(elem)

    # No encryption!
    elem = E(b"EncryptionType")
    elem.add_int32(0)
    header_ext.elems.append(elem)

    if time is None:
        time = datetime.datetime.now()
    elem = E(b"CreationTimeStamp")
    selem = E(b"Version")
    selem.add_int32(1000)
    elem.elems.append(selem)
    selem = E(b"Year")
    selem.add_int32(time.year)
    elem.elems.append(selem)
    selem = E(b"Month")
    selem.add_int32(time.month)
    elem.elems.append(selem)
    selem = E(b"Day")
    selem.add_int32(time.day)
    elem.elems.append(selem)
    selem = E(b"Hour")
    selem.add_int32(time.hour)
    elem.elems.append(selem)
    selem = E(b"Minute")
    selem.add_int32(time.minute)
    elem.elems.append(selem)
    selem = E(b"Second")
    selem.add_int32(time.second)
    elem.elems.append(selem)
    selem = E(b"Millisecond")
    selem.add_int32(time.microsecond * 1000)
    elem.elems.append(selem)
    header_ext.elems.append(elem)

    elem = E(b"Creator")
    elem.add_string_unicode("Blender version %s" % bpy.app.version_string)
    header_ext.elems.append(elem)

    # Skip 'SceneInfo' element for now...

    root.elems.append(header_ext)
    ##### End of FBXHeaderExtension element.

    # FileID is replaced by dummy value currently...
    elem = E(b"FileId")
    elem.add_bytes(b"FooBar")
    root.elems.append(elem)

    # CreationTime is replaced by dummy value currently, but anyway...
    elem = E(b"CreationTime")
    elem.add_string_unicode("{:04}-{:02}-{:02} {:02}:{:02}:{:02}:{:03}"
                            "".format(time.year, time.month, time.day, time.hour, time.minute, time.second,
                                      time.microsecond * 1000))
    root.elems.append(elem)

    elem = E(b"Creator")
    elem.add_string_unicode("Blender version %s" % bpy.app.version_string)
    root.elems.append(elem)

    ##### Start of GlobalSettings element.
    global_settings = E(b"GlobalSettings")

    elem = E(b"Version")
    elem.add_int32(1000)
    global_settings.elems.append(elem)

    props = E(b"Properties70")
    elem_props_set_integer(props, b"UpAxis", 1)
    elem_props_set_integer(props, b"UpAxisSign", 1)
    elem_props_set_integer(props, b"FrontAxis", 2)
    elem_props_set_integer(props, b"FrontAxisSign", 1)
    elem_props_set_integer(props, b"CoordAxis", 0)
    elem_props_set_integer(props, b"CoordAxisSign", 1)
    elem_props_set_number(props, b"UnitScaleFactor", 1.0)
    elem_props_set_color_rgb(props, b"AmbientColor", (0.0, 0.0, 0.0))
    elem_props_set_string(props, b"DefaultCamera", "")
    # XXX Those time stuff is taken from a file, have no (complete) idea what it means!
    elem_props_set_enum(props, b"TimeMode", 11)
    elem_props_set_timestamp(props, b"TimeSpanStart", 0)
    elem_props_set_timestamp(props, b"TimeSpanStop", 479181389250)
    global_settings.elems.append(props)

    root.elems.append(props)
    ##### End of GlobalSettings element.


# This func can be called with just the filepath
def save_single(operator, scene, filepath="",
                global_matrix=None,
                context_objects=None,
                object_types={'EMPTY', 'CAMERA', 'LAMP', 'ARMATURE', 'MESH'},
                use_mesh_modifiers=True,
                mesh_smooth_type='FACE',
                use_armature_deform_only=False,
                use_anim=True,
                use_anim_optimize=True,
                anim_optimize_precision=6,
                use_anim_action_all=False,
                use_metadata=True,
                path_mode='AUTO',
                use_mesh_edges=True,
                use_default_take=True,
                **kwargs
                ):

    import bpy_extras.io_utils

    print('\nFBX export starting... %r' % filepath)
    start_time = time.process_time()

    # Only used for camera and lamp rotations
    mtx_x90 = Matrix.Rotation(math.pi / 2.0, 3, 'X')
    # Used for mesh and armature rotations
    mtx4_z90 = Matrix.Rotation(math.pi / 2.0, 4, 'Z')

    if global_matrix is None:
        global_matrix = Matrix()
        global_scale = 1.0
    else:
        global_scale = global_matrix.median_scale

    # Use this for working out paths relative to the export location
    base_src = os.path.dirname(bpy.data.filepath)
    base_dst = os.path.dirname(filepath)

    # collect images to copy
    copy_set = set()

    root = encode_bin.FBXElem(b"")  # Root element has no id, as it is not saved per se!

    fbx_header_elements(root)
    # Building the whole FBX scene would be here!

    encode_bin.write(filepath, root, 7300)

    # copy all collected files.
    bpy_extras.io_utils.path_reference_copy(copy_set)

    print('export finished in %.4f sec.' % (time.process_time() - start_time))
    return {'FINISHED'}


# defaults for applications, currently only unity but could add others.
def defaults_unity3d():
    return dict(global_matrix=Matrix.Rotation(-math.pi / 2.0, 4, 'X'),
                use_selection=False,
                object_types={'ARMATURE', 'EMPTY', 'MESH'},
                use_mesh_modifiers=True,
                use_armature_deform_only=True,
                use_anim=True,
                use_anim_optimize=False,
                use_anim_action_all=True,
                batch_mode='OFF',
                use_default_take=True,
                )


def save(operator, context,
         filepath="",
         use_selection=False,
         batch_mode='OFF',
         use_batch_own_dir=False,
         **kwargs
         ):
    """
    This is a wrapper around save_single, which handles multi-scenes (or groups) cases, when batch-exporting a whole
    .blend file.
    """

    ret = None

    org_mode = None
    if context.active_object and context.active_object.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
        org_mode = context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

    if batch_mode == 'OFF':
        kwargs_mod = kwargs.copy()
        if use_selection:
            kwargs_mod["context_objects"] = context.selected_objects
        else:
            kwargs_mod["context_objects"] = context.scene.objects

        ret = save_single(operator, context.scene, filepath, **kwargs_mod)
    else:
        fbxpath = filepath

        prefix = os.path.basename(fbxpath)
        if prefix:
            fbxpath = os.path.dirname(fbxpath)

        if batch_mode == 'GROUP':
            data_seq = bpy.data.groups
        else:
            data_seq = bpy.data.scenes

        # call this function within a loop with BATCH_ENABLE == False
        # no scene switching done at the moment.
        # orig_sce = context.scene

        new_fbxpath = fbxpath  # own dir option modifies, we need to keep an original
        for data in data_seq:  # scene or group
            newname = "_".join((prefix, bpy.path.clean_name(data.name)))

            if use_batch_own_dir:
                new_fbxpath = os.path.join(fbxpath, newname)
                # path may already exist
                # TODO - might exist but be a file. unlikely but should probably account for it.

                if not os.path.exists(new_fbxpath):
                    os.makedirs(new_fbxpath)

            filepath = os.path.join(new_fbxpath, newname + '.fbx')

            print('\nBatch exporting %s as...\n\t%r' % (data, filepath))

            if batch_mode == 'GROUP':  # group
                # group, so objects update properly, add a dummy scene.
                scene = bpy.data.scenes.new(name="FBX_Temp")
                scene.layers = [True] * 20
                # bpy.data.scenes.active = scene # XXX, cant switch
                for ob_base in data.objects:
                    scene.objects.link(ob_base)

                scene.update()
                # TODO - BUMMER! Armatures not in the group wont animate the mesh
            else:
                scene = data

            kwargs_batch = kwargs.copy()
            kwargs_batch["context_objects"] = data.objects

            save_single(operator, scene, filepath, **kwargs_batch)

            if batch_mode == 'GROUP':
                # remove temp group scene
                bpy.data.scenes.remove(scene)

        # no active scene changing!
        # bpy.data.scenes.active = orig_sce

        ret = {'FINISHED'}  # so the script wont run after we have batch exported.

    if context.active_object and org_mode and bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=org_mode)

    return ret
