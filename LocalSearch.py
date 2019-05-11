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
    ordered_sol = create_ordered_list_of(init_solution)
    endtime = get_end_time(ordered_sol,EVA_TREE,GRAPH)[0]
    print(ordered_sol,' => ',endtime)
    best_solution =  init_solution
    ite = 0
    while (ite < n_iter) :
        neighbor_list = get_neighbors_of(ordered_sol)
        for sol in neighbor_list :  
#            print('-----{}------'.format(sol))
            if get_end_time(sol,EVA_TREE,GRAPH)[0] <endtime :
                ordered_sol = sol 
                endtime,best_solution = get_end_time(sol,EVA_TREE,GRAPH)
                print(sol,' => ',endtime)
        ite +=1 
        
    
    return best_solution,endtime
    
    
    
