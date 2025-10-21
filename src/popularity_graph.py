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

    g.nodes[caller]['outgoing_count'] += 1
    g.nodes[caller]['outgoing_duration'] += duration_seconds
    g.nodes[caller]['unique_callees'].add(callee)

    g.nodes[callee]['incoming_count'] += 1
    g.nodes[callee]['incoming_duration'] += duration_seconds
    g.nodes[callee]['unique_callers'].add(caller)

    if g.has_edge(caller, callee):
        g[caller][callee]['count'] += 1
        g[caller][callee]['duration'] += duration_seconds
    else:
        g.add_edge(caller, callee, count=1, duration=duration_seconds)


def get_popularity_score(number):

    g = data.popularity_graph
    if g is None or not g.has_node(number):
        return 0.0
    
    node_data = g.nodes[number]
    incoming_count = node_data.get('incoming_count', 0)
    incoming_duration = node_data.get('incoming_duration', 0)
    outgoing_count = node_data.get('outgoing_count', 0)
    
    score = (incoming_count * 2.0) + (incoming_duration / 60.0) + (outgoing_count * 0.5)
    return score

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
