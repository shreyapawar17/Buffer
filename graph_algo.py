import heapq
import networkx as nx

def find_safest_route(graph, start, end):
    pq = [(0, start)]
    safety_scores = {node: float('inf') for node in graph}
    safety_scores[start] = 0
    path = {}

    while pq:
        current_score, current_node = heapq.heappop(pq)

        if current_node == end:
            break

        for neighbor, weight in graph[current_node].items():
            new_score = current_score + weight
            if new_score < safety_scores[neighbor]:
                safety_scores[neighbor] = new_score
                path[neighbor] = current_node
                heapq.heappush(pq, (new_score, neighbor))

    return reconstruct_path(path, start, end)

def reconstruct_path(path, start, end):
    route = []
    while end in path:
        route.append(end)
        end = path[end]
    route.append(start)
    return route[::-1]
