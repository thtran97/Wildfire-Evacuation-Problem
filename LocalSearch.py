import numpy as np
import math
from DataProcess import *


#ordered by time start of each node
def create_ordered_list_of(solution) : 
    ordered_sol = sorted(solution,key= lambda item : item[-1])
    ordered_sol = [item[0] for item in ordered_sol]
    return ordered_sol

#exchange positions of 2 nodes in the ordered list  -> a neigbor 
def get_neighbors_of(ordered_sol) : 
    neighbor_list = []
    for i in range(len(ordered_sol)) :
        for j in range(i+1,len(ordered_sol)) :
            new_sol = np.copy(ordered_sol)
            new_sol[i] = ordered_sol[j]
            new_sol[j] = ordered_sol[i]
            neighbor_list.append(new_sol)
    return neighbor_list

 
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
        neighbor_list = get_neighbors_of(ordered_list_of_sol)
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

def LocalSearchRun2(init_solution,EVA_TREE,GRAPH,n_iter=10) : 
    ordered_list_of_sol = create_ordered_list_of(init_solution)
    endtime,best_solution = get_end_time_2(ordered_list_of_sol,EVA_TREE,GRAPH)
    
    ite = 0
    not_move = 0
    previous_time = endtime
    while (ite < n_iter and not_move < 5) :
        print("Iteration {}:".format(ite))
        print(ordered_list_of_sol,' => ',endtime)
        neighbor_list = get_neighbors_of(ordered_list_of_sol)
        for neighbor in neighbor_list :  
            ## find the best neighbor
            end,current_sol = get_end_time_2(neighbor,EVA_TREE,GRAPH)
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

def LocalSearchRandomStart(EVA_TREE,GRAPH,n_iter=10,n_start_points=5) :
    
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
        print("----------------------------------------------------------------")
    
    endtime = np.min(endtime_list)
    index = [i for i,j in enumerate(endtime_list) if j==endtime]
    best_solution = sol_list[index[0]]
    
    return endtime,best_solution
    
