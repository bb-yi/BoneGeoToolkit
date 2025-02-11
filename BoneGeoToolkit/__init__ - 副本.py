# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Bonegeotoolkit",
    "author": "SFY",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}
import bpy
import math
from mathutils import Euler, Vector
from bpy.types import GeometryNode
from .utils import tool_functions as ntf


class BoneGeoToolkitBoneSocket(bpy.types.NodeSocket):
    """示例自定义插槽类型"""

    bl_idname = "BoneSocketType"
    bl_label = "Bone Socket"
    bl_color = (0.32, 1, 0.48, 1.0)  # 插槽颜色

    # 定义多个属性
    armature: bpy.props.PointerProperty(name="Armature", type=bpy.types.Object)
    bone_name: bpy.props.StringProperty(name="Bone Name", default="")

    def draw(self, context, layout, node, text):
        """绘制插槽"""
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            col = layout.column(align=True)
            # 添加第一个属性到列中
            col.prop(self, "armature", text="Armature", icon="ARMATURE_DATA")
            # 添加第二个属性到列中
            col.prop(self, "bone_name", text="Bone Name", icon="BONE_DATA")

    def draw_color(self, context, node):
        """定义插槽颜色"""
        return self.bl_color


class test_node(bpy.types.Node):
    bl_idname = "CustomNodeTypetest_node"
    bl_label = "Test Node"
    bl_icon = "SETTINGS"

    test_float: bpy.props.FloatProperty(name="Test Float", default=1.0, update=lambda self, context: self.update_sockets())
    test_int: bpy.props.IntProperty(name="Test Int", default=1)
    test_bool: bpy.props.BoolProperty(name="Test Bool", default=True)
    test_string: bpy.props.StringProperty(name="Test String", default="Hello World")
    test_enum: bpy.props.EnumProperty(
        name="Test Enum",
        items=[
            ("ITEM1", "Item 1", "Item 1 description"),
            ("ITEM2", "Item 2", "Item 2 description"),
            ("ITEM3", "Item 3", "Item 3 description"),
        ],
        default="ITEM1",
    )
    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)

    def init(self, context):
        self.outputs.new("NodeSocketFloat", "Float Output")
        self.outputs.new("NodeSocketInt", "Int Output")
        self.outputs.new("NodeSocketBool", "Bool Output")
        self.outputs.new("NodeSocketString", "String Output")
        self.inputs.new("NodeSocketFloat", "Float Input")
        self.inputs.new("NodeSocketInt", "整数输入11")

    def draw_buttons(self, context, layout):
        layout.operator("mynode.test_operator", text="Test Button")
        layout.prop(self, "test_float")
        layout.prop(self, "test_int")
        layout.prop(self, "test_bool")
        layout.prop(self, "test_string")
        layout.prop(self, "test_enum")
        layout.prop(self, "object")

    def draw_label(self):
        return "Test Node"

    def update_sockets(self):
        print("sockets updated")

    def update(self):
        output_sockets = self.outputs.get("Float Output")
        if output_sockets is not None and output_sockets.is_linked:
            for link in output_sockets.links:
                if link.is_valid:
                    socket = link.to_socket
                    print(socket.type)
                    if socket.type == "VALUE":
                        socket.default_value = self.test_float
                    elif socket.type == "INT":
                        socket.default_value = int(self.test_float)
                    elif socket.type == "BOOLEAN":
                        socket.default_value = self.test_float >= 1


class GeometryNodeCustom(bpy.types.GeometryNodeCustomGroup):
    bl_idname = "GeometryNodeCustom"
    bl_label = "Custom Geometry Node"

    @classmethod
    def poll(cls, context):  # mandatory with geonode
        return True

    def init(self, context):
        name = f".{self.bl_idname}"
        if name not in bpy.data.node_groups.keys():
            ng = bpy.data.node_groups.new(name=name, type="GeometryNodeTree")
            in_node = ng.nodes.new("NodeGroupInput")
            in_node.location.x -= 200
            out_node = ng.nodes.new("NodeGroupOutput")
            out_node.location.x += 200
            sockets = {
                "Camera Object": "NodeSocketObject",
                "Field of View": "NodeSocketFloat",
                "Shift X": "NodeSocketFloat",
                "Shift Y": "NodeSocketFloat",
                "Clip Start": "NodeSocketFloat",
                "Clip End": "NodeSocketFloat",
                "Resolution X": "NodeSocketInt",
                "Resolution Y": "NodeSocketInt",
            }
            # socket = ng.interface.new_socket(name="test", socket_type="NodeSocketFloat", in_out="OUTPUT")
            # socket = ng.interface.new_socket(name="test1111", socket_type="NodeSocketFloat", in_out="INPUT")

            for socket_name, socket_type in sockets.items():
                socket = ng.interface.new_socket(name=socket_name, socket_type=socket_type, in_out="OUTPUT")
        else:
            ng = bpy.data.node_groups[name].copy()
        self.node_tree = ng
        self.label = self.bl_label

    def update(self):
        pass

    def draw_buttons(self, context, layout):
        """node interface drawing"""
        layout.label(text="Custom Geometry Node")

        return None


class BoneGeoToolkit_Bone_input_node(bpy.types.Node):
    bl_idname = "BoneInputNode"
    bl_label = "Bone Input Node"
    bl_icon = "BLANK1"

    def init(self, context):
        self.inputs.new("NodeSocketObject", "Object")
        self.inputs.new("NodeSocketString", "Bone Name")
        self.outputs.new("BoneSocketType", "Bone")

    def draw_buttons(self, context, layout):
        # # 检查值是否变化
        # if self.inputs[0].default_value != getattr(self, "_last_value", 0):
        #     print("输入值变化！")
        pass

    def draw_label(self):
        return "Bone Input Node"

    def update(self):
        # print("Bone Input Node update")
        output_sockets = self.outputs.get("Bone")
        if output_sockets is not None and output_sockets.is_linked:
            for link in output_sockets.links:
                if link.is_valid:
                    socket = link.to_socket
                    socket.armature = self.inputs[0].default_value
                    socket.bone_name = self.inputs[1].default_value


class BoneGeoToolkit_BoneInfoNode(bpy.types.Node):
    bl_idname = "CustomBoneInfoNode"
    bl_label = "Custom Bone Info Node"
    bl_icon = "BLANK1"
    bl_width_default = 150
    bl_height_default = 100

    obj: bpy.props.PointerProperty(name="Object", type=bpy.types.Object)
    bone_name: bpy.props.StringProperty(name="Bone Name", default="")

    def init(self, context):
        self.outputs.new("NodeSocketVector", "Head Location")
        self.outputs.new("NodeSocketVector", "Tail Location")
        self.outputs.new("NodeSocketVector", "Rotation")
        self.outputs.new("NodeSocketVector", "Scale")
        # self.inputs.new("NodeSocketObject", "Object")
        # self.inputs.new("NodeSocketString", "Bone Name")
        self.inputs.new("BoneSocketType", "Bone")

    def draw_buttons(self, context, layout):
        # layout.prop(self, "obj")
        # layout.prop(self, "bone_name")
        pass

    def draw_label(self):
        return "Bone Info Node"

    def update(self):

        # self.obj = self.inputs["Object"].default_value
        # self.bone_name = self.inputs["Bone Name"].default_value

        self.obj = self.inputs["Bone"].armature
        self.bone_name = self.inputs["Bone"].bone_name
        if not self.obj:
            return
        if not self.obj.pose or self.bone_name is None:
            return
        if self.bone_name not in self.obj.pose.bones:
            return
        output_sockets = self.outputs.get("Head Location")
        if output_sockets is not None and output_sockets.is_linked:
            for link in output_sockets.links:
                if link.is_valid:
                    socket = link.to_socket
                    bone = self.obj.pose.bones[self.bone_name]
                    socket.default_value = bone.head
        output_sockets = self.outputs.get("Tail Location")
        if output_sockets is not None and output_sockets.is_linked:
            for link in output_sockets.links:
                if link.is_valid:
                    socket = link.to_socket
                    bone = self.obj.pose.bones[self.bone_name]
                    socket.default_value = bone.tail

        output_sockets = self.outputs.get("Rotation")
        if output_sockets is not None and output_sockets.is_linked:
            for link in output_sockets.links:
                if link.is_valid:
                    socket = link.to_socket
                    bone = self.obj.pose.bones[self.bone_name]
                    euler = bone.matrix.to_quaternion().to_euler("XYZ")
                    euler_list = [euler.x, euler.y, euler.z]
                    adjusted_euler_list = [euler_list[0] - math.pi / 2, euler_list[1], euler_list[2]]
                    socket.default_value = Euler(adjusted_euler_list, "XYZ")
        output_sockets = self.outputs.get("Scale")
        if output_sockets is not None and output_sockets.is_linked:
            for link in output_sockets.links:
                if link.is_valid:
                    socket = link.to_socket
                    bone = self.obj.pose.bones[self.bone_name]
                    socket.default_value = bone.scale.copy()


class BoneGeoToolkit_update_handlers_manager(bpy.types.Node):
    bl_idname = "BoneGeoToolkit_update_handlers_manager"
    bl_label = "update handlers manager"
    bl_icon = "TOOL_SETTINGS"
    bl_width_default = 300
    bl_height_default = 100

    def init(self, context):
        pass

    def draw_buttons(self, context, layout):
        layout.operator(updata_test_operator.bl_idname, text="更新节点数据")
        row = layout.row()
        row.operator(add_depsgraph_update_pre_handler_operator.bl_idname, text="添加depsgraph_update_pre")
        row.operator(remove_depsgraph_update_pre_handler_operator.bl_idname, text="移除depsgraph_update_pre")
        row2 = layout.row()
        row2.operator(add_depsgraph_update_post_handler_operator.bl_idname, text="添加depsgraph_update_post")
        row2.operator(remove_depsgraph_update_post_handler_operator.bl_idname, text="移除depsgraph_update_post")
        row3 = layout.row()
        row3.operator(add_frame_change_pre_handler_operator.bl_idname, text="添加frame_change_pre")
        row3.operator(remove_frame_change_pre_handler_operator.bl_idname, text="移除frame_change_pre")
        row4 = layout.row()
        row4.operator(add_frame_change_post_handler_operator.bl_idname, text="添加frame_change_post")
        row4.operator(remove_frame_change_post_handler_operator.bl_idname, text="移除frame_change_post")

    def draw_label(self):
        return "Update Handlers Manager"


class BoneGeoToolkit_transform_bone_node(bpy.types.Node):
    bl_idname = "TransformBoneNode"
    bl_label = "Transform Bone Node"
    bl_icon = "BLANK1"

    def init(self, context):
        self.inputs.new("NodeSocketGeometry", "Geometry Input")
        self.outputs.new("NodeSocketGeometry", "Geometry Output")
        self.inputs.new("BoneSocketType", "Bone")
        self.inputs.new("NodeSocketVector", "Location")
        self.inputs.new("NodeSocketVector", "Rotation")
        scale_socket = self.inputs.new("NodeSocketVector", "Scale")
        scale_socket.default_value = (1.0, 1.0, 1.0)  # 默认缩放为 1 倍
        self.outputs.new("BoneSocketType", "Bone")
        pass

    def draw_buttons(self, context, layout):
        pass

    def draw_label(self):
        return "Transform Bone Node"

    def update(self):
        # """当输入或输出发生变化时调用此方法"""
        # # 获取输入插槽的几何数据
        # input_socket = self.inputs["Geometry Input"]
        # if input_socket.is_linked:
        #     # 如果输入插槽已连接，获取连接的几何数据
        #     input_geometry = input_socket.links[0].from_socket.default_value
        #     # 设置输出插槽的几何数据
        #     self.outputs["Geometry Output"].default_value = input_geometry
        # else:
        #     # 如果输入插槽未连接，可以设置一个默认值或清空输出
        #     self.outputs["Geometry Output"].default_value = None

        armature = self.inputs["Bone"].armature
        bone_name = self.inputs["Bone"].bone_name
        if not armature or not bone_name:
            return
        if bone_name not in armature.pose.bones:
            return
        bone = armature.pose.bones[bone_name]
        location = self.inputs["Location"].default_value
        rotation = self.inputs["Rotation"].default_value
        scale = self.inputs["Scale"].default_value
        bone.location = location
        bone.rotation_euler = rotation
        bone.scale = scale
        output_sockets = self.outputs.get("Bone")
        if output_sockets is not None and output_sockets.is_linked:
            for link in output_sockets.links:
                if link.is_valid:
                    socket = link.to_socket
                    socket.armature = armature
                    socket.bone_name = bone_name


def BoneGeoToolkit_update_handler(scene):
    # 在这里添加操作符的逻辑
    for tree in bpy.data.node_groups:
        for node in tree.nodes:
            if isinstance(node, BoneGeoToolkit_BoneInfoNode):
                # 手动调用节点的 update 方法
                node.update()
            if isinstance(node, BoneGeoToolkit_Bone_input_node):
                node.update()


class updata_test_operator(bpy.types.Operator):
    bl_idname = "mynode.updata_test_operator"
    bl_label = "updata_test_operator"
    bl_description = "updata_test_operator"

    def execute(self, context):
        BoneGeoToolkit_update_handler(bpy.context.scene)
        self.report({"INFO"}, "updata_test_operator executed!")
        return {"FINISHED"}


class add_depsgraph_update_pre_handler_operator(bpy.types.Operator):
    bl_idname = "mynode.add_depsgraph_update_pre_handler"
    bl_label = "add_depsgraph_update_pre_handler"
    bl_description = "add_depsgraph_update_pre_handler"

    def execute(self, context):
        target_handler = BoneGeoToolkit_update_handler
        if not (target_handler in bpy.app.handlers.depsgraph_update_pre):
            bpy.app.handlers.depsgraph_update_pre.append(target_handler)
        self.report({"INFO"}, "添加depsgraph_update_pre")
        return {"FINISHED"}


class remove_depsgraph_update_pre_handler_operator(bpy.types.Operator):
    bl_idname = "mynode.remove_depsgraph_update_pre_handler"
    bl_label = "remove_depsgraph_update_pre_handler"
    bl_description = "remove_depsgraph_update_pre_handler"

    def execute(self, context):
        for handler in bpy.app.handlers.depsgraph_update_pre:
            target_handler = BoneGeoToolkit_update_handler
            if handler == target_handler:
                bpy.app.handlers.depsgraph_update_pre.remove(target_handler)
                self.report({"INFO"}, "已移除depsgraph_update_pre")
            else:
                self.report({"INFO"}, "不存在depsgraph_update_pre")
        return {"FINISHED"}


class add_depsgraph_update_post_handler_operator(bpy.types.Operator):
    bl_idname = "mynode.add_depsgraph_update_post_handler"
    bl_label = "add_depsgraph_update_post_handler"
    bl_description = "add_depsgraph_update_post_handler"

    def execute(self, context):
        target_handler = BoneGeoToolkit_update_handler
        if not (target_handler in bpy.app.handlers.depsgraph_update_post):
            bpy.app.handlers.depsgraph_update_post.append(target_handler)
        self.report({"INFO"}, "添加depsgraph_update_post")
        return {"FINISHED"}


class remove_depsgraph_update_post_handler_operator(bpy.types.Operator):
    bl_idname = "mynode.remove_depsgraph_update_post_handler"
    bl_label = "remove_depsgraph_update_post_handler"
    bl_description = "remove_depsgraph_update_post_handler"

    def execute(self, context):
        target_handler = BoneGeoToolkit_update_handler
        for handler in bpy.app.handlers.depsgraph_update_post:
            if handler == target_handler:
                bpy.app.handlers.depsgraph_update_post.remove(target_handler)
                self.report({"INFO"}, "已移除depsgraph_update_post")
            else:
                self.report({"INFO"}, "不存在depsgraph_update_post")
        return {"FINISHED"}


class add_frame_change_post_handler_operator(bpy.types.Operator):
    bl_idname = "mynode.add_frame_change_post_handler"
    bl_label = "add_frame_change_post_handler"
    bl_description = "add_frame_change_post_handler"

    def execute(self, context):
        target_handler = BoneGeoToolkit_update_handler
        if not (target_handler in bpy.app.handlers.frame_change_post):
            bpy.app.handlers.frame_change_post.append(target_handler)
        self.report({"INFO"}, "添加frame_change_post")
        return {"FINISHED"}


class remove_frame_change_post_handler_operator(bpy.types.Operator):
    bl_idname = "mynode.remove_frame_change_post_handler"
    bl_label = "remove_frame_change_post_handler"
    bl_description = "remove_frame_change_post_handler"

    def execute(self, context):
        target_handler = BoneGeoToolkit_update_handler
        for handler in bpy.app.handlers.frame_change_post:
            if handler == target_handler:
                bpy.app.handlers.frame_change_post.remove(target_handler)
                self.report({"INFO"}, "已移除frame_change_post")
            else:
                self.report({"INFO"}, "不存在frame_change_post")
        return {"FINISHED"}


class add_frame_change_pre_handler_operator(bpy.types.Operator):
    bl_idname = "mynode.add_frame_change_pre_handler"
    bl_label = "add_frame_change_pre_handler"
    bl_description = "add_frame_change_pre_handler"

    def execute(self, context):
        target_handler = BoneGeoToolkit_update_handler
        if not (target_handler in bpy.app.handlers.frame_change_pre):
            bpy.app.handlers.frame_change_pre.append(target_handler)
        self.report({"INFO"}, "添加frame_change_pre")
        return {"FINISHED"}


class remove_frame_change_pre_handler_operator(bpy.types.Operator):
    bl_idname = "mynode.remove_frame_change_pre_handler"
    bl_label = "remove_frame_change_pre_handler"
    bl_description = "remove_frame_change_pre_handler"

    def execute(self, context):
        target_handler = BoneGeoToolkit_update_handler
        for handler in bpy.app.handlers.frame_change_pre:
            if handler == target_handler:
                bpy.app.handlers.frame_change_pre.remove(target_handler)
                self.report({"INFO"}, "已移除frame_change_pre")
            else:
                self.report({"INFO"}, "不存在frame_change_pre")
        return {"FINISHED"}


def Add_to_Node_Menu(self, context):
    if context.area.type == "NODE_EDITOR" and context.space_data.tree_type == "GeometryNodeTree":
        layout = self.layout
        layout.menu("SNA_MT_GEO_NODE_test_Menu", text="Bone Tools", icon="BONE_DATA")


nodes = [
    GeometryNodeCustom,
    BoneGeoToolkit_update_handlers_manager,
    test_node,
    BoneGeoToolkit_Bone_input_node,
    BoneGeoToolkit_BoneInfoNode,
    BoneGeoToolkit_transform_bone_node,
]


class SNA_MT_GEO_NODE_test_Menu(bpy.types.Menu):
    bl_idname = "SNA_MT_GEO_NODE_test_Menu"
    bl_label = "test_menu"

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.column_flow(columns=1)
        layout.operator_context = "INVOKE_DEFAULT"
        for temp_node in nodes:
            if hasattr(temp_node, "bl_icon"):
                icon = temp_node.bl_icon
            else:
                icon = "BLANK1"  # 替换为默认图标名称
            # 添加一个节点
            node = layout.operator("node.add_node", text=temp_node.bl_label, icon=icon)
            node.type = temp_node.bl_idname
            node.use_transform = True


operators = [
    updata_test_operator,
    add_depsgraph_update_pre_handler_operator,
    remove_depsgraph_update_pre_handler_operator,
    add_depsgraph_update_post_handler_operator,
    remove_depsgraph_update_post_handler_operator,
    add_frame_change_post_handler_operator,
    remove_frame_change_post_handler_operator,
    add_frame_change_pre_handler_operator,
    remove_frame_change_pre_handler_operator,
]


# 注册函数
def register():
    bpy.utils.register_class(BoneGeoToolkitBoneSocket)
    for operator in operators:
        bpy.utils.register_class(operator)

    for node in nodes:
        bpy.utils.register_class(node)
    # 注册自定义节点
    bpy.utils.register_class(SNA_MT_GEO_NODE_test_Menu)
    bpy.types.NODE_MT_add.append(Add_to_Node_Menu)


# 注销函数
def unregister():
    bpy.utils.unregister_class(BoneGeoToolkitBoneSocket)
    for operator in operators:
        bpy.utils.unregister_class(operator)

    for node in nodes:
        bpy.utils.unregister_class(node)
    bpy.utils.unregister_class(SNA_MT_GEO_NODE_test_Menu)
    bpy.types.NODE_MT_add.remove(Add_to_Node_Menu)


if __name__ == "__main__":
    register()
