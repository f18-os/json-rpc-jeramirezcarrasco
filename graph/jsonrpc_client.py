from node import *
import socket
from bsonrpc import JSONRpc
from bsonrpc import request, service_class
from bsonrpc.exceptions import FramingError
from bsonrpc.framing import (
	JSONFramingNetstring, JSONFramingNone, JSONFramingRFC7464)


#Using this the program will figure out if the given node name is a clone of an already existing node
def Not_clone(Node_name, Node_Dic):
    for i in range(0, len(Node_Dic)):
        if Node_name == Node_Dic[i]['name']:
            return False
    return True

#Change a node into dictionary form
def Node_into_Dictionary(Root, Node_Dic):
    #Using the root as an index we are going to iterate through every children it has
    for i in range(0, len(Root.children)):
        ChildrenNode = Root.children[i]
        #If the children has no child do the following
        if ChildrenNode.children == []:
            #Checks if the node is already in the list
            if Not_clone(ChildrenNode.name, Node_Dic):
                Node_Dic.append({'name': ChildrenNode.name, 'val': ChildrenNode.val, 'children': []})
        else:
            if Not_clone(ChildrenNode.name, Node_Dic):
                Node_Dic.append({'name': ChildrenNode.name, 'val': ChildrenNode.val, 'children': ChildrenList(ChildrenNode)})
                Node_Dic = Node_into_Dictionary(ChildrenNode, Node_Dic)
    return Node_Dic

#This will return a list of all the father childrens
def ChildrenList(Father):
    Childrens = []
    for i in range(0, len(Father.children)):
        Childrens.append(Father.children[i].name)
    return Childrens

# This method(function) receives a list of children names and returns the nodes that match that name in a list form
def FatherChildren(Root_List, ChildrenList):
    Childrens = []
    for i in range(0, len(ChildrenList)):
        for j in range(0, len(Root_List)):
            if Root_List[j].name == ChildrenList[i]:
                Childrens.append(Root_List[j])
    return Childrens

#Change a dictionary into a tree
def Dictionary_into_Node(Node_Dic):
    Root_List = []
    #going backwards it iterates through the dictionary
    for i in reversed(range(0, len(Node_Dic))):
        #If the current Dictionary has no child it will create a node and append it
        if Node_Dic[i]['children'] == []:
            Root_List.append(node(Node_Dic[i]['name']))
            Root_List[len(Root_List) - 1].val = Node_Dic[i]['val']
        else:
            #If it does have a child it will look for its child in the Root list dictionary and append them in a new node
            Root_List.append(node(Node_Dic[i]['name'], FatherChildren(Root_List, Node_Dic[i]['children'])))
            Root_List[len(Root_List) - 1].val = Node_Dic[i]['val']
    #Will return the last node in the List which is the root of the tree
    return Root_List[len(Root_List) - 1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 50001))
rpc = JSONRpc(s,framing_cls=JSONFramingNone)
server = rpc.get_peer_proxy()

leaf1 = node("leaf1")
leaf2 = node("leaf2")
root = node("root", [leaf1, leaf1, leaf2])

print("graph before increment")
root.show()

Dict_Root = []
Dict_Root.append(({'name': root.name, 'val': root.val, 'children': ChildrenList(root)}))
Dict_Root = Node_into_Dictionary(root, Dict_Root)
# do this increment remotely:
Incremented_Dict = server.increment(Dict_Root)
print("graph after increment")
root = Dictionary_into_Node(Incremented_Dict)
root.show()
rpc.close()