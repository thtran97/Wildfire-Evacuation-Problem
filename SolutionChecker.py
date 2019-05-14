import numpy as np
import math
import glob
import os
from DataProcess import *

def read_solution (filename):
    SOLUTION = []
    with open(filename,'r') as fp :
        line = fp.read().splitlines()
        test_name = line[0]
        nb_evac_node = int(line[1])
        for i in range(nb_evac_node) : 
            data = list(map(lambda x : int(x),line[2+i].split()))
            SOLUTION.append(data)
            next = 2+i
        NATURE = line[next+1]
        F_OBJECTIF = int(line[next+2])
        methode = line[next+3]
    return SOLUTION,F_OBJECTIF,NATURE

def print_solution(filename) : 
    print('-----------------------------')
    SOLUTION,F_OBJECTIF,NATURE = read_solution(filename)
    print('A solution is :',SOLUTION)
    print('f_objectif = ',F_OBJECTIF)
    print('Nature of solution : ',NATURE)
    print('-----------------------------')
    return 0

def get_solution_info_of(node_id,SOLUTION) : 
    [sol_info] = [item for item in SOLUTION if item[:][0] == node_id]
    eva_rate = sol_info[1]
    t_start = sol_info[2]
    return eva_rate,t_start

def verify_solution(data_path,solution_path) : 
    EVA_TREE,GRAPH,NB_NODES = read_data(data_path)
    SOLUTION,F_OBJECTIF,NATURE = read_solution(solution_path)
    NB_EVA_NODES = len(EVA_TREE)
    NB_EDGES = len(GRAPH)
    LIST_EVA_NODES = [item[0] for item in EVA_TREE]
    
    print_data(data_path)
    print_solution(solution_path)
    print('CREATION TASKS & VERIFY CONSTRAINTS')
    print('-----------------------------')
    ressources = {}
    for edge in GRAPH :
        edge_cap = edge[-1]
#         print('max cap of edge [{}-{}] : {}'.format(edge[0],edge[1],edge_cap))
        ressources.setdefault('Cap of edge[{}-{}]'.format(edge[0],edge[1]),np.full(40,edge_cap))
#         print(ressources)
    
    tasks = {}
    for i in LIST_EVA_NODES : 
        nb_evacuees,max_rate,route_length,route_list = get_eva_node_info(i,EVA_TREE)
        rate,start = get_solution_info_of(i,SOLUTION)
        if rate > max_rate : 
            result = False
            exit(0)
#         print('task {},rate={},start={}'.format(i,rate,start))
        duration,demande_res,rate = get_task(i,EVA_TREE,GRAPH,rate)
#         print(duration,demande_res)
        current = i
        for j in demande_res : 
#             print('Evacuees from {} at node {}'.format(i,j))
            nxt = j
            if current != nxt :
                _,length,edge_cap = get_edge_info(current,nxt,GRAPH)
                tasks.setdefault('Evacuees from {} at edge [{}-{}]'.format(i,current,nxt), [start,start+length+duration,duration,rate])
                dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(current,nxt)]))
                dispo[start:start+duration] -= rate
#                 print('dispo[{}-{}]='.format(current,nxt),dispo)
                check_dispo = [item for item in dispo if item < 0]
                if (len(check_dispo) > 0) : 
                    print('TOO MANY PERSONS AT EDGE [{}-{}] !!!'.format(current,nxt))
                    result = False
                    exit(0)
#                 assert(dispo.all() >= 0)
                else :
                    ressources['Cap of edge[{}-{}]'.format(current,nxt)] = dispo
                start += length
            current = nxt
            
    print('ressources info after evacuation = ',ressources)        
    print('tasks = ', tasks)
    print('Nb of tasks = ',len(tasks))
    print('-----------------------------')
    print('CHECK F_OBJECTIF')
    print('-----------------------------')
    

    end_time = np.max([tasks[keys][1] for keys in tasks])
    print('End time is : ',end_time)
    if (end_time == F_OBJECTIF) : 
        result = True
    else :
        result = False
    
    return result

