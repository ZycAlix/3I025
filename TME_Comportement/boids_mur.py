#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# multirobot.py
# Contact (ce fichier uniquement): nicolas.bredeche(at)upmc.fr
# 
# Description:
#   Template pour simulation mono- et multi-robots type khepera/e-puck/thymio
#   Ce code utilise pySpriteWorld, développé par Yann Chevaleyre (U. Paris 13)
# 
# Dépendances:
#   Python 2.x
#   Matplotlib
#   Pygame
# 
# Historique: 
#   2016-03-28__23h23 - template pour 3i025 (IA&RO, UPMC, licence info)
#   2018-03-27__20h55 - réécriture de la fonction step(.), utilisation de valeurs normalisées (senseurs et effecteurs). Interface senseurs, protection du nombre de commandes de translation et de rotation (1 commande par appel de step(.) pour chacune)
#
# Aide: code utile
#   - Partie "variables globales": en particulier pour définir le nombre d'agents. La liste SensorBelt donne aussi les orientations des différentes capteurs de proximité.
#   - La méthode "step" de la classe Agent
#   - La fonction setupAgents (permet de placer les robots au début de la simulation)
#   - La fonction setupArena (permet de placer des obstacles au début de la simulation)
#   - il n'est pas conseillé de modifier les autres parties du code.
# 

from robosim import *
from random import random, shuffle
import time
import sys
import atexit
from itertools import count


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Aide                 '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

#game.setMaxTranslationSpeed(3) # entre -3 et 3
# size of arena: 
#   screenw,screenh = taille_terrain()
#   OU: screen_width,screen_height

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  variables globales   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

game = Game()

agents = []
screen_width=512 #512,768,... -- multiples de 32  
screen_height=512 #512,768,... -- multiples de 32
nbAgents = 40

maxSensorDistance = 30              # utilisé localement.
maxRotationSpeed = 5
maxTranslationSpeed = 1

SensorBelt = [-170,-80,-40,-20,+20,40,80,+170]  # angles en degres des senseurs (ordre clockwise)

maxIterations = -1 # infinite: -1

showSensors = True
frameskip = 0   # 0: no-skip. >1: skip n-1 frames
verbose = True

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Classe Agent/Robot   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

class Agent(object):
    
    agentIdCounter = 0 # use as static
    id = -1
    robot = -1
    name = "Equipe Alpha" # A modifier avec le nom de votre équipe

    translationValue = 0 # ne pas modifier directement
    rotationValue = 0 # ne pas modifier directement

    def __init__(self,robot):
        self.id = Agent.agentIdCounter
        Agent.agentIdCounter = Agent.agentIdCounter + 1
        #print "robot #", self.id, " -- init"
        self.robot = robot

    def getRobot(self):
        return self.robot

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def step(self):

        #print "robot #", self.id, " -- step"

        p = self.robot

        # actions
        # valeur de paramètre entre -1 et +1.
        # cette valeur sera converti ensuite entre:
        #  - pour setTranslation: entre -maxTranslationSpeed et +maxTranslationSpeed
        #  - pour setRotation: entre -maxRotationSpeed et +maxRotationSpeed
        # Attention:
        #   ces fonctions *programment* la commande motrice, mais *ne l'exécute pas*
        #   la dernière valeur allouée exécutée. Chaque fonction doit donc être appelé une seule fois.
        
        #On met d'abord hate_Wall en première priorité.
        sensor_infos = sensors[p]
        dist_min = 999
        index_min = -1

        for i, impact in enumerate(sensor_infos) : # impact est donc un namedtuple avec plein d'infos sur l'impact: namedtuple('RayImpactTuple', ['sprite','layer','x', 'y','dist_from_border','dist_from_center','rel_angle_degree','abs_angle_degree'])
            if impact.dist_from_border <= maxSensorDistance :
                if impact.layer == 'obstacle' :
                    if impact.dist_from_border < dist_min :
                        dist_min = impact.dist_from_border
                        index_min = i

        if index_min > 3 and dist_min <= maxSensorDistance:
            self.setRotationValue(-1)
            self.setTranslationValue(1)
        elif index_min <= 3 and dist_min <= maxSensorDistance and index_min >= 0:
            self.setRotationValue(1)
            self.setTranslationValue(1)
        # Ici, on a au total 3 règles : attraction, répulsion, orientation, on choisit le plus proche comme la condition.    
        else :
            sensor_infos = sensors[p]
            dist_min = 999
            index_min = -1

            for i, impact in enumerate(sensor_infos) : # impact est donc un namedtuple avec plein d'infos sur l'impact: namedtuple('RayImpactTuple', ['sprite','layer','x', 'y','dist_from_border','dist_from_center','rel_angle_degree','abs_angle_degree'])
                if impact.dist_from_border <= maxSensorDistance :
                    if impact.layer == 'joueur':
                        if impact.dist_from_border < dist_min :
                            dist_min = impact.dist_from_border
                            index_min = i

            if dist_min <= maxSensorDistance :
                if self.id % 3 == 0 : # règle attraction 
                    if index_min > 3 :
                        self.setRotationValue(1)
                        self.setTranslationValue(1)
                    else :
                        self.setRotationValue(-1)
                        self.setTranslationValue(1)
                elif self.id % 3 == 1 : #règle répulsion
                    if index_min > 3 :
                        self.setRotationValue(-1)
                        self.setTranslationValue(1)
                    else :
                        self.setRotationValue(1)
                        self.setTranslationValue(1)
                else : # règle orientation
                    robot_plus_proche = sensor_infos[index_min].sprite
                    orientation = robot_plus_proche.orientation()
                    if orientation - p.orientation() > 0 and orientation - p.orientation() <= 180 : # on sait que l'orientation est positive et absolue
                        self.setRotationValue(-1)
                    elif orientation - p.orientation() < 0 and orientation - p.orientation() >= -180 :
                        self.setRotationValue(1)
                    elif orientation - p.orientation() > 180 and orientation - p.orientation() < 360 :
                        self.setRotationValue(1)
                    elif orientation - p.orientation() < -180 and orientation - p.orientation() > -360 :
                        self.setRotationValue(-1)
                    else : 
                        print("Current robot "+ str(self.id)+ " and his closet neighboor "+ str(robot_plus_proche.numero)+" have the same orientation")# Même orientation, on fait rien 

            else : # donne une aleatoire orientation vers laquelle le robot essaye de bouguer
                self.setRotationValue(random()*2 -1)
                self.setTranslationValue(1)
                print("++++++++++++++++++++") 

        # monitoring - affiche diverses informations sur l'agent et ce qu'il voit.
        # pour ne pas surcharger l'affichage, je ne fais ca que pour le player 1
        if verbose == True and self.id == 0:

            efface()    # j'efface le cercle bleu de l'image d'avant
            color( (0,0,255) )
            circle( *game.player.get_centroid() , r = 22) # je dessine un rond bleu autour de ce robot

            # monitoring (optionnel - changer la valeur de verbose)
            print ("\n# Current robot at " + str(p.get_centroid()) + " with orientation " + str(p.orientation()))

            sensor_infos = sensors[p] # sensor_infos est une liste de namedtuple (un par capteur).
            for i,impact in enumerate(sensors[p]):  # impact est donc un namedtuple avec plein d'infos sur l'impact: namedtuple('RayImpactTuple', ['sprite','layer','x', 'y','dist_from_border','dist_from_center','rel_angle_degree','abs_angle_degree'])
                if impact.dist_from_border > maxSensorDistance:
                    print ("- sensor #" + str(i) + " touches nothing")
                else:
                    print ("- sensor #" + str(i) + " touches something at distance " + str(impact.dist_from_border))
                    if impact.layer == 'joueur':
                        playerTMP = impact.sprite
                        print ("  - type: robot no." + str(playerTMP.numero))
                        print ("    - x,y = " + str( playerTMP.get_centroid() ) + ")" )# renvoi un tuple
                        print ("    - orientation = " + str( playerTMP.orientation() ) + ")") # p/r au "nord"
                    elif impact.layer == 'obstacle':
                        print ("  - type obstacle")
                    else:
                        print ("  - type boundary of window")
        return

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


    def getDistanceAtSensor(self,id):
        sensor_infos = sensors[self.robot] # sensor_infos est une liste de namedtuple (un par capteur).
        return min(sensor_infos[id].dist_from_border,maxSensorDistance) / maxSensorDistance

    def getObjectTypeAtSensor(self,id):
        if sensors[self.robot][id].dist_from_border > maxSensorDistance:
            return 0 # nothing
        elif sensors[self.robot][id].layer == 'joueur':
            return 2 # robot
        else:
            return 1 # wall/border

    def getRobotInfoAtSensor(self,id):
        if sensors[self.robot][id].dist_from_border < maxSensorDistance and sensors[self.robot][id].layer == 'joueur':
            otherRobot = sensors[self.robot][id].sprite
            info = {'id': otherRobot.numero, 'centroid': otherRobot.get_centroid(), 'orientation': otherRobot.orientation()}
            return info
        else:
            #print "[WARNING] getPlayerInfoAtSensor(.): not a robot!"
            return None

    def setTranslationValue(self,value):
        if value > 1:
            print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = maxTranslationSpeed
        elif value < -1:
            print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = -maxTranslationSpeed
        else:
            value = value * maxTranslationSpeed
        self.robot.forward(value)

    def setRotationValue(self,value):
        if value > 1:
            print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = maxRotationSpeed
        elif value < -1:
            print ("[WARNING] translation value not in [-1,+1]. Normalizing.")
            value = -maxRotationSpeed
        else:
            value = value * maxRotationSpeed
        self.robot.rotate(value)


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Fonctions init/step  '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

def setupAgents():
    global screen_width, screen_height, nbAgents, agents, game

    # Make agents
    nbAgentsCreated = 0
    for i in range(nbAgents):
        while True:
            p = -1
            while p == -1: # p renvoi -1 s'il n'est pas possible de placer le robot ici (obstacle)
                p = game.add_players( (random()*screen_width , random()*screen_height) , None , tiled=False)
            if p:
                p.oriente( random()*360 )
                p.numero = nbAgentsCreated
                nbAgentsCreated = nbAgentsCreated + 1
                agents.append(Agent(p))
                break
    game.mainiteration()


def setupArena():
    for i in range(6,13):
        addObstacle(row=3,col=i)
    for i in range(3,10):
        addObstacle(row=12,col=i)
    addObstacle(row=4,col=12)
    addObstacle(row=5,col=12)
    addObstacle(row=6,col=12)
    addObstacle(row=11,col=3)
    addObstacle(row=10,col=3)
    addObstacle(row=9,col=3)



def stepWorld():
    # chaque agent se met à jour. L'ordre de mise à jour change à chaque fois (permet d'éviter des effets d'ordre).
    shuffledIndexes = [i for i in range(len(agents))]
    shuffle(shuffledIndexes)
    for i in range(len(agents)):
        agents[shuffledIndexes[i]].step()
        agents[shuffledIndexes[i]].getRobot().forward(agents[shuffledIndexes[i]].translationValue)
        agents[shuffledIndexes[i]].getRobot().rotate(agents[shuffledIndexes[i]].rotationValue)
    return


'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Fonctions internes   '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

def addObstacle(row,col):
    # le sprite situe colone 13, ligne 0 sur le spritesheet
    game.add_new_sprite('obstacle',tileid=(0,13),xy=(col,row),tiled=True)

class MyTurtle(Turtle): # also: limit robot speed through this derived class
    maxRotationSpeed = maxRotationSpeed # 10, 10000, etc.
    def rotate(self,a):
        mx = MyTurtle.maxRotationSpeed
        Turtle.rotate(self, max(-mx,min(a,mx)))

def onExit():
    print ("\n[Terminated]")

'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''
'''  Main loop            '''
'''''''''''''''''''''''''''''
'''''''''''''''''''''''''''''

init('empty',MyTurtle,screen_width,screen_height) # display is re-dimensioned, turtle acts as a template to create new players/robots
game.auto_refresh = False # display will be updated only if game.mainiteration() is called
game.frameskip = frameskip
atexit.register(onExit)

setupArena()
setupAgents()
game.mainiteration()

iteration = 0
while iteration != maxIterations:
    # c'est plus rapide d'appeler cette fonction une fois pour toute car elle doit recalculer le masque de collision,
    # ce qui est lourd....
    sensors = throw_rays_for_many_players(game,game.layers['joueur'],SensorBelt,max_radius = maxSensorDistance+game.player.diametre_robot() , show_rays=showSensors)
    stepWorld()
    game.mainiteration()
    iteration = iteration + 1
