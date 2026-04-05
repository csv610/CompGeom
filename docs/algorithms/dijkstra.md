# Dijkstra's Algorithm (Shortest Paths)

## 1. Overview
Dijkstra's algorithm is a fundamental graph-search algorithm that finds the shortest paths between nodes in a graph. For a given source node, the algorithm finds the shortest distance to every other node. It is the discrete equivalent of the Fast Marching Method and serves as the backbone of modern navigation and network routing systems.

## 2. Definitions
*   **Graph ($G$)**: A collection of vertices $V$ connected by weighted edges $E$.
*   **Weight ($w$)**: A value associated with an edge representing distance, cost, or time. Weights must be non-negative.
*   **Source ($S$)**: The starting node from which distances are calculated.
*   **Priority Queue**: A data structure that stores nodes and their current best distances, allowing for efficient retrieval of the "nearest" node.

## 3. Theory
The algorithm operates by maintaining a set of "visited" nodes and a set of "unvisited" nodes. Initially, the distance to the source is 0, and the distance to all other nodes is infinity. In each step, the algorithm:
1.  Selects the unvisited node with the smallest known distance.
2.  "Relaxes" all of its neighbors: for each neighbor, it checks if going through the current node provides a shorter path than the previously known best path.
3.  Marks the current node as visited.

This greedy strategy works because the weights are non-negative; once a node is visited, its distance is guaranteed to be the shortest possible.

## 4. Pseudo code
```python
function Dijkstra(graph, source):
    # 1. Initialize
    distances = {v: infinity for v in graph.vertices}
    previous = {v: None for v in graph.vertices}
    distances[source] = 0
    
    pq = PriorityQueue()
    pq.push(source, 0)
    
    # 2. Main Loop
    while not pq.empty():
        # Get the node with the minimum distance
        u, dist_u = pq.pop_min()
        
        # If we found a longer path than already known, skip
        if dist_u > distances[u]: continue
        
        # 3. Relaxation
        for v, weight in graph.neighbors(u):
            new_dist = distances[u] + weight
            
            if new_dist < distances[v]:
                distances[v] = new_dist
                previous[v] = u
                pq.push(v, new_dist)
                
    return distances, previous
```

## 5. Parameters Selections
*   **Data Structure**: Using a **Fibonacci Heap** or **Binary Heap** for the priority queue is critical for performance. Binary heaps are most common in practice.
*   **Edge Weights**: If any edge weight is negative, the algorithm fails; the Bellman-Ford algorithm should be used instead.

## 6. Complexity
*   **Time Complexity**: $O((E + V) \log V)$ with a binary heap, where $V$ is the number of vertices and $E$ is the number of edges. $O(E + V \log V)$ with a Fibonacci heap.
*   **Space Complexity**: $O(V + E)$ to store the graph and the distance arrays.

## 7. Usages
*   **GPS Navigation**: Finding the fastest route between two locations.
*   **Network Routing**: Protocols like OSPF (Open Shortest Path First) use Dijkstra to route data packets across the internet.
*   **Social Networks**: Finding "degrees of separation" between people.
*   **Robotics**: Pathfinding for autonomous vehicles on a roadmap.
*   **Game Development**: AI movement (often using A*, which is a heuristic-based extension of Dijkstra).

## 8. Testing methods and Edge cases
*   **Disconnected Graphs**: Nodes that cannot be reached from the source should maintain a distance of infinity.
*   **Single-Node Graph**: Distance to itself is 0.
*   **Parallel Edges**: The algorithm should always select the edge with the minimum weight between two nodes.
*   **Cycles**: Dijkstra correctly handles cycles as long as all weights are non-negative.
*   **Path Reconstruction**: Ensure the `previous` pointers correctly trace the full path back to the source.

## 9. References
*   Dijkstra, E. W. (1959). "A note on two problems in connexion with graphs". Numerische Mathematik.
*   Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). "Introduction to Algorithms". MIT Press.
*   [Wikipedia: Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
