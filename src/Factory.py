from cmu_112_graphics import *
import math


class Node(object):  # node class with id number, location tuple, neighbor dictionary
    def __init__(self, id, location, neighbors):
        self.id = id
        self.location = location
        self.neighbors = neighbors


class Building(Node):  # node subclass with building name
    def __init__(self, id, location, neighbors, name):
        super().__init__(id, location, neighbors)
        self.name = name

    # returns the string in the format that it will be stored into the txt file
    def __repr__(self):
        x = str(self.location[0])
        y = str(self.location[1])
        strBuilder = "$" + str(self.id) + ";" + f"{x},{y};"
        for neighbor in self.neighbors:
            strBuilder = strBuilder + str(neighbor) + ":" + str(self.neighbors[neighbor]) + ","
        strBuilder = strBuilder[:-1] + ";building;" + self.name
        return strBuilder


class Crosswalk(Node):  # node subclass "Crosswalk"
    def __init__(self, id, location, neighbors):
        super().__init__(id, location, neighbors)

    # returns the string in the format that it will be stored into the txt file
    def __repr__(self):
        x = str(self.location[0])
        y = str(self.location[1])
        strBuilder = "$" + str(self.id) + ";" + f"{x},{y};"
        for neighbor in self.neighbors:
            strBuilder = strBuilder + str(neighbor) + ":" + str(self.neighbors[neighbor]) + ","
        strBuilder = strBuilder[:-1] + ";crosswalk"
        return strBuilder


class Intersection(Node):  # node subclass "Intersection"
    def __init__(self, id, location, neighbors):
        super().__init__(id, location, neighbors)

    # returns the string in the format that it will be stored into the txt file
    def __repr__(self):
        x = str(self.location[0])
        y = str(self.location[1])
        strBuilder = "$" + str(self.id) + ";" + f"{x},{y};"
        for neighbor in self.neighbors:
            strBuilder = (strBuilder + str(neighbor) + ":" + str(self.neighbors[neighbor])
                          + ",")
        return strBuilder[:-1] + ";intersection"

# stores some base values
def appStarted(app):
    # keeps track of current nodes that were created as well as ID
    app.id = 1
    app.nodeList = []
    # saves image of the cmu map
    app.mapImage = app.loadImage('cmuMap.png')
    # stores values and booleans for node that is currently being created
    app.startNode = True
    app.x, app.y = 0, 0
    app.startFlavor = False
    app.flavor = ""
    app.startName = False
    app.name = ""
    app.startNeighbor = False
    app.neighbors = {}
    app.neighborId = ""
    app.validNeighbor = True
    app.r = 10
    # opens the file that will be read to.
    app.f = open("nodes.txt", "x")


def mousePressed(app, event):  # sets position of node if we are in set node mode
    if app.startNode:
        app.x, app.y = event.x, event.y
        app.startFlavor = True
        app.startNode = False


# if the key press is down, print the list of nodes
def keyPressed(app, event):
    if event.key == "Down":
        print(app.nodeList)

    # if the key press is up, write to file as long as there is no node being created
    elif event.key == "Up" and app.startNode:
        app.displayPrint = True
        for node in app.nodeList:
            val = str(node)
            app.f.write(val)

        app.f.close()
    # takes input for the type of node
    elif app.startFlavor:
        if event.key == "0":
            app.flavor = "intersection"
        elif event.key == "1":
            app.flavor = "building"
        elif event.key == "2":
            app.flavor = "crosswalk"
        elif event.key == "Escape":
            app.startFlavor = False
            if app.flavor == "building":
                app.startName = True
            else:
                app.startNeighbor = True
    # takes input for the name
    elif app.startName:
        if event.key == "Escape":
            app.startName = False
            app.startNeighbor = True
        else:
            app.name += event.key
    # starts neighbor select
    elif app.startNeighbor:
        if len(app.nodeList) == 0:
            if app.flavor == "intersection":
                node = Intersection(app.id, (app.x, app.y), {})
            elif app.flavor == "crosswalk":
                node = Crosswalk(app.id, (app.x, app.y), {})
            else:
                node = Building(app.id, (app.x, app.y), {}, app.name)
            app.nodeList.append(node)
            app.startNeighbor = False
            app.startNode = True
            resetValues(app)
            app.id += 1
        else:
            if event.key == "Enter":
                if app.neighborId.isdigit() and int(app.neighborId) < app.id:
                    app.validNeighbor = True
                    app.neighborId = int(app.neighborId)
                    x = app.nodeList[app.neighborId - 1].location[0]
                    y = app.nodeList[app.neighborId - 1].location[1]
                    dis = distance(app.x, app.y, x, y)
                    app.neighbors[app.neighborId] = dis
                    app.nodeList[app.neighborId - 1].neighbors[app.id] = dis
                    app.neighborId = ""
                else:
                    app.validNeighbor = False
                    app.neighborId = ""
            # creates the nodes and adds it to the list
            elif event.key == "Escape":
                if app.flavor == "intersection":
                    node = Intersection(app.id, (app.x, app.y), app.neighbors)
                elif app.flavor == "crosswalk":
                    node = Crosswalk(app.id, (app.x, app.y), app.neighbors)
                else:
                    node = Building(app.id, (app.x, app.y), app.neighbors, app.name)
                app.nodeList.append(node)
                app.startNeighbor = False
                app.startNode = True
                app.id += 1
                resetValues(app)
            else:
                app.neighborId += event.key

# finds distance between 2 points
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# resets the values
def resetValues(app):
    app.name = ""
    app.flavor = ""
    app.neighbors = {}
    app.neighorId = ""
    app.validNeighbor = True


# draws all of the nodes and prompts for what to input
def redrawAll(app, canvas):
    canvas.create_image(app.width, app.height, image=ImageTk.PhotoImage(app.mapImage),
                        anchor="se")
    drawNodes(app, canvas)
    if (app.startNode):
        drawStartNode(app, canvas)
    if (app.startFlavor):
        drawStartFlavor(app, canvas)
    if (app.startNeighbor and len(app.nodeList) != 0):
        drawStartNeighbor(app, canvas)
    if (app.startName):
        drawStartName(app, canvas)


# loops through all the nodes and displays it
def drawNodes(app, canvas):
    for node in app.nodeList:
        x = node.location[0]
        y = node.location[1]
        canvas.create_oval(x - app.r, y - app.r, x + app.r, y + app.r, fill='pink')
        canvas.create_text(x, y, text=str(node.id), font='Arial 10')
    if app.startNeighbor and len(app.nodeList) != 0:
        canvas.create_oval(app.x - app.r, app.y - app.r, app.x + app.r, app.y + app.r,
                           fill='purple')
        canvas.create_text(app.x, app.y, text=str(app.id), font='Arial 10')


# draws the current node as a different node.
def drawStartNode(app, canvas):
    x = int(app.width / 2)
    y = app.height / 10
    canvas.create_text(x, y, text="Please select a node with mouse press",
                       font="Arial 30")


# draw the words for the flavor
def drawStartFlavor(app, canvas):
    x = int(app.width / 2)
    y = app.height / 10
    canvas.create_text(x, y, text='''Please input a flavor (0 = intersection, 
                        1 = building, 2 = crosswalk, click escape when done)''',
                       font="Arial 30")


# draws the neighbor text to prompt the input
def drawStartNeighbor(app, canvas):
    x = int(app.width / 2)
    y = app.height / 10
    canvas.create_text(x, y, text="Input neighbor ID", font="Arial 30")


# draw start name prompt
def drawStartName(app, canvas):
    x = int(app.width / 2)
    y = app.height / 10
    canvas.create_text(x, y, text="Type in name:" + app.name,
                       font="Arial 30")

# run app
runApp(width=1059, height=882)