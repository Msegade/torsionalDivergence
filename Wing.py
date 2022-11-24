import numpy as np
import tables 

class Wing:

    def __init__(self, span, chords, h5FileName):

        
        self.span = span
        self.yPos = np.linspace(0, span, 11)
        self.rootChord = chords[0]
        self.tipChord = chords[1]

        h5file = tables.open_file(h5FileName, 'r')
        self.nodes = h5file.root.NASTRAN.INPUT.NODE.GRID.read()
        h5file.close()

        self.setDict = {}

    @property
    def chords(self):

        rate = (self.rootChord-self.tipChord)/self.span
        chords = [self.rootChord-rate*y for y in self.yPos]

        return chords

    def getNodesRbe3(self, tol=0.1):
        '''
            Get a fixed distance if tol=float
            get tributary lengths if tol=ADAPT
        '''
        yPos = self.yPos[1:]
        n = len(yPos)

        if isinstance(tol, float):
            rTols = [tol]*n
            lTols = [tol]*n
        elif tol=='ADAPT':
            lTols = self.getTributaryLengths(yPos, 'left')
            rTols = self.getTributaryLengths(yPos, 'right')

        ypNodes = self.nodes['X'][:,1]
        setsRbe3 = []
        for yP, (lTol, rTol) in zip(yPos, zip(lTols, rTols)):
            lBound = yP - lTol
            uBound = yP + rTol
            indexes = np.where(np.logical_and(ypNodes>=lBound, ypNodes < uBound))
            setsRbe3.append(self.nodes[indexes])

        return setsRbe3

    def getTributaryLengths(self, yPos, side):

        widths = np.append(yPos[0], np.diff(yPos))
        tol = []
        if side == 'left':
            tol = [w/2 for w in widths[1:]]
            # First width covered by first airfoil
            tol.insert(0, widths[0])
        if side == 'right':
            tol = [w/2 for w in widths[1:]]
            # No elements to the right of the last node
            tol.append(0.0)
        return tol

    def addSet(self, setNumber, nodeIds, coords):

        nDict = {'ids': nodeIds, 'coords': coords}
        self.setDict[setNumber] = nDict
