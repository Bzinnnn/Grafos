from collections import defaultdict, deque

class MaxFlow:
    def __init__(self, n):
        self.size = n
        self.graph = defaultdict(list)
        self.capacity = {}

    def add_edge(self, u, v, w):
        self.graph[u].append(v)
        self.graph[v].append(u)
        self.capacity[(u, v)] = w
        self.capacity[(v, u)] = 0

    def bfs(self, source, sink, parent):
        visited = [False] * self.size
        queue = deque([source])
        visited[source] = True

        while queue:
            u = queue.popleft()
            for v in self.graph[u]:
                if not visited[v] and self.capacity[(u, v)] > 0:
                    parent[v] = u
                    visited[v] = True
                    if v == sink:
                        return True
                    queue.append(v)
        return False

    def edmonds_karp(self, source, sink):
        parent = [-1] * self.size
        max_flow = 0
        flow_paths = []

        while self.bfs(source, sink, parent):
            path_flow = float('Inf')
            s = sink
            path = []
            while s != source:
                path_flow = min(path_flow, self.capacity[(parent[s], s)])
                path.append(s)
                s = parent[s]
            path.append(source)
            path.reverse()
            flow_paths.append(path)

            v = sink
            while v != source:
                u = parent[v]
                self.capacity[(u, v)] -= path_flow
                self.capacity[(v, u)] += path_flow
                v = parent[v]

            max_flow += path_flow

        return max_flow, flow_paths

def can_schedule_doctors(n, k, c, periods, availability):
    # Número de nós: source (0) + sink (1) + médicos (n) + dias de férias (sum of length of periods) + períodos (k)
    num_days = sum(len(Dj) for Dj in periods)
    num_nodes = 2 + n + num_days + k
    source = 0
    sink = 1
    offset_doctors = 2
    offset_days = 2 + n
    offset_periods = 2 + n + num_days

    maxflow = MaxFlow(num_nodes)

    # Conectar source aos médicos
    for i in range(n):
        maxflow.add_edge(source, offset_doctors + i, c)

    day_counter = 0
    period_node_map = {}
    day_node_map = {}

    # Conectar médicos aos dias e criar nós intermediários de períodos
    for j, Dj in enumerate(periods):
        period_node = offset_periods + j
        period_node_map[j] = period_node
        for day in Dj:
            day_node = offset_days + day_counter
            day_node_map[day] = day_node
            day_counter += 1
            # Conectar nó do período a cada dia do período
            maxflow.add_edge(period_node, day_node, 1)

            for i in range(n):
                if day in availability[i]:
                    maxflow.add_edge(offset_doctors + i, day_node, 1)

            # Conectar dias ao sink
            maxflow.add_edge(day_node, sink, 1)

    # Verificar se o fluxo máximo é igual ao número de dias
    total_days = day_counter
    max_flow, flow_paths = maxflow.edmonds_karp(source, sink)

    if max_flow != total_days:
        return False, {}

    # Atribuir médicos aos dias com base nos caminhos de fluxo
    doctor_assignments = defaultdict(list)
    for path in flow_paths:
        for i in range(1, len(path) - 1):
            u = path[i]
            v = path[i + 1]
            if source < u < offset_days and offset_days <= v < offset_days + total_days:
                doctor_idx = u - offset_doctors + 1  # Ajustar para começar em 1
                day_idx = [day for day, node in day_node_map.items() if node == v][0] + 1  # Ajustar para começar em 1
                doctor_assignments[doctor_idx].append(day_idx)

    return True, doctor_assignments

# Coleta de dados
n = int(input("Número de médicos: "))
k = int(input("Número de períodos de férias: "))
c = int(input("Máximo de dias de feriado que um médico pode trabalhar no total: "))

periods = []
print("Informe os períodos de férias (ex: para 3 dias, insira 1 2 3):")
for j in range(k):
    period = list(map(int, input(f"Período {j + 1}: ").split()))
    periods.append([day - 1 for day in period])  # Ajustar para começar em 0 internamente

availability = []
print("Informe a disponibilidade dos médicos (ex: para os dias 1 e 2, insira 1 2):")
for i in range(n):
    available_days = list(map(int, input(f"Médico {i + 1}: ").split()))
    availability.append(set(day - 1 for day in available_days))  # Ajustar para começar em 0 internamente

can_schedule, assignments = can_schedule_doctors(n, k, c, periods, availability)
if can_schedule:
    print("É possível agendar os médicos. As atribuições são:")
    for doctor, days in assignments.items():
        print(f"Médico {doctor}: Dias {days}")
else:
    print("Não é possível agendar os médicos.")
