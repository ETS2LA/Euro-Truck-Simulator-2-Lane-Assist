import Plugins.Map.data as data
import logging

def get_path_to_destination():
    """Find a path from current position to destination"""
    
    route = data.plugin.modules.Route.run()
    if len(route) != len(data.navigation_plan):
        nodes = []
        first = route[0]
        for item in route:
            try:
                node = data.map.get_node_by_uid(item.uid)
                if node:
                    nodes.append(node)
            except Exception:
                pass
            
        logging.warning(f"Found a route with {len(nodes)} nodes, it's {first.distance / 1000 :.1f} km long and will take {first.time / 60 :.1f} min (in game) to complete")
        return nodes
    
    return data.navigation_plan