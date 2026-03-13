#!/usr/bin/env python3
"""Deadlock Detection and Recovery System using RAG/WFG.
Uses only standard Python libraries. Menu-driven console app."""

class Process:
    def __init__(self, pid):
        self.pid = pid
        self.active = True
        self.allocated = []  # list of res ids held

    def __str__(self):
        status = 'Active' if self.active else 'Terminated'
        return f'P{self.pid} ({status}, holds: {self.allocated})'

class SystemState:
    def __init__(self, n_proc, n_res):
        self.n_proc = n_proc
        self.n_res = n_res
        self.processes = [Process(i) for i in range(n_proc)]
        self.allocation = [[0] * n_res for _ in range(n_proc)]  # alloc[p][r] = 1 if held
        self.request = [[0] * n_res for _ in range(n_proc)]     # req[p][r] = 1 if wants
        self.available = [0] * n_res                           # avail[r]
        self.rag = {}  # res -> holders, proc_alloc, proc_req
        self.wfg = {}  # pid -> waiting pids

    def print_matrices(self):
        print("\n=== ALLOCATION MATRIX (P x R) ===")
        for p in range(self.n_proc):
            print(f'P{p}: {self.allocation[p]}')
        print("\n=== REQUEST MATRIX (P x R) ===")
        for p in range(self.n_proc):
            print(f'P{p}: {self.request[p]}')
        print(f"\n=== AVAILABLE: {self.available}")

def input_matrices(state):
    """Interactive input for matrices."""
    print(f"Enter data for {state.n_proc} processes, {state.n_res} resources.")
    
    # Allocation
    print("\nAllocation Matrix (row by row, space sep 0/1):")
    for p in range(state.n_proc):
        row = list(map(int, input(f'Row P{p}: ').split()))
        state.allocation[p] = row
    
    # Request
    print("\nRequest Matrix:")
    for p in range(state.n_proc):
        row = list(map(int, input(f'Row P{p}: ').split()))
        state.request[p] = row
    
    # Available
    state.available = list(map(int, input('Available vector: ').split()))

def build_rag(state):
    """Build RAG: update proc.allocated, rag holders/proc_alloc/proc_req."""
    state.rag = {'holders': [[] for _ in range(state.n_res)], 
                 'proc_alloc': [[] for _ in range(state.n_proc)], 
                 'proc_req': [[] for _ in range(state.n_proc)] }
    for p in range(state.n_proc):
        state.processes[p].allocated = []
        for r in range(state.n_res):
            if state.allocation[p][r]:
                state.rag['holders'][r].append(p)
                state.rag['proc_alloc'][p].append(r)
                state.processes[p].allocated.append(r)
            if state.request[p][r]:
                state.rag['proc_req'][p].append(r)

def derive_wfg(state):
    """WFG: p -> q if p requests r with avail[r]==0 and q holds r."""
    build_rag(state)
    state.wfg = {p: [] for p in range(state.n_proc)}
    for p in range(state.n_proc):
        for r in state.rag['proc_req'][p]:
            if state.available[r] == 0 and state.rag['holders'][r]:
                state.wfg[p].extend(state.rag['holders'][r])

def visualize_ascii(state):
    """ASCII RAG."""
    state.print_matrices()
    print("\n=== RAG EDGES ===")
    print("Allocation (proc -> res):")
    for p in range(state.n_proc):
        alloc_res = [r for r in range(state.n_res) if state.allocation[p][r]]
        if alloc_res:
            print(f'P{p} holds {[chr(65 + r) for r in alloc_res]}')
    print("\nRequest (proc -> res):")
    for p in range(state.n_proc):
        req_res = [r for r in range(state.n_res) if state.request[p][r]]
        if req_res:
            print(f'P{p} requests {[chr(65 + r) for r in req_res]}')

def detect_deadlock(state):
    """DFS cycle detection on WFG."""
    derive_wfg(state)
    visit = [False] * state.n_proc
    rec_stack = [False] * state.n_proc
    deadlocked_set = set()

    def dfs(node):
        visit[node] = True
        rec_stack[node] = True
        for nei in state.wfg.get(node, []):
            if not visit[nei]:
                if dfs(nei):
                    deadlocked_set.add(nei)
                    return True
            elif rec_stack[nei]:
                deadlocked_set.add(nei)
                return True
        rec_stack[node] = False
        return False

    for p in range(state.n_proc):
        if not visit[p] and state.processes[p].active:
            dfs(p)
    return sorted(list(deadlocked_set)) if deadlocked_set else None

def recover_terminate(state, pid):
    """Terminate process pid, free resources."""
    if pid >= state.n_proc or not state.processes[pid].active:
        print("Invalid PID.")
        return
    for r in state.processes[pid].allocated:
        state.allocation[pid][r] = 0
        state.available[r] += 1  # assume unit
    state.processes[pid].active = False
    print(f"Terminated P{pid}, freed resources.")

def recover_preempt(state, from_pid, res_id):
    """Preempt res_id from from_pid, add to available."""
    if from_pid >= state.n_proc or res_id >= state.n_res or state.allocation[from_pid][res_id] == 0:
        print("Invalid preempt.")
        return
    state.allocation[from_pid][res_id] = 0
    state.available[res_id] += 1
    print(f"Preempted R{chr(65+res_id)} from P{from_pid}.")

global_state = None

def main_menu():
    global global_state
    print("\nSample Deadlock: 3 P, 3 R (A B C)\nAlloc:\nP0: 0 1 0\nP1: 0 0 1\nP2: 1 0 0\nReq:\nP0: 1 0 0\nP1: 0 1 0\nP2: 0 0 1\nAvail: 0 0 0")
    while True:
        print("\n=== DEADLOCK SYSTEM ===")
        print("1. Enter system data")
        print("2. Display RAG")
        print("3. Detect Deadlock")
        print("4. Recover - Terminate Process")
        print("5. Recover - Preempt Resource")
        print("6. Exit")
        
        choice = input('Choose: ').strip()
        
        if choice == '1':
            n_proc = int(input('Enter # processes: '))
            n_res = int(input('Enter # resources: '))
            global_state = SystemState(n_proc, n_res)
            input_matrices(global_state)
            print("\nData entered!")
        elif choice == '2':
            if global_state is None:
                print('Enter data first!')
                continue
            visualize_ascii(global_state)
        elif choice == '3':
            if global_state is None:
                print('Enter data first!')
                continue
            deadlocked = detect_deadlock(global_state)
            if deadlocked:
                print(f"DEADLOCK DETECTED among Processes: { [f'P{i}' for i in deadlocked] }")
            else:
                print('No Deadlock Detected.')
        elif choice == '4':
            if global_state is None:
                print('Enter data first!')
                continue
            deadlocked = detect_deadlock(global_state)
            if not deadlocked:
                print('No deadlock.')
                continue
            pid = int(input(f'Terminate which PID (e.g. {min(deadlocked)})? '))
            recover_terminate(global_state, pid)
        elif choice == '5':
            if global_state is None:
                print('Enter data first!')
                continue
            deadlocked = detect_deadlock(global_state)
            if not deadlocked:
                print('No deadlock.')
                continue
            pid = int(input('From PID? '))
            rid = int(input('Resource ID (0-A,1-B,...)? '))
            recover_preempt(global_state, pid, rid)
        elif choice == '6':
            break
        else:
            print('Invalid.')

if __name__ == '__main__':
    main_menu()
