import sys
sys.path.insert(0, "..")
import time
from opcua import ua, Server

if __name__ == "__main__":

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://localhost:48400/freeopcua/server/")     
    server.application_uri = "urn:freeopcua:python:server"     
    #server.import_xml("OpcUaModbus.NodeSet2.xml") 
    uri = "http://www.maxim.org/OpcUaAggregation/"
    idx = server.register_namespace(uri)
    objects = server.get_objects_node()  
    AggregationObjects=objects.add_object(idx, "AggregationObjects")
    Motor=AggregationObjects.add_object(idx, "Motor")
    Current=Motor.add_variable(idx, "Current", ua.Variant(12, ua.VariantType.Double))
    Voltage=Motor.add_variable(idx, "Voltage", ua.Variant(12, ua.VariantType.Double))
    Speed=Motor.add_variable(idx, "Speed", ua.Variant(22, ua.VariantType.Double))
    Current.set_writable()
    Voltage.set_writable()
    Speed.set_writable()
   
    
    # starting!
    server.start()
    
    try:
        count = 0
        while True:
            time.sleep(1)
            count += 0.12
            Current.set_value(count)
            Voltage.set_value(count)
            Speed.set_value(count)
    finally:
        #close connection, remove subcsriptions, etc
        server.stop()