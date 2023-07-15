import threading
from opcua import ua , Client
import time
from collections import deque
from Common import get_variables,get_Node_Path,get_Node_By_Name

class ThreadClient(threading.Thread):
    def __init__(self,AggregatedServer):
        threading.Thread.__init__(self)  
        self._stopper = threading.Event()
     
        self.Name=AggregatedServer.get_browse_name().Name
        path=["2:AggregationObjects"]
        self.AggregationObjects=AggregatedServer.get_child(path)
        path=["2:Endpoint"]
        Endpoint=AggregatedServer.get_child(path)
        self.ServerURI=Endpoint.get_value()
        #print(self.ServerURI)
        self.client = Client(self.ServerURI)
        nodes=[]
        self.variableList=[]
        # create AggregationServer Variable List
        get_variables(AggregatedServer,nodes)        
        for node in nodes:
           nodeName=node.get_browse_name().Name
           if nodeName!="Endpoint":
                path=deque([])     
                path.appendleft(node.get_browse_name().Name)
                get_Node_Path(node,path)
                ClientPath=self.convertToClinetPath(path)
                self.variableList.append([node,ClientPath])
                #print(self.variableList)
                node.set_writable()
                node.set_attribute(ua.AttributeIds.Historizing, ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
            
    def convertToClinetPath(self,Path):
          ClientPath=[]
          for nodeName in Path:
              
              if (nodeName!="AggregatedServers") and(nodeName!=self.Name):
                  if nodeName=="Objects":
                      ClientPath.append("0:"+nodeName)
                  else:
                      ClientPath.append("2:"+nodeName)
          return ClientPath        
    def stop(self): 
       self._stopper.set()  
  
    def stopped(self): 
        return self._stopper.isSet()  
    
    def run(self):
        #Start
        try:
            self.client.connect()
            while True: 
                #print(self.Name)
                for Variable in self.variableList:
                    VariableName=Variable[0].get_browse_name().Name
                    #print(Variable[1])
                    node=self.client.nodes.root.get_child(Variable[1])
                    value=node.get_value()
                    AggregatedNode=get_Node_By_Name(self.AggregationObjects,VariableName)
                    #print(AggregatedNode)
                    AggregatedNode.set_value(value)
                if self.stopped():
                    print("Client Stopping...")
                    return
                time.sleep(1)
        finally:
             self.client.disconnect() 
             print("client Disconnected")