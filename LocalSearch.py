import numpy as np
import math
import time
from DataProcess import *


#ordered by time start of each node
def create_ordered_list_of(solution) : 
    ordered_sol = sorted(solution,key= lambda item : item[-1])
    ordered_sol = [item[0] for item in ordered_sol]
    return ordered_sol

def get_conflict_arc(l1, l2):
    res = []
    for item1 in l1:
        if item1 in l2:
            res.append(item1)
    return res

def get_non_conflict_list(x, LIST_EVA_NODES,EVA_TREE,GRAPH):
    ok = 1
    res = []
    lx = get_task(x,EVA_TREE,GRAPH,eva_rate=None)[1]
    rate_x = get_task(x,EVA_TREE,GRAPH,eva_rate=None)[2]
    for node in LIST_EVA_NODES:

        if x != node:

            ln = get_task(node,EVA_TREE,GRAPH,eva_rate=None)[1]
            rate_n = get_task(node,EVA_TREE,GRAPH,eva_rate=None)[2]
            lc = get_conflict_arc(lx, ln)
            if(len(lc) == 1):

                res.append(node)
            else:
                for i in range(len(lc)-1):
                    cap = get_edge_info(lc[i], lc[i+1], GRAPH)[2]

                    if (cap < rate_x + rate_n):
                        ok = 0
                        break
            if (ok == 1):

                res.append(node)
            ok = 1
    return res
                    

#exchange positions of 2 nodes in the ordered list  -> a neigbor 
def get_neighbors_of(ordered_sol,EVA_TREE,GRAPH) : 
    neighbor_list = []
    for i in range(len(ordered_sol)) :
        l = get_non_conflict_list(ordered_sol[i],ordered_sol,EVA_TREE,GRAPH)
        for j in range(i+1,len(ordered_sol)) :
            if not(ordered_sol[j] in l): 
                new_sol = np.copy(ordered_sol)
                new_sol[i] = ordered_sol[j]
                new_sol[j] = ordered_sol[i]
                neighbor_list.append(new_sol)
    return neighbor_list


#Local Search algorithm 
def LocalSearchRun(init_solution,EVA_TREE,GRAPH,n_iter=10) : 
    ordered_list_of_sol = create_ordered_list_of(init_solution)
    endtime = get_end_time(ordered_list_of_sol,EVA_TREE,GRAPH)[0]

    best_solution =  init_solution
    ite = 0
    not_move = 0
    previous_time = endtime
    while (ite < n_iter and not_move < 5) :
        print("Iteration {}:".format(ite))
        print(ordered_list_of_sol,' => ',endtime)

        neighbor_list = get_neighbors_of(ordered_list_of_sol, EVA_TREE, GRAPH)
        for neighbor in neighbor_list :  
            ## find the best neighbor
            end,current_sol = get_end_time(neighbor,EVA_TREE,GRAPH)
            if end < endtime :
                ordered_list_of_sol = neighbor 
                endtime = end
                best_solution = current_sol
                #print(neighbor,' => ',endtime)
        
        if endtime != previous_time : 
            not_move = 0
            previous_time = endtime
        else :
            not_move += 1
                
        ite +=1 
    return endtime,best_solution


#Local Search Random Start algorithm using get_neighbor_v2, returning algo name and exec time
def LocalSearchRandomStart(EVA_TREE,GRAPH,n_iter=10,n_start_points=5) :
    exc_time = time.time()
    
    algo_name = 'Local Search with Random Start'
    
    LIST_EVA_NODES = [item[0] for item in EVA_TREE]
    
    sol_list = []
    endtime_list = []
    
    for i in range(n_start_points) :
        random.shuffle(LIST_EVA_NODES)
        _,init_solution = get_end_time(LIST_EVA_NODES,EVA_TREE,GRAPH)
        print("---------------------------Start n.{}---------------------------".format(i+1))
        endtime,best_solution = LocalSearchRun(init_solution,EVA_TREE,GRAPH,n_iter)
        sol_list.append(best_solution)
        endtime_list.append(endtime)
        
        
    
    endtime = np.min(endtime_list)
    index = [i for i,j in enumerate(endtime_list) if j==endtime]
    best_solution = sol_list[index[0]]
    
    exc_time = time.time() - exc_time
    
    return endtime,best_solution,algo_name,exc_time
