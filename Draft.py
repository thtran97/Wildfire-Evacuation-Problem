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
        ressources.setdefault('Cap of edge[{}-{}]'.format(edge[0],edge[1]),np.full(200,edge_cap))
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
                if start >= max_start:
                    print('Due Date violated for node !', i)
                    error = True
            current = nxt
            
#         print('ressources info after evacuation of node {} with rate{} = {}'.format(i,max_rate,ressources))
        
#    print('tasks = ', tasks)
#    print('Nb of tasks = ',len(tasks))
    if error:
        end_time = 999999999
    else:
        end_time = np.max([tasks[keys][1] for keys in tasks])
#     print([tasks[keys][1] for keys in tasks])
#    print('End time is : ',end_time)
    solution = create_solution(tasks,LIST_EVA_NODES)
    
    return end_time,solution