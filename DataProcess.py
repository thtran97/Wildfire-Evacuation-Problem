import numpy as np
import math
import glob
import os
import random

def read_data(filename) :
    eva_tree, graph = [],[]
    nb_node = 0
    mode,start = 0,0
    with open(filename, 'r') as fp :
        for line in fp :
          
            if (line.find('evacuation info') != -1):
                print('Add evacuation info')             
                mode = 1
                start = 0
            
            elif (line.find('graph') != -1):
                print('Add graph info')             
                mode = 2
                start = 0
            
            elif (mode == 1 and start == 0) :
                start = 1
                nb_evac_node = int(line.split()[0]) 
                safe_node = int(line.split()[1])
#             print('safe node is : ',safe_node)
#             print('number of evacuation nodes : ', nb_evac_node)
                          
            elif (mode == 2 and start == 0) :
                start = 1
                nb_node = int(line.split()[0])
                n = int(line.split()[1])
#             print('number of nodes : ',nb_node)
#             print('number of edges : ',n)

            
            elif (mode == 1 and start == 1) :
                data = list(map(lambda x : int(x),line.split()))
                eva_tree.append(data)

                  
            elif (mode == 2 and start == 1) :
                data = list(map(lambda x : int(x),line.split()))
                graph.append(data)
      
    used_edges = set()
    new_graph = []
    for eva_node in eva_tree : 
        route_list = [eva_node[0]] + eva_node[4:]
        for i in range(eva_node[3]) : 
            if route_list[i] < route_list[i+1] : 
                used_edges.add((route_list[i],route_list[i+1]))
            else :
                used_edges.add((route_list[i+1],route_list[i]))
#            print((route_list[i],route_list[i+1]))
#    print(used_edges)
    for edges in graph : 
        if (edges[0],edges[1]) in used_edges :
            new_graph.append(edges)       
            
    return eva_tree,new_graph,nb_node

def print_data(filename):
    eva_tree,graph,nb_nodes = read_data(filename)
    nb_eva_nodes = len(eva_tree)
    nb_edges = len(graph)
    list_eva_nodes = [item[0] for item in eva_tree]

    print('-----------------------------')
    print('evacuation_tree = ', eva_tree)
    print('graph = ',graph)
    print('number of evacuation nodes : ',nb_eva_nodes)
    print('List of evac nodes : ',list_eva_nodes)
    print('number of nodes = ',nb_nodes)
    print('number of edges = ',nb_edges)
    print('-----------------------------')
    return 0
    
def get_eva_node_info(node_id,EVA_TREE) :
    [eva_node_info] = [item for item in EVA_TREE if item[0]==node_id]
#     print(eva_node_info)
    nb_evacuees = eva_node_info[1]
    max_rate = eva_node_info[2]
    route_length = eva_node_info[3]
    route_list = eva_node_info[4:]
    return nb_evacuees,max_rate,route_length,route_list


def get_edge_info(node1,node2,GRAPH):
    if node1 < node2 :
        [edge_info] = [item for item in GRAPH if (item[0]==node1) & (item[1]==node2)]
    else : 
        [edge_info] = [item for item in GRAPH if (item[0]==node2) & (item[1]==node1)]
    due_date = edge_info[2]
    length = edge_info[3]
    capacity = edge_info[4]
    return due_date,length,capacity


def get_task(node_id,EVA_TREE,GRAPH,eva_rate=None) :
    tasks = []
    nb_evacuees,max_rate,route_len,route_list = get_eva_node_info(node_id,EVA_TREE)
    route_list = [node_id] + route_list
    edges_cap = [get_edge_info(route_list[i],route_list[i+1],GRAPH)[2] for i in range (route_len)]
    max_rate = np.min([max_rate]+edges_cap)
    
    if eva_rate == None : 
        eva_rate = max_rate
    else :
        if (eva_rate > max_rate) :
            print("ERROR ON EVACUATION RATE !!")
#         assert(eva_rate <= max_rate)
    

    duration = math.ceil(nb_evacuees/eva_rate)
#     print(DEMANDE_RES)
    return duration,route_list,eva_rate

def create_solution(TASKS,LIST_EVA_NODES) :
    solution = []
    for i in LIST_EVA_NODES : 
        [Si] = [TASKS[keys] for keys in TASKS if 'Evacuees from {} at edge [{}-'.format(i,i) in keys ]
        solution.append([i,Si[-1],Si[0]])
    
    return solution

def get_duration(node_id,EVA_TREE,GRAPH) :
    nb_evacuees,cap_max,route_len,route_list = get_eva_node_info(node_id,EVA_TREE)
    # find capacity as max as possible
    route_list = [node_id] + route_list
    edges_cap = [get_edge_info(route_list[i],route_list[i+1],GRAPH)[2] for i in range (route_len)]
    cap_max = np.min([cap_max]+edges_cap)
#    print(cap_max)
    # find duration 
    edges_length = [get_edge_info(route_list[i],route_list[i+1],GRAPH)[1] for i in range (route_len)]
    E_tmp = np.sum(np.array(edges_length)) + math.ceil(nb_evacuees / cap_max)

    return int(E_tmp)


def get_end_time(LIST_EVA_NODES,EVA_TREE,GRAPH) : 
    ressources = {}
    for edge in GRAPH :
        edge_cap = edge[-1]
#         print('max cap of edge [{}-{}] : {}'.format(edge[0],edge[1],edge_cap))
        ressources.setdefault('Cap of edge[{}-{}]'.format(edge[0],edge[1]),np.full(200,edge_cap))
#         print(ressources)
   
    tasks = {}
    for i in LIST_EVA_NODES : 
        nb_evacuees,max_rate,route_length,route_list = get_eva_node_info(i,EVA_TREE)
        start = 0
        duration,demande_res,eva_rate = get_task(i,EVA_TREE,GRAPH)
        current = i
#        print(eva_rate)
        for j in demande_res : 
#             print('Evacuees from {} at node {}'.format(i,j))
            nxt = j
            if current != nxt :
                _,length,edge_cap = get_edge_info(current,nxt,GRAPH)

                ok = False
                while (not ok) :
                    if current < nxt :
                        dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(current,nxt)]))
                    else : 
                        dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(nxt,current)]))
                    dispo[start:start+duration] -= eva_rate
#                     print('dispo[{}-{}]={}'.format(current,nxt,dispo))
                    check_dispo = [item for item in dispo if item < 0]
#                     print(check_dispo)
                    if (len(check_dispo) > 0) :        
#                         print('OVERLOAD')
                        start += len(check_dispo) 
                        ok = False
                        # Change the time start of the previous nodes 
                        for keys in tasks :
                            if 'Evacuees from {}'.format(i) in keys :
                                tasks[keys][0] += len(check_dispo)
                    else : 
                        ok = True
                        ressources['Cap of edge[{}-{}]'.format(current,nxt)] = dispo

                tasks.setdefault('Evacuees from {} at edge [{}-{}]'.format(i,current,nxt), [start,start+length+duration,duration,eva_rate])
        
                start += length
            current = nxt
            
#         print('ressources info after evacuation of node {} with rate{} = {}'.format(i,max_rate,ressources))
        
#    print('tasks = ', tasks)
#    print('Nb of tasks = ',len(tasks))
    
    end_time = np.max([tasks[keys][1] for keys in tasks])
#     print([tasks[keys][1] for keys in tasks])
#    print('End time is : ',end_time)
    solution = create_solution(tasks,LIST_EVA_NODES)
    
    return end_time,solution

def get_borne_inf(LIST_EVA_NODES,EVA_TREE,GRAPH) : 
    eva_time = [get_duration(item,EVA_TREE,GRAPH) for item in LIST_EVA_NODES]
    return np.max(eva_time)

def get_borne_sup(LIST_EVA_NODES,EVA_TREE,GRAPH) :
#    ORDERED_LIST_EVA_NODES = sorted(LIST_EVA_NODES,key = lambda item : get_duration(item,EVA_TREE,GRAPH))    
#    print(ORDERED_LIST_EVA_NODES)
    RANDOM_LIST = random.choices(LIST_EVA_NODES,k=len(LIST_EVA_NODES))
    endtime,sol = get_end_time(RANDOM_LIST,EVA_TREE,GRAPH)
    return endtime,sol

def create_solution_file(solution,end_time) : 
    file  = open('data/wildfire_sup.solution','w')
    file.write('inputTD\n')
    file.write('{}\n'.format(len(solution)))
    for item in solution : 
        file.write('{} {} {}\n'.format(item[0],item[1],item[2]))
    file.write('valid\n')
    file.write('{}\n'.format(end_time))
    file.write('tmps calcul.. Nan\n')
    file.write('generated by ...\n')
    file.write('home\n')
    
    file.close()
    return 0



