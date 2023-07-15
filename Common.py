from opcua import ua, Server
from collections import deque
def get_variables(node,variables):
    nodes=[]
    childs=node.get_children(refs=ua.ObjectIds.HasComponent)
    for child in childs:
        nodes.append(child)
    childs=node.get_children(refs=ua.ObjectIds.HasProperty)
    for child in childs:
        nodes.append(child)
    #print(nodes)
    for node in nodes:
        if node.get_node_class().name=="Variable":
              variables.append(node)
        if node.get_node_class().name=="Object":
              get_variables(node,variables)                     
def get_Node_Path(Node,path): 
       ParentNode=Node.get_parent()
       ParentNodeName=ParentNode.get_browse_name().Name
       #print(ParentNodeName) 
       path.appendleft(ParentNode.get_browse_name().Name)
       if ParentNodeName=="Objects":
           return
       else:
           
           get_Node_Path(ParentNode, path)
def get_Node_By_Name(node,Name):
              #print(Name)
              childs=node.get_children(refs=ua.ObjectIds.HasComponent)
              #print(childs)
              if childs!=[]:
                  i=0
                  for child in childs:
                        
                         #print(child.get_browse_name().Name)
                         if(child.get_browse_name().Name==Name):
                                 #print("return")
                                 return childs[i]
                         else:    
                             #print(child.get_node_class().name)    
                             if(child.get_node_class().name=="Object"):
                                 #print("is Object")
                                 return get_Node_By_Name(child,Name)
                         i=i+1         
              else:                   
                      childs=node.get_children(refs=ua.ObjectIds.HasProperty)
                      #print("property")
                      if childs!=[]:
                              for child in childs:
                                      #print(child.get_browse_name().Name)
                                       if(child.get_browse_name().Name==Name): 
                                               return child
                                       