import sys
sys.path.insert(0, "..")
import time
from opcua import ua, Server
from collections import deque
from Common import get_variables,get_Node_Path
from ThreadClient import ThreadClient
from opcua.server.history_sql import HistorySQLite

if __name__ == "__main__":

    # setup Aggregation server
    server = Server()    
    server.set_endpoint("opc.tcp://localhost:48410/freeopcua/server/")     
    server.application_uri = "urn:freeopcua:python:server"     
    #server.import_xml("OpcUaModbus.NodeSet2.xml") 
    # Create aggregation information model
    uri = "http://www.maxim.org/OpcUaAggregation/"
    idx = server.register_namespace(uri)
    objects = server.get_objects_node()  
    AggregatedServers=objects.add_object(idx, "AggregatedServers")
    AggregatedServer1=AggregatedServers.add_object(idx, "Server1")
    Endpoint= AggregatedServer1.add_variable(idx,"Endpoint", ua.Variant("opc.tcp://localhost:48400/freeopcua/server/", ua.VariantType.String))    
    AggregationObjects=AggregatedServer1.add_object(idx, "AggregationObjects")
    Motor=AggregationObjects.add_object(idx, "Motor")
    Current=Motor.add_variable(idx, "Current", ua.Variant(0, ua.VariantType.Double))
    voltage=Motor.add_variable(idx, "Voltage", ua.Variant(0, ua.VariantType.Double))
    Speed=Motor.add_variable(idx, "Speed", ua.Variant(0, ua.VariantType.Double))
   
    # Start Clients Thread
    root=server.get_root_node()
    path=["0:Objects", "2:AggregatedServers"]
    
    AggregatedServers=root.get_child(path)
    AggregatedServerChildrens=AggregatedServers.get_children()
    #AggregatedServersNum=len(AggregatedServerChildrens)
    clients_threads = []
    i=0
    for AggregatedServerChildren in AggregatedServerChildrens:
            clients_threads.append(ThreadClient(AggregatedServerChildren))
            clients_threads[i].start()
            i=i+1
    #Start Server  
    server.iserver.history_manager.set_storage(HistorySQLite("my_datavalue_history.sql"))     
    server.start()
    # Enable WriteAccess and Historizing 
    nodes=[]
    get_variables(AggregatedServers,nodes)
    for node in nodes:
        nodeName=node.get_browse_name().Name
        if nodeName!="Endpoint":
            path=deque([])
            path.appendleft(node.get_browse_name().Name)
            get_Node_Path(node,path)
            #print(path)
            node.set_writable()
            node.set_attribute(ua.AttributeIds.Historizing, ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
            server.historize_node_data_change(node, period=None, count=100)
    # main Loop
    try:
        count = 0
        while True:
            time.sleep(5)
            count += 0.1
         
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()
        for clients_thread in clients_threads:
                clients_thread.stop()