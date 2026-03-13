# Deadlock Detection and Recovery System

## Overview
A Python-based simulation of deadlock detection and recovery using Resource Allocation Graph (RAG) and derived Wait-For Graph (WFG). Uses standard libraries only, fully offline.

### How it Works
1. **Input**: User enters #processes (P), #resources (R), allocation matrix (P x R, 0/1), request matrix (P x R, 0/1), available vector (R ints).
2. **RAG**: Built from allocation (proc holds res) and request (proc wants res) edges.
3. **WFG**: Derived process->process waits (if P1 requests R held only by P2).
4. **Detection**: DFS cycle detection on WFG identifies deadlocked processes.
5. **Recovery**: 
   - Terminate a process (frees its resources).
   - Preempt resource from one process to another in cycle.
6. **Viz**: ASCII representation of graphs/matrices.

## Quick Start
```
cd "c:/Users/koush/OneDrive/Desktop/Deadlock Detection and Recovery System"
python main.py
```

## Menu Options
1. Enter system data (prompts for matrices).
2. Display RAG (ASCII).
3. Detect Deadlock.
4. Apply Recovery (if deadlocked).
5. Exit.

## Sample Input / Output

**Sample Deadlock Scenario** (3 Procs P0,P1,P2; 3 Res A=0,B=1,C=2)
```
Enter # processes: 3
Enter # resources: 3

Allocation Matrix (P x R, enter row by row, space separated 0/1):
Row 0: 0 1 0
Row 1: 0 0 1
Row 2: 1 0 0

Request Matrix:
Row 0: 1 0 0
Row 1: 0 1 0
Row 2: 0 0 1

Available: 0 0 0
```

**Detection Output:**
```
DEADLOCK DETECTED among Processes: P0, P1, P2
Cycle: P0 -> A (held by P2) -> P2 -> C (held by P1) -> P1 -> B (held by P0)
```

**ASCII RAG:**
```
Processes: P0, P1, P2
Resources: A, B, C

Alloc Edges:
P0 -- B
P1 -- C
P2 -- A

Request Edges:
P0 -> A
P1 -> B
P2 -> C
```

**Recovery:**
```
Recovery: Terminate P0
Updated Available: 0 1 0
P0 terminated.
```

## Algorithm Explanation
- **RAG**: Bipartite graph Proc-Res with alloc (hold) and req (want) edges.
- **WFG**: From RAG, P1 waits for P2 if P1 req R exclusively held by P2.
- **Deadlock**: Cycle in WFG (mutual wait).
- **Detection**: DFS from each proc, track visit path/recursion stack for back edges.
- **Recovery**: Termination simplest (victim selection: lowest PID); preemption rolls back alloc.

## File Structure
- `main.py`: Core logic and menu.
- `README.md`: This file.
- `TODO.md`: Progress tracker.

## Testing
Run `python main.py` and follow menu with sample above. Verifies cycle detect + recovery updates state correctly.

**Built with Python 3 standard libs only.**

