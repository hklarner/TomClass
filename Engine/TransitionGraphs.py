

import itertools as IT



def iter_dfs(G, s):
    S, Q = set(), []
    Q.append(s)
    while Q:
        u = Q.pop()
        if u in S: continue
        S.add(u)
        Q.extend(G[u])
        yield u

def dfs_topsort(G):
    S, res = set(), []
    def recurse(u):
        if u in S: return
        S.add(u)
        for v in G[u]:
            recurse(v)
        res.append(u)

    for u in G:
        recurse(u)
    res.reverse()
    return res

def tr(G):
    GT = {}
    for u in G: GT[u] = set()
    for u in G:
        for v in G[u]:
            GT[v].add(u)
    return GT

def walk(G, H, s, S=set()):
    P, Q = set([s]), set([s])
    forward = set()
    while Q:
        u = Q.pop()
        forward.update(H[u])
        for v in G[u].difference(P, S):
            Q.add(v)
            P.add(v)

    terminal = forward==P
            
    return P, terminal

def attracting_sccs(G):
    GT = tr(G)
    sccs, seen = [], set()
    for u in dfs_topsort(G):
        if u in seen: continue
        C, terminal = walk(GT, G, u, seen)
        seen.update(C)
        if terminal:
            sccs.append(C)
    
    return sccs

def sccs(G):
    GT = tr(G)
    sccs, seen = [], set()
    for u in dfs_topsort(G):
        if u in seen: continue
        C, terminal = walk(GT, G, u, seen)
        seen.update(C)
        sccs.append(C)
    
    return sccs
            




def async_successors(Components, Parameters, State):
    succs = set([])
    fixpoint = True
    for comp in Components:
        for p in comp.parameters:
            if all([State[reg.index] in p.context[reg] for reg in p.context]):
                break

        if State[comp.index] == Parameters[p]:
            continue
        
        fixpoint = False
        delta = -1
        if State[comp.index] < Parameters[p]:
            delta = 1

        suc = list(State[:])
        suc[comp.index]+= delta
        succs.add(tuple(suc))

    if fixpoint:
        succs.add(tuple(State[:]))

    return succs

def async_reachability_graph(Components, Parameters, Initial_states=set()):
    G = dict()
    Q = set(Initial_states)
    
    while Q:
        u = Q.pop()
        succs = async_successors(Components, Parameters, u)
        G[u] = succs
        for v in succs.difference(G):
            Q.add(v)
            
    return G

def async_attractors(Components, Parameters, Initial_states):
    if not Initial_states:
        Initial_states = [tuple(s) for s in IT.product(  *[range(comp.max+1) for comp in Components]  )]
    G = async_reachability_graph(Components, Parameters, Initial_states)

    return attracting_sccs(G)

def async_sccs(Components, Parameters, Initial_states=set()):
    if not Initial_states:
        Initial_states = [tuples(s) for s in IT.product(  *[range(comp.max+1) for comp in Components]  )]
    G = async_reachability_graph(Components, Parameters, Initial_states)

    return sccs(G)


def sync_successor(Components, Parameters, State):
    suc = State[:]

    for comp in Components:
        for p in comp.parameters:
            if all([State[reg.index] in p.context[reg] for reg in p.context]):
                break

        if State[comp.index]==self.params[p]:
            continue

        delta = -1
        if State[comp.index]<self.params[p]:
            delta = 1

        suc[comp.index]+= delta

    return suc
