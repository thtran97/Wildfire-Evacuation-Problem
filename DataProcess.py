import numpy as np
import math
import glob
import os
import random

source_path = os.path.dirname(os.path.abspath('__file__')) + '/InstancesInt/'
solution_path = os.path.dirname(os.path.abspath('__file__')) + '/Solutions/'

def read_data(filename) :
    eva_tree, graph = [],[]
    nb_node = 0
    mode,start = 0,0
    with open(filename, 'r') as fp :
        for line in fp :
          
            if (line.find('evacuation info') != -1):
                #print('Add evacuation info')             
                mode = 1
                start = 0
            
            elif (line.find('graph') != -1):
                #print('Add graph info')             
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
        Si = [TASKS[key] for key in TASKS if ('Evacuees from {} at edge [{}-'.format(i,i) in key or ('Evacuees from {} at edge'.format(i) in key and '-{}]'.format(i) in key))]
        solution.append([i,Si[0][-1],Si[0][0]])
    
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
        ressources.setdefault('Cap of edge[{}-{}]'.format(edge[0],edge[1]),np.full(500,edge_cap))
#         print(ressources)
   
    tasks = {}
    for i in LIST_EVA_NODES : 
#        nb_evacuees,max_rate,route_length,route_list = get_eva_node_info(i,EVA_TREE)
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
                                tasks[keys][1] += len(check_dispo)
                    else : 
                        ok = True
                        ressources['Cap of edge[{}-{}]'.format(current,nxt)] = dispo

                tasks.setdefault('Evacuees from {} at edge [{}-{}]'.format(i,current,nxt), [start,start+length+duration,duration,eva_rate])
        
                start += length
            current = nxt
            
#         print('ressources info after evacuation of node {} with rate{} = {}'.format(i,max_rate,ressources))
        
#    print('tasks = ', tasks)
#     print('Nb of tasks = ',len(tasks))
    
    end_time = np.max([tasks[keys][1] for keys in tasks])
#     print([tasks[keys][1] for keys in tasks])
#    print('End time is : ',end_time)
    solution = create_solution(tasks,LIST_EVA_NODES)
    
        
#     for i  in LIST_EVA_NODES :
#         for key in tasks : 
#             if  ('Evacuees from {} at edge [{}-'.format(i,i) in key or ('Evacuees from {} at edge'.format(i) in key and '-{}]'.format(i) in key)) :
#                 print(i,key, tasks[key])
    return end_time,solution

def get_end_time_2(LIST_EVA_NODES,EVA_TREE,GRAPH) : 
    ressources = {}
    for edge in GRAPH :
        edge_cap = edge[-1]
#         print('max cap of edge [{}-{}] : {}'.format(edge[0],edge[1],edge_cap))
        ressources.setdefault('Cap of edge[{}-{}]'.format(edge[0],edge[1]),np.full(500,edge_cap))
#         print(ressources)
   
    tasks = {}
    for i in LIST_EVA_NODES : 
        nb_evacuees,max_rate,route_length,route_list = get_eva_node_info(i,EVA_TREE)
        start = 0
        duration,demande_res,eva_rate = get_task(i,EVA_TREE,GRAPH)
        current = i
#        print(eva_rate)
        for j in demande_res : 
#            print('Evacuees from {} at node {}'.format(i,j))
            nxt = j
            if current != nxt :
                _,length,edge_cap = get_edge_info(current,nxt,GRAPH)
                
                #Second solution variable 
                start2= start
                error_rate = 0
                end_time2 = 10000000
                
                cumul_time = 0
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
                        error_rate = check_dispo[0]
#                         print('OVERLOAD')
                        start += len(check_dispo) 
                        ok = False
                        
                        cumul_time += len(check_dispo)
                        
                    else : 
                        ok = True
                
                        #here there is no more conflict
                        #First solution : start,end=start + duration, rate = eva_rate
                        #Second solution : 
                        eva_rate2 = eva_rate + error_rate
                        end_time1 = start + duration
                        #print(eva_rate2)
                        if (eva_rate2 > 0 and start2 + math.ceil(nb_evacuees / eva_rate2) < end_time1) :
                            #print("choose 2")
                            #if solutio 2 is better
                            #no change time start of the previous nodes
                            #decrease the rate
                            start = start2
                            eva_rate = eva_rate2
                            duration = math.ceil(nb_evacuees / eva_rate2)
                            if current < nxt :
                                dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(current,nxt)]))
                            else : 
                                dispo = np.copy(np.array(ressources['Cap of edge[{}-{}]'.format(nxt,current)]))
                            dispo[start:start+duration] -= eva_rate
                            # Change the eva_rate of the previous nodes 
                            for keys in tasks :
                                if 'Evacuees from {}'.format(i) in keys :
                                    tasks[keys][-1] = eva_rate
                                    tasks[keys][2] = duration 
                        else :        
                            #print("choose 1")
                            #if solution 1 is better
                            # Change the time start of the previous nodes 
                            for keys in tasks :
                                if 'Evacuees from {}'.format(i) in keys :
                                    tasks[keys][0] += cumul_time
                                
                        #update ressource
                        ressources['Cap of edge[{}-{}]'.format(current,nxt)] = dispo
                tasks.setdefault('Evacuees from {} at edge [{}-{}]'.format(i,current,nxt), [start,start+length+duration,duration,eva_rate])
        
                start += length
            
            current = nxt
            
#         print('ressources info after evacuation of node {} with rate{} = {}'.format(i,max_rate,ressources))
        
#    print('tasks = ', tasks)
#    print('Nb of tasks = ',len(tasks))
    print("okk")
    end_time = np.max([tasks[keys][1] for keys in tasks])
#     print([tasks[keys][1] for keys in tasks])
#    print('End time is : ',end_time)
    solution = create_solution(tasks,LIST_EVA_NODES)
    
    return end_time,solution


def get_latest_starttime(node,EVA_TREE,GRAPH):
    rate = get_task(node,EVA_TREE,GRAPH,None)[2]
    nb_evacuees,_,_,route_list = get_eva_node_info(node,EVA_TREE)
    route_list.reverse()
    route_list.append(node)
    #print(route_list)
    res, _, _ = get_edge_info(route_list[0],route_list[1],GRAPH)
    for i in range(1, len(route_list)-1):
        due_date, length, _ = get_edge_info(route_list[i],route_list[i+1],GRAPH)
        #print('Im on arc {}-{}'.format(route_list[i],route_list[i+1]))
        #print('R-L', res - length)
        #print('DD', due_date)
        if res-length > due_date:
            res = due_date
        else:
            res = res - length
        #print('R', res)
    return res - int(nb_evacuees/rate)


def get_end_time_3(LIST_EVA_NODES,EVA_TREE,GRAPH) : 
    error = False
    ressources = {}
    for edge in GRAPH :
        edge_cap = edge[-1]
#         print('max cap of edge [{}-{}] : {}'.format(edge[0],edge[1],edge_cap))
        ressources.setdefault('Cap of edge[{}-{}]'.format(edge[0],edge[1]),np.full(500,edge_cap))
#         print(ressources)
   
    tasks = {}
    for i in LIST_EVA_NODES : 
#        nb_evacuees,max_rate,route_length,route_list = get_eva_node_info(i,EVA_TREE)
        start = 0
        duration,demande_res,eva_rate = get_task(i,EVA_TREE,GRAPH)
        max_start = get_latest_starttime(i,EVA_TREE,GRAPH)
        current = i
#        print(eva_rate)
        for j in demande_res : 
#             print('Evacuees from {} at node {}'.format(i,j))
            nxt = j
            if current != nxt :
                due_date,length,edge_cap = get_edge_info(current,nxt,GRAPH)

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
                                tasks[keys][1] += len(check_dispo)
                    else : 
                        ok = True
                        ressources['Cap of edge[{}-{}]'.format(current,nxt)] = dispo
                        
                #if start >= max_start:
                #    print('Due Date eviolated for node !', i)
                #    error = True
                 
                if (start + duration > due_date):
                    print('Due Date violated for node !', i)
                    error = True
                    
                tasks.setdefault('Evacuees from {} at edge [{}-{}]'.format(i,current,nxt), [start,start+length+duration,duration,eva_rate])
        
                start += length
            current = nxt
            
#         print('ressources info after evacuation of node {} with rate{} = {}'.format(i,max_rate,ressources))
        
#    print('tasks = ', tasks)
#     print('Nb of tasks = ',len(tasks))
    
    end_time = np.max([tasks[keys][1] for keys in tasks])
#     print([tasks[keys][1] for keys in tasks])
#    print('End time is : ',end_time)
    solution = create_solution(tasks,LIST_EVA_NODES)
    
        
#     for i  in LIST_EVA_NODES :
#         for key in tasks : 
#             if  ('Evacuees from {} at edge [{}-'.format(i,i) in key or ('Evacuees from {} at edge'.format(i) in key and '-{}]'.format(i) in key)) :
#                 print(i,key, tasks[key])
    if error:
        end_time = 999999
        
    return end_time,solution


def get_borne_inf(LIST_EVA_NODES,EVA_TREE,GRAPH) : 
    eva_time = [get_duration(item,EVA_TREE,GRAPH) for item in LIST_EVA_NODES]
    print (eva_time)
    return np.max(eva_time)

def get_borne_sup(LIST_EVA_NODES,EVA_TREE,GRAPH) :
#    ORDERED_LIST_EVA_NODES = sorted(LIST_EVA_NODES,key = lambda item : get_duration(item,EVA_TREE,GRAPH))    
#    print(ORDERED_LIST_EVA_NODES)
#    RANDOM_LIST = random.choices(LIST_EVA_NODES,k=len(LIST_EVA_NODES))
    random.shuffle(LIST_EVA_NODES)
    endtime,sol = get_end_time(LIST_EVA_NODES,EVA_TREE,GRAPH)
    return endtime,sol

def create_solution_file(filename,solution,end_time) : 
    file  = open(filename,'w')
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

def find_starttime(x, sol):
    res = 0
    for item in sol:
        if x == item[0]:
            res = item[2]
    return res

def create_solution_file2(source,solution,end_time) : 
    filename = solution_path + source + '.solution'
    sourcename = source_path + source + '.full'
    
    eva_tree = read_data(sourcename)[0]
    
    file = open(filename,'w')
    
    file.write(source)
    file.write('\n')
    file.write('{}\n'.format(len(solution)))
    for item in eva_tree : 
        get
        file.write('{} {} {}\n'.format(item[0],item[2],find_starttime(item[0], solution)))
    file.write('valid\n')
    file.write('{}\n'.format(end_time))
    file.write('tmps calcul.. Nan\n')
    file.write('generated by ...\n')
    file.write('home\n')
    
    file.close()
    return 0

def create_solution_file3(source,solution,end_time,algo_name,exc_time) : 
    filename = solution_path + source + '.solution'
    sourcename = source_path + source + '.full'
    
    eva_tree, graph, _ = read_data(sourcename)
    
    file = open(filename,'w')
    
    file.write(source)
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


