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
#                print('Add evacuation info')             
                mode = 1
                start = 0
            
            elif (line.find('graph') != -1):
#                print('Add graph info')             
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

    ## clean the graph      
    used_edges = set()
    new_graph = []
    for eva_node in eva_tree : 
        route_list = [eva_node[0]] + eva_node[4:]
        for i in range(eva_node[3]) : 
            if route_list[i] < route_list[i+1] : 
                used_edges.add((route_list[i],route_list[i+1]))
            else :
                used_edges.add((route_list[i+1],route_list[i]))

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
    
def get_eva_node_info(node_id,eva_tree) :
    [eva_node_info] = [item for item in eva_tree if item[0]==node_id]
    nb_evacuees = eva_node_info[1]
    max_rate = eva_node_info[2]
    route_length = eva_node_info[3]
    route_list = eva_node_info[4:]
    return nb_evacuees,max_rate,route_length,route_list


def get_edge_info(node1,node2,graph):
    if node1 < node2 :
        [edge_info] = [item for item in graph if (item[0]==node1) & (item[1]==node2)]
    else : 
        [edge_info] = [item for item in graph if (item[0]==node2) & (item[1]==node1)]
    due_date = edge_info[2]
    length = edge_info[3]
    capacity = edge_info[4]
    return due_date,length,capacity


def get_task(node_id,eva_tree,graph,eva_rate=None) :
    tasks = []
    nb_evacuees,max_rate,route_len,route_list = get_eva_node_info(node_id,eva_tree)
    route_list = [node_id] + route_list
    edges_cap = [get_edge_info(route_list[i],route_list[i+1],graph)[2] for i in range (route_len)]
    max_rate = np.min([max_rate]+edges_cap)
    
    if eva_rate == None : 
        eva_rate = max_rate
    else :
        if (eva_rate > max_rate) :
            print("get_task >> ERROR ON EVACUATION RATE !!")
    duration = math.ceil(nb_evacuees/eva_rate)
    return duration,route_list,eva_rate

def create_solution(tasks,list_eva_nodes) :
    solution = []
    for i in list_eva_nodes : 
        Si = [tasks[key] for key in tasks if ('Evacuees from {} at edge [{}-'.format(i,i) in key or ('Evacuees from {} at edge'.format(i) in key and '-{}]'.format(i) in key))]
        solution.append([i,Si[0][3],Si[0][0]])
    return solution

def get_duration(node_id,eva_tree,graph) :
    nb_evacuees,cap_max,route_len,route_list = get_eva_node_info(node_id,eva_tree)
    ## find capacity as max as possible
    route_list = [node_id] + route_list
    edges_cap = [get_edge_info(route_list[i],route_list[i+1],graph)[2] for i in range (route_len)]
    cap_max = np.min([cap_max]+edges_cap)
    ## find duration 
    edges_length = [get_edge_info(route_list[i],route_list[i+1],graph)[1] for i in range (route_len)]
    E_tmp = np.sum(np.array(edges_length)) + math.ceil(nb_evacuees / cap_max)
    return int(E_tmp)


def get_end_time(list_eva_nodes,eva_tree,graph) : 
    ## Initialize the ressources 
    ressources = {}
    for edge in graph :
        edge_cap = edge[-1]
        ressources.setdefault('Cap of edge[{}-{}]'.format(edge[0],edge[1]),np.full(500,edge_cap))   
        
    ## Arrange the tasks 
    tasks = {}
    for i in list_eva_nodes : 
#         print('Test for node ',i)
        cap_ok = False
        delay_time = 0
        while(not cap_ok) :
            start = 0
            ## find delay_time
            ## arrange the following tasks with the start+delay_time
            duration,demande_res,eva_rate = get_task(i,eva_tree,graph)
            current = i
            for j in demande_res : 
                nxt = j
                if current != nxt :
                    due_date,length,edge_cap = get_edge_info(current,nxt,graph)
                    if current < nxt :
                        dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(current,nxt)]))
                    else : 
                        dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(nxt,current)]))
                    dispo[start+delay_time:start+delay_time+duration] -= eva_rate
                    check_dispo = [item for item in dispo if item<0]
                    if len(check_dispo) > 0 :
#                         print('Overload [{}-{}] : '.format(current,nxt),dispo)
                        delay_time += len(check_dispo)
                        cap_ok = False
                        break
                    else : 
                        cap_ok = True
#                         print('OK [{}-{}] with delay = {}'.format(current,nxt,delay_time))
                    start += length
                current = j
                
#         print(delay_time)
        start = delay_time
        duration,demande_res,eva_rate = get_task(i,eva_tree,graph)
        current = i
        for j in demande_res : 
            nxt = j
            if current != nxt :
                due_date,length,edge_cap = get_edge_info(current,nxt,graph)
                if current < nxt :
                    dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(current,nxt)]))
                else : 
                    dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(nxt,current)]))
                dispo[start:start+duration] -= eva_rate
                check_dispo = [item for item in dispo if item<0]
#                 if len(check_dispo) > 0 :
#                     print('Overload! [{}-{}] : '.format(current,nxt))
                ## Update the ressources of the current edge
                if current < nxt :
                    ressources['Cap of edge[{}-{}]'.format(current,nxt)] = dispo
                else : 
                    ressources['Cap of edge[{}-{}]'.format(nxt,current)] = dispo
                tasks['Evacuees from {} at edge [{}-{}]'.format(i,current,nxt)] = [start,start+length+duration,duration,eva_rate,due_date,dispo]
                start += length
            current = j
    
#         print('After node',i,' res = ',ressources)
#     print('tasks = ', tasks)
#     print('Nb of tasks = ',len(tasks))
    end_time = np.max([tasks[keys][1] for keys in tasks])
#     print([tasks[keys][1] for keys in tasks])
#    print('End time is : ',end_time)
    solution = create_solution(tasks,list_eva_nodes)
    return end_time,solution


def get_end_time_alpha(list_eva_nodes,eva_tree,graph) : 
    ## Initialize the ressources 
    ressources = {}
    for edge in graph :
        edge_cap = edge[-1]
        ressources.setdefault('Cap of edge[{}-{}]'.format(edge[0],edge[1]),np.full(500,edge_cap))   
        
    ## Arrange the tasks 
    tasks = {}
    for i in list_eva_nodes : 
        cap_ok = False
        shift_time = 0
        dist = 0
        while(not cap_ok) :
            start = shift_time

            ## arrange the following tasks with the start
            duration,demande_res,eva_rate = get_task(i,eva_tree,graph)
            current = i
            
            for j in demande_res : 
                nxt = j
                if current != nxt :
                    due_date,length,edge_cap = get_edge_info(current,nxt,graph)
                        
                    if current < nxt :
                        dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(current,nxt)]))
                    else : 
                        dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(nxt,current)]))
                    
                    dispo[start:start+duration] -= eva_rate
                    if shift_time > 0 :
                        dispo[start-dist:start-dist+duration] += eva_rate
#                         print(start-shift_time,start-shift_time+duration)
#                     print('Cap of edge[{}-{}] = {}'.format(current,nxt,dispo))
                    ## Update the ressources of the current edge
                    if current < nxt :
                        ressources['Cap of edge[{}-{}]'.format(current,nxt)] = dispo
                    else : 
                        ressources['Cap of edge[{}-{}]'.format(nxt,current)] = dispo
                    
                    
#                     if shift_time == 0 :
#                         tasks.setdefault('Evacuees from {} at edge [{}-{}]'.format(i,current,nxt), [start,start+length+duration,duration,eva_rate,due_date,dispo])
#                     else :
                    tasks['Evacuees from {} at edge [{}-{}]'.format(i,current,nxt)] = [start,start+length+duration,duration,eva_rate,due_date,dispo]
                    
                    start += length
                current = j

            ## check the capacity constraints with this time start
#             stop = False
            
            for key in tasks :
                if 'Evacuees from {}'.format(i) in key :
                    check_dispo = [item for item in tasks[key][5] if item<0]
                    if len(check_dispo) > 0 :
                        shift_time += len(check_dispo)
                        dist = len(check_dispo)
#                         stop = True
                        cap_ok = False
                        break
                    else :
                        cap_ok = True
                ## return cap_ok and shift_time 

#     print('tasks = ', tasks)
#     print('Nb of tasks = ',len(tasks))
    end_time = np.max([tasks[keys][1] for keys in tasks])
#     print([tasks[keys][1] for keys in tasks])
#    print('End time is : ',end_time)
    solution = create_solution(tasks,list_eva_nodes)
    return end_time,solution



def get_latest_starttime(node,eva_tree,graph):
    rate = get_task(node,eva_tree,graph,None)[2]
    nb_evacuees,_,_,route_list = get_eva_node_info(node,eva_tree)
    route_list.reverse()
    route_list.append(node)
    #print(route_list)
    res, _, _ = get_edge_info(route_list[0],route_list[1],graph)
    for i in range(1, len(route_list)-1):
        due_date, length, _ = get_edge_info(route_list[i],route_list[i+1],graph)
        if res-length > due_date:
            res = due_date
        else:
            res = res - length
        #print('R', res)
    return res - int(nb_evacuees/rate)

def get_list_priority(eva_tree,graph) : 
    list_eva_nodes = [item[0] for item in eva_tree]
    maxstart = [(get_latest_starttime(item,eva_tree,graph),item) for item in list_eva_nodes]
    print(maxstart)
    maxstart.sort()
    print(maxstart)
    result = [item[1] for item in maxstart]
    return result



def get_borne_inf(list_eva_nodes,eva_tree,graph) : 
    eva_time = [get_duration(item,eva_tree,graph) for item in list_eva_nodes]
    return np.max(eva_time)

def get_borne_sup(eva_tree,graph) :
    endtime,sol = get_end_time(get_list_priority(eva_tree.graph),eva_tree,graph)
    return endtime,sol


def find_starttime(x, sol):
    res = 0
    for item in sol:
        if x == item[0]:
            res = item[2]
    return res


def create_solution_file(dataname,solution,end_time,algo_name,exc_time) : 
    
    datapath = os.path.dirname(os.path.abspath('__file__')) +  '/InstancesInt/' + dataname + '.full'
    solutionpath = os.path.dirname(os.path.abspath('__file__')) + '/Solutions/' + dataname + '.solution'

    eva_tree, graph, _ = read_data(datapath)
    
    file = open(solutionpath,'w')
    
    file.write(dataname)
    file.write('\n')
    file.write('{}\n'.format(len(solution)))
    for item in eva_tree : 
        rate = get_task(item[0],eva_tree,graph,eva_rate=None)[2]
        file.write('{} {} {}\n'.format(item[0],rate,find_starttime(item[0], solution)))
    file.write('valid\n')
    file.write('{}\n'.format(end_time))
    file.write(str(exc_time))
    file.write('\n')
    file.write(algo_name)
    file.write('\n')
    file.write('\"oh hell yes\"\n')
    
    file.close()
    return 0


