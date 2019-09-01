import scipy.sparse as sp
import numpy as np
from copy import deepcopy
from util.Logger import logger
class LeaveOneOutDataSplitter(object):
    def __init__(self,path,separator, threshold):
        self.path =path
        self.separator = separator
        self.threshold = threshold
    def load_data_by_user_time(self):
        logger.info("Loading interaction records from %s "%(self.path))
        pos_per_user = {}
        num_ratings=0
        num_items=0
        num_users=0
        #user/item {raw id, inner id} map
        userids = {}
        itemids = {}
        # inverse views of userIds, itemIds, 
        idusers = {}
        iditems={}
        with open(self.path+".rating", 'r') as f:
            for line in f.readlines():
                useridx, itemidx,rating,time= line.strip().split(self.separator)
                
                if float(rating)>= self.threshold:
                    num_ratings+=1
                    if  itemidx not in itemids:
                        iditems[num_items]=itemidx
                        itemids[itemidx] = num_items
                        num_items+=1
    
                    if useridx not in userids:
                        idusers[num_users]=useridx
                        userids[useridx]=num_users
                        num_users+=1
                        pos_per_user[userids[useridx]]=[]
                    pos_per_user[userids[useridx]].append((itemids[itemidx],1,int(float(time))))
                else :
                    num_ratings+=1
                    if  itemidx not in itemids:
                        iditems[num_items]=itemidx
                        itemids[itemidx] = num_items
                        num_items+=1
    
                    if useridx not in userids:
                        idusers[num_users]=useridx
                        userids[useridx]=num_users
                        num_users+=1
                        pos_per_user[userids[useridx]]=[]
                    pos_per_user[userids[useridx]].append((itemids[itemidx],rating,int(float(time))))
                # rating_matrix[self.userids[useridx],self.itemids[itemidx]] = rating
            for u in np.arange(num_users):
                pos_per_user[u]=sorted(pos_per_user[u], key=lambda d: d[2])
            logger.info("\"num_users\": %d,\"num_items\":%d, \"num_ratings\":%d\n"%(num_users,num_items,num_ratings))
            userseq = deepcopy(pos_per_user)
            train_dict = {}
            train_matrix = sp.dok_matrix((num_users, num_items), dtype=np.float32)
            test_matrix = sp.dok_matrix((num_users, num_items), dtype=np.float32)
            time_matrix = sp.dok_matrix((num_users, num_items), dtype=np.float32)
            for u in np.arange(num_users):
                if len(pos_per_user[u])<3:
                    test_item=-1
                    continue
                
                test_item=pos_per_user[u][-1]
                pos_per_user[u].pop()
                
                test_matrix[u,test_item[0]] = test_item[1]
                time_matrix[u,test_item[0]] = test_item[2]
                items = []
                for enlement in pos_per_user[u]:
                    items.append(enlement[0])
                    train_matrix[u,enlement[0]]=enlement[1]
                    time_matrix[u,enlement[0]] = enlement[2]
                train_dict[u]=items  
        return train_matrix,train_dict,test_matrix,userseq,userids,itemids,time_matrix
