import bpy


def get_socket_value(ng, idx):
    return ng.nodes["Group Output"].inputs[idx].default_value


def set_socket_value(ng, idx, value=None):
    ng.nodes["Group Output"].inputs[idx].default_value = value
    return ng.nodes["Group Output"].inputs[idx].default_value


def set_socket_label(ng, idx, label=None):
    ng.outputs[idx].name = str(label)
    return None


def get_socket_type(ng, idx):
    return ng.outputs[idx].type


def set_socket_type(ng, idx, socket_type="NodeSocketFloat"):
    """set socket type via bpy.ops.node.tree_socket_change_type() with manual override, context MUST be the geometry node editor"""

    snode = bpy.context.space_data
    if snode is None:
        return None

    # forced to do a ugly override like this... eww
    restore_override = {"node_tree": snode.node_tree, "pin": snode.pin}
    snode.pin = True
    snode.node_tree = ng
    ng.active_output = idx
    bpy.ops.node.tree_socket_change_type(in_out="OUT", socket_type=socket_type)  # operator override is best, but which element do we need to override, not sure what the cpp operator need..

    # then restore... all this will may some signal to depsgraph
    for api, obj in restore_override.items():
        setattr(snode, api, obj)

    return None


def create_socket(ng, socket_type="NodeSocketFloat", socket_name="Value"):
    socket = ng.outputs.new(socket_type, socket_name)
    return socket


def remove_socket(ng, idx):
    todel = ng.outputs[idx]
    ng.outputs.remove(todel)
    return None


def create_new_nodegroup(name, sockets={}):
    """create new nodegroup with outputs from given dict {"name":"type",}, make sure given type are correct"""

    ng = bpy.data.node_groups.new(name=name, type="GeometryNodeTree")
    in_node = ng.nodes.new("NodeGroupInput")
    in_node.location.x -= 200
    out_node = ng.nodes.new("NodeGroupOutput")
    out_node.location.x += 200

    for socket_name, socket_type in sockets.items():
        create_socket(ng, socket_type=socket_type, socket_name=socket_name)

    return ng
