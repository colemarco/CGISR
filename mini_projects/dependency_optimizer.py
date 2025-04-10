from collections import defaultdict, deque
from typing import List, Dict, Tuple, Set
import graphviz


class RenderPass:
    def __init__(self, name: str, queue: int, dependencies: List[str]):
        self.name = name
        self.queue = queue
        self.dependencies = dependencies
        self.ssis = defaultdict(int)


class RenderGraph:
    def __init__(self, passes: List[RenderPass], num_queues: int):
        self.passes = {p.name: p for p in passes}
        self.graph = defaultdict(list)
        self.in_degree = defaultdict(int)
        self.num_queues = num_queues
        self.order = []
        self.levels = {}
        self._build()

    def _build(self):
        for p in self.passes.values():
            for dep in p.dependencies:
                self.graph[dep].append(p.name)
                self.in_degree[p.name] += 1

    def topological_sort(self):
        queue = deque([name for name in self.passes if self.in_degree[name] == 0])
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in self.graph[node]:
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)
        if len(order) != len(self.passes):
            raise ValueError("Graph has cycles!")
        self.order = order

    def compute_levels(self):
        def dfs(node: str) -> int:
            if node in self.levels:
                return self.levels[node]
            level = 0
            for dep in self.passes[node].dependencies:
                level = max(level, dfs(dep) + 1)
            self.levels[node] = level
            return level

        for name in self.passes:
            dfs(name)

    def compute_ssis(self):
        for name in self.order:
            p = self.passes[name]
            ssis = [0] * self.num_queues
            for dep_name in p.dependencies:
                dep = self.passes[dep_name]
                for q in range(self.num_queues):
                    if q == p.queue:
                        ssis[q] = max(ssis[q], dep.ssis[q] + 1)
                    else:
                        ssis[q] = max(ssis[q], dep.ssis[q])
            p.ssis = {q: ssis[q] for q in range(self.num_queues)}

    def greedy_sync_selection(self, name: str):
        p = self.passes[name]
        R = set(q for q in range(self.num_queues) if q != p.queue and p.ssis[q] > 0)
        D = [self.passes[d] for d in p.dependencies]
        syncs = []

        while R:
            best = None
            best_coverage = set()
            for u in D:
                coverage = set()
                for q in R:
                    if u.ssis[q] >= p.ssis[q]:
                        coverage.add(q)
                if len(coverage) > len(best_coverage):
                    best = u
                    best_coverage = coverage
            if best:
                syncs.append(best.name)
                R -= best_coverage
                D.remove(best)
            else:
                break
        return syncs

    def optimized_execution(self):
        self.topological_sort()
        self.compute_levels()
        self.compute_ssis()

        # Sort based on level and queue (greedy optimization potential)
        return sorted(self.order, key=lambda x: (self.levels[x], self.passes[x].queue))

    def visualize(self, filename="render_graph"):
        dot = graphviz.Digraph(comment="Render Graph")
        for name, p in self.passes.items():
            label = f"{name}\nQ{p.queue}"
            dot.node(name, label)
        for p in self.passes.values():
            for dep in p.dependencies:
                dot.edge(dep, p.name)
        dot.render(filename, format="png", cleanup=True)
        print(f"Graph saved to {filename}.png")


# Example usage
if __name__ == "__main__":
    render_passes = [
        RenderPass("GBuffer", 0, []),
        RenderPass("ShadowMap", 1, []),
        RenderPass("DepthPrepass", 0, []),
        RenderPass("AmbientOcclusion", 2, ["GBuffer", "DepthPrepass"]),
        RenderPass("Reflections", 2, ["GBuffer", "DepthPrepass"]),
        RenderPass("Lighting", 0, ["GBuffer", "ShadowMap", "AmbientOcclusion"]),
        RenderPass("SSR", 2, ["Reflections", "Lighting"]),
        RenderPass("Bloom", 0, ["Lighting"]),
        RenderPass("ToneMapping", 0, ["Bloom", "SSR"]),
        RenderPass("UI", 1, ["ToneMapping"]),
        RenderPass("PostFX", 1, ["ToneMapping"]),
        RenderPass("FinalBlit", 0, ["PostFX", "UI"]),
    ]

    rg = RenderGraph(render_passes, num_queues=3)
    order = rg.optimized_execution()

    print("Execution Order:")
    for name in order:
        print(f"{name} (Queue {rg.passes[name].queue})")

    print("\nRecommended Synchronizations:")
    for name in order:
        syncs = rg.greedy_sync_selection(name)
        if syncs:
            print(f"{name} should sync with: {', '.join(syncs)}")

    rg.visualize("render_graph_output")
