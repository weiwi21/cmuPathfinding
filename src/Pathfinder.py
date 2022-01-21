from cmu_112_graphics import *
import math

# nodes class same as factory
class Node(object):  # node class with id number, location tuple, neighbor dictionary
    def __init__(self, id, location, neighbors):
        self.id = id
        self.location = location
        self.neighbors = neighbors
        self.previous = None


class Building(Node):  # node subclass with building name
    def __init__(self, id, location, neighbors, name):
        super().__init__(id, location, neighbors)
        self.name = name

    def __repr__(self):
        x = str(self.location[0])
        y = str(self.location[1])
        strBuilder = "$" + str(self.id) + ";" + f"({x},{y});"
        for neighbor in self.neighbors:
            strBuilder = strBuilder + str(neighbor) + ":" + str(self.neighbors[neighbor]) + ","
        strBuilder = strBuilder[:-1] + ";" + self.name
        return strBuilder


class Crosswalk(Node):  # node subclass "Crosswalk"
    def __init__(self, id, location, neighbors):
        super().__init__(id, location, neighbors)

    def __repr__(self):
        x = str(self.location[0])
        y = str(self.location[1])
        strBuilder = "$" + str(self.id) + ";" + f"({x},{y});"
        for neighbor in self.neighbors:
            strBuilder = strBuilder + str(neighbor) + ":" + str(self.neighbors[neighbor]) + ","
        strBuilder = strBuilder[:-1]
        return strBuilder


class Intersection(Node):  # node subclass "Intersection"
    def __init__(self, id, location, neighbors):
        super().__init__(id, location, neighbors)

    def __repr__(self):
        x = str(self.location[0])
        y = str(self.location[1])
        strBuilder = "$" + str(self.id) + ";" + f"({x},{y});"
        for neighbor in self.neighbors:
            strBuilder = (strBuilder + str(neighbor) + ":" + str(self.neighbors[neighbor])
                          + ",")
        return strBuilder[:-1]

# read in the file and returns the numbers
def readFile(filePath):
    file1 = open(filePath, "r")
    lines = file1.readlines()
    return lines


# takes in the list and then turns it into a list of node objects
def makeNodeList(filePath):
    lines = readFile(filePath)[0]
    nodeList = []
    for line in lines.split("$")[1:]:
        nodeDict = {}
        params = line.split(";")
        id = int(params[0])
        location = params[1].split(",")
        x = int(location[0])
        y = int(location[1])
        index = 2
        neighbors = params[index]
        if neighbors.count(":") > 0:
            index += 1
            for neighbor in neighbors.split(","):
                vals = neighbor.split(":")
                key = int(vals[0])
                value = float(vals[1])
                nodeDict[key] = value
        flavor = params[index]
        if flavor == "intersection":
            node = Intersection(id, (x, y), nodeDict)
        elif flavor == "building":
            name = params[index + 1]
            node = Building(id, (x, y), nodeDict, name)
        else:
            node = Crosswalk(id, (x, y), nodeDict)
        nodeList.append(node)
    return nodeList


# set some base variables
def appStarted(app):
    app.nodeList = makeNodeList("nodes.txt")
    app.setStart = False
    app.start = 0
    app.setEnd = False
    app.end = 0
    app.nodeChoiceFailed = False
    app.path = []
    app.r = 10
    app.timerDelay = 0
    app.i = 0
    app.delayedPath = []
    app.pathLength = 0
    app.mapScale = 1.4371
    app.mapImage = app.loadImage('cmuMap.png')


# timer fired for making the path appear step by step
def timerFired(app):
    app.timerDelay += 1
    if app.timerDelay % 5 == 0 and len(app.path) > 0:
        app.delayedPath.append(app.path.pop(0))
    if len(app.path) == 0:
        app.printDistance = True


# used to find which 2 nodes to pathfind between
def mousePressed(app, event):
    if app.setStart or app.setEnd:
        x, y = event.x, event.y
        for node in app.nodeList:
            if distance(x, y, node.location[0], node.location[1]) <= app.r:
                if app.setStart:
                    app.start = node.id
                    app.setStart = False
                    app.setEnd = True
                    break
                else:
                    app.end = node.id
                    app.setStart = False
                    app.setEnd = False
                    app.nodeChoiceFailed = False
                    if app.start == app.end:
                        app.setEnd = True
                        app.nodeChoiceFailed = True
                    else:
                        aStar(app, app.start, app.end)
                        app.timerDelay = 0
                    break


# used to start the info
def keyPressed(app, event):
    if event.key == "s":
        resetValues(app)
        app.setStart = True


# reset some values that are changed, called when generating new path
def resetValues(app):
    app.setStart = False
    app.start = 0
    app.setEnd = False
    app.end = 0
    app.path = []
    app.delayedPath = []
    app.pathLength = 0
    for node in app.nodeList:
        node.previous = None


# a star pathfinding
def aStar(app, start, end):
    nodeList = app.nodeList
    startNode = nodeList[start - 1]
    endNode = nodeList[end - 1]
    openList = [startNode]
    closedList = []
    while len(openList) > 0:
        currentNode = openList[0]
        currentIndex = 0

        nodeMin = float("inf")
        for i, exploreNode in enumerate(openList):
            back = backTrack(exploreNode)
            straightLine = distance(exploreNode.location[0], exploreNode.location[1],
                                    endNode.location[0], endNode.location[1])
            cost = back + straightLine
            if cost < nodeMin:
                nodeMin = cost
                currentNode = exploreNode
                currentIndex = i

        openList.pop(currentIndex)
        closedList.append(currentNode)

        if currentNode.id == endNode.id:
            app.path = getPath(endNode)
            app.pathLength = round(backTrack(endNode) * app.mapScale, 2)
            return

        neighbors = currentNode.neighbors

        for neighbor in neighbors:
            neighborNode = nodeList[neighbor - 1]
            if neighborNode in closedList:
                continue
            elif neighborNode in openList:
                if backTrack(neighborNode) > backTrack(currentNode) + neighbors[neighbor]:
                    neighborNode.previous = currentNode
            else:
                openList.append(neighborNode)
                neighborNode.previous = currentNode


# recursively finds and returns a list of node objects
def getPath(node):
    if node.previous is None:
        return [node]
    else:
        return getPath(node.previous) + [node]


# recursively finds the cost it takes to get to a certain point from the start
def backTrack(node):
    if node.previous is None:
        return 0
    else:
        nodeId = node.id
        previousNode = node.previous
        return backTrack(node.previous) + previousNode.neighbors[nodeId]


# distance
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# drawing nodes, path, distance, and other informations
def redrawAll(app, canvas):
    canvas.create_image(app.width, app.height, image=ImageTk.PhotoImage(app.mapImage),
                        anchor="se")
    if not app.setStart and not app.setEnd:
        canvas.create_text(app.width / 2, 70, text="Please press \'s\' to set a start and end point", font="Arial 25")
    drawPath(app, canvas)
    drawNodes(app, canvas)
    drawChoiceFailed(app, canvas)
    drawTotalDistance(app, canvas)
    if app.setStart:
        canvas.create_text(app.width / 2, 70, text="Please select a starting point", font="Arial 25")
    elif app.setEnd:
        canvas.create_text(app.width / 2, 70, text="Please select an ending point", font="Arial 25")


def drawChoiceFailed(app, canvas):
    if app.nodeChoiceFailed:
        canvas.create_text(app.width / 2, 100,
                           text="Please choose an end point that is different from the starting point", font="Arial 25")


def drawTotalDistance(app, canvas):
    if app.pathLength > 0:
        canvas.create_text(app.width / 10, 100, text=str(app.pathLength) + " Meters", font="Helvetica 20")


def drawPath(app, canvas):
    for x in range(len(app.delayedPath) - 1):
        node1 = app.delayedPath[x]
        node2 = app.delayedPath[x + 1]
        canvas.create_line(node1.location[0], node1.location[1],
                           node2.location[0], node2.location[1],
                           fill="red", width = 5)


def drawNodes(app, canvas):
    for node in app.nodeList:
        x = node.location[0]
        y = node.location[1]
        canvas.create_oval(x - app.r, y - app.r, x + app.r, y + app.r, fill='pink')
        canvas.create_text(x, y, text=str(node.id), font='Arial 10')

    if app.start != 0:
        startNode = app.nodeList[app.start - 1]
        x = startNode.location[0]
        y = startNode.location[1]
        canvas.create_oval(x - app.r, y - app.r, x + app.r, y + app.r, fill='green')
        canvas.create_text(x, y, text=str(startNode.id), font='Arial 10')

    if app.end != 0:
        endNode = app.nodeList[app.end - 1]
        x = endNode.location[0]
        y = endNode.location[1]
        canvas.create_oval(x - app.r, y - app.r, x + app.r, y + app.r, fill='red')
        canvas.create_text(x, y, text=str(endNode.id), font='Arial 10')


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


runApp(width=1059, height=882)