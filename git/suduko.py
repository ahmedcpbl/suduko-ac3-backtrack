from copy import deepcopy
import sys

alphabets = ['A', 'B', 'C', 'D','E', 'F', 'G','H','I']
boxIndexList =  [i + str(n) for i in alphabets for n in range(1,10)]

class csp:
    def __init__(self, initialstate):
        #create a set of variables boardboxes using dict with index of Letter[vertical] and number [horizontal]
        self.solution = ""
        self.boardboxes = {}
        initialstate =  list(map(int,list(initialstate)))
        self.domain = list(range(1, 10))
        
        #create a dictionary of domains for all box indexes and neighbors for each
        self.domains = {}
        self.neighbors = {}
        
        self.unassignedVars = []
        #set initial value or domain of available values  #need to fix this to determine row and use dict
        for i in range(0,len(initialstate) ) :
            
            curBoxName = boxIndexList[i]
            if initialstate[i] == 0:
                self.boardboxes[curBoxName] = 0
                self.domains[curBoxName] = self.domain.copy()
            else:
               self.boardboxes[curBoxName] = initialstate[i]
               self.domains[curBoxName] = [initialstate[i]]
             
            #loop through the whole board, and for each box
        for letter in alphabets:
            for i in range(1, 10):
                #do the following:
                myneighbors = []
                
                #add horizontal arcs
                for horizontal in range(1, 10):
                    myneighbors.append(letter + str(horizontal))
                #add vertical arcs
                for vertical in alphabets:
                    myneighbors.append(vertical + str(i))
                #handle boxes
                alphaindex = alphabets.index(letter) 
                if alphaindex >=0 and alphaindex < 3:
                    ystart = 0
                elif alphaindex >= 3 and alphaindex < 6:
                    ystart = 3
                else: 
                    ystart = 6
                if i < 4 and i >0:
                    xstart = 1
                elif i < 7 and i > 3:
                    xstart = 4
                else:
                    xstart = 7
                for x in range(0, 3):
                    for y in range(0, 3):
                        myneighbors.append(alphabets[ystart+y] + str(xstart+x))
                #shake out the duplicates from the list
                myneighbors = list(set(myneighbors))    
                #remove self
                myneighbors.remove(letter + str(i))
                self.neighbors[letter + str(i)] = myneighbors.copy()
                
            
    def output(self):
        outfile = open("output.txt", 'w')
        outstring = ""
        for boxID in boxIndexList:
            outstring += str(self.boardboxes[boxID])
        self.solution = outstring
        outfile.write(outstring)
        outfile.close()
	print(outstring)
        
    def isSolved(self):
        for k, dom in self.domains.items():
            if len(dom) > 1:
                return False
        return True
     
    def getUnassigned(self):
        self.unassignedVars = []
        for x in boxIndexList:
             if self.boardboxes[x] == 0:
                 self.unassignedVars.append(x)
    
    def getMRV(self):
        mrvNode = ""
        mrvNodeLen = 9
        for x in self.unassignedVars:
            if len(self.domains[x]) < mrvNodeLen:
                mrvNode = x
                mrvNodeLen = len(self.domains[x])
        if mrvNode:
            self.unassignedVars.remove(mrvNode)
        return mrvNode
        
    
    def hasUnassigned(self):
        if self.unassignedVars:
            return True
        else:
            return False
    
    def checkConsistency(self, node, ProposedValue):
        #check neighbors to see if a value can be assigned to this node
        for neighbor in self.neighbors[node]:
            if len(self.domains[neighbor]) == 1 and (ProposedValue in self.domains[neighbor]):
                return False
        #if we have gotten here, we can try to assign the value, so set it and remove it
        #from domains of other nodes
        self.domains[node] = [ProposedValue]
        self.boardboxes[node] = ProposedValue
        for neighbor in self.neighbors[node]:
                if ProposedValue in self.domains[neighbor]:
                    self.domains[neighbor].remove(ProposedValue)
        return True
        
            
def AC3(csp):
        queue = []
        for X in boxIndexList:
            for y in csp.neighbors[X]:
                queue.append((X, y))
        #queue = [y for y in csp.neighbors[X] for X in boxIndexList ]
        while queue:
            node1, node2 = queue.pop()
            if revise(csp, node1, node2):
                if len(csp.domains[node1]) == 0:
                    return False
                else:
                    for neighbor in csp.neighbors[node1]:
                        queue.append((node1, neighbor))
        return True
        
def revise(csp, node1, node2):
    revised = False
    val1 =  int(csp.boardboxes[node1] )
    val2 = int(csp.boardboxes[node2])
    
    #if one already has a value assigned, handle that
    if not (val1 == 0 and val2 == 0):
        changes = 2
        try:
            csp.domains[node1].remove(val2)
        except ValueError:
            changes = changes - 1
        try:
            csp.domains[node2].remove(val1)
        except ValueError:
            changes = changes -1
        if changes:
            return True
    
    #if the secondary node only has one possible value
    if len(csp.domains[node2]) == 1:
        csp.boardboxes[node2] = csp.domains[node2][0]
        try:
            csp.domains[node1].remove(csp.domains[node2][0])
            return True
        except ValueError:
            return False
            
    if len(csp.domains[node1]) == 1:
        csp.boardboxes[node1] = csp.domains[node1][0]
        try:
            csp.domains[node2].remove(csp.domains[node1][0])
            return True
        except ValueError:
            return False
    
    return revised
        
        
def Backtrack(dictAssign,  csp):       
    if csp.hasUnassigned() == False:
        return csp
    original_csp = deepcopy(csp)
    MostLikelyToFail = original_csp.getMRV()
    for n in original_csp.domains[MostLikelyToFail]:
        validmove = original_csp.checkConsistency(MostLikelyToFail, n)
        if validmove: 
            dictAssign[MostLikelyToFail] =n
            result = Backtrack(dictAssign, original_csp)
            if result != False:
                return result
            else:
                original_csp = deepcopy(csp)
    return False

def SolveIt(startstate):
    B = csp(startstate)
    AC3(B)
    if B.isSolved():
        B.output()
        return B.solution
    else:
        if not B.isSolved():
            B.getUnassigned()
            puzzlesolution = Backtrack({}, B)
            if not puzzlesolution.isSolved():
                #print("failed to solve")
                pass
            else:
                puzzlesolution.output()
            return puzzlesolution.solution
        B.output()
        return B.solution

puzzle = sys.argv[1]
SolveIt(puzzle)
