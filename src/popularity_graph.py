import networkx as nx
import data

def init_graph():
    data.popularity_graph = nx.DiGraph()

def update_on_call(call):
    g = data.popularity_graph
    if g is None:
        init_graph()
        g = data.popularity_graph
    caller = call.caller
    callee = call.callee
    duration_seconds = int(call.duration)
    if not g.has_node(caller):
        g.add_node(caller, incoming_count=0, outgoing_count=0, incoming_duration=0, outgoing_duration=0, unique_callers=set(), unique_callees=set())
    if not g.has_node(callee):
        g.add_node(callee, incoming_count=0, outgoing_count=0, incoming_duration=0, outgoing_duration=0, unique_callers=set(), unique_callees=set())
    # Update caller 
    g.nodes[caller]['outgoing_count'] += 1
    g.nodes[caller]['outgoing_duration'] += duration_seconds
    g.nodes[caller]['unique_callees'].add(callee)
    # Update callee 
    g.nodes[callee]['incoming_count'] += 1
    g.nodes[callee]['incoming_duration'] += duration_seconds
    g.nodes[callee]['unique_callers'].add(caller)
    # Add/update edge
    if g.has_edge(caller, callee):
        g[caller][callee]['count'] += 1
        g[caller][callee]['duration'] += duration_seconds
    else:
        g.add_edge(caller, callee, count=1, duration=duration_seconds)

def rebuild_from_calls(calls, blocked_set=None):
    """Rebuild the popularity graph from a list of Call objects, optionally skipping blocked numbers."""
    init_graph()
    g = data.popularity_graph
    for call in calls:
        if blocked_set and (call.caller in blocked_set or call.callee in blocked_set):
            continue
        update_on_call(call)

def get_top_outgoing(n=5):
    g = data.popularity_graph
    if g is None:
        return []
    nodes = g.nodes(data=True)
    sorted_nodes = sorted(nodes, key=lambda x: x[1]['outgoing_count'], reverse=True)
    return sorted_nodes[:n]

def get_top_incoming(n=5):
    g = data.popularity_graph
    if g is None:
        return []
    nodes = g.nodes(data=True)
    sorted_nodes = sorted(nodes, key=lambda x: x[1]['incoming_count'], reverse=True)
    return sorted_nodes[:n]
