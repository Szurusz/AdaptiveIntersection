from os import times
import random
import time
import threading
import pygame
import sys
import math

from pygame.math import enable_swizzling
from util import blit_rotate_center

from pygame import image
from pygame import color
from pygame.constants import K_ESCAPE
from pygame.transform import rotate

# Definiowanie szybkosci symulacji
clock = pygame.time.Clock()

# Utworzenie grup Sprites
spriteGroup = pygame.sprite.OrderedUpdates()
textboxGroup = pygame.sprite.OrderedUpdates()

# tlo
backgroundImage=pygame.image.load('images/intersection.png') 

# Wykorzystywane kolory
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
gray = (99,100,102)
backgroundGreen = (19, 103, 52)
red = (255, 0, 0)

# Zaladowanie wygladu swiatel
UPredSignal = pygame.image.load('images/signals/red.png')
RIGHTredSignal = pygame.transform.rotate(UPredSignal, 90)
DOWNredSignal = pygame.transform.rotate(UPredSignal, 180)
LEFTredSignal = pygame.transform.rotate(UPredSignal, 270)

UPyellowSignal = pygame.image.load('images/signals/yellow.png')
RIGHTyellowSignal = pygame.transform.rotate(UPyellowSignal, 90)
DOWNyellowSignal = pygame.transform.rotate(UPyellowSignal, 180)
LEFTyellowSignal  = pygame.transform.rotate(UPyellowSignal, 270)

UPredyellowSignal = pygame.image.load('images/signals/redyellow.png')
RIGHTredyellowSignal = pygame.transform.rotate(UPredyellowSignal, 90)
DOWNredyellowSignal = pygame.transform.rotate(UPredyellowSignal, 180)
LEFTredyellowSignal  = pygame.transform.rotate(UPredyellowSignal, 270)

UPgreenSignal = pygame.image.load('images/signals/green.png')
RIGHTgreenSignal = pygame.transform.rotate(UPgreenSignal, 90)
DOWNgreenSignal = pygame.transform.rotate(UPgreenSignal, 180)
LEFTgreenSignal   = pygame.transform.rotate(UPgreenSignal, 270)

# Zaladowanie wygladu znakow
scale = (40,40)
sign1_image = pygame.image.load('images/signs/left.png')
UPsign1 = pygame.transform.scale(sign1_image,scale)
LEFTsign1 = pygame.transform.rotate(UPsign1, 90)
DOWNsign1 = pygame.transform.rotate(UPsign1,180)
RIGHTsign1 = pygame.transform.rotate(UPsign1,270)

sign2_image = pygame.image.load('images/signs/stright.png')
UPsign2 = pygame.transform.scale(sign2_image,scale)
LEFTsign2 = pygame.transform.rotate(UPsign2, 90)
DOWNsign2 = pygame.transform.rotate(UPsign2, 180)
RIGHTsign2 = pygame.transform.rotate(UPsign2, 270)

sign3_image = pygame.image.load('images/signs/turn_right.png')
UPsign3 = pygame.transform.scale(sign3_image,scale)
LEFTsign3 = pygame.transform.rotate(UPsign3, 90)
DOWNsign3 = pygame.transform.rotate(UPsign3, 180)
RIGHTsign3 = pygame.transform.rotate(UPsign3, 270)

# Zaladowanie ikon pory dnia
morning = pygame.image.load('images/timeDay/morning.png')
afternoon = pygame.image.load('images/timeDay/afternoon.png')
evening = pygame.image.load('images/timeDay/evening.png')
night = pygame.image.load('images/timeDay/night.png')

# Pobranie wymiarow tla
screenWidth, screenHeight = backgroundImage.get_width(), backgroundImage.get_height()

# Ustawie rozmiaru okna o wymiarach tla
screenSize = (screenWidth, screenHeight)
screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption("ADAPTACJA")

# Ustawienie tla na skrzyzowanie
background = pygame.image.load('images/intersection.png').convert()

# Parametry semaforow
signals = []    # tworzenie tablicy sygnalow
noOfSignals = 4 # ilosc cykli sygnalowych (poziomy > pionowy > skret w lewo poziomo > skret w lewo pionowo)
currentGreen = 0  # zmienna okreslajaca ktory cykl jest w tej chwili posiada swiatlo zielone
nextGreen = (currentGreen+1)%noOfSignals    # zmienna okreslajaca nastepny cykl dla ktorego swiatlo bedzie zielone
currentYellow = 0   # zmienna okreslajaca ktory z cykli posiada zolte/czerwone swiatlo
nextYellow = 0 # zmienna okreslajaca zmiane czrwonego swiatla na zolte/zielone

# Zmienna zliczajaca ilosc pojazdow przed semaforem (widocznych przez czujnik)
global numberOfDetectCars
numberOfDetectCars = {'right': [0,0,0,0], 'down': [0,0,0,0], 'left': [0,0,0,0], 'up': [0,0,0,0]}

# zmienne zliczajace ilosc pojazdow przed semaforem (ogolnie)
global numberOfCars
numberOfCars = {'right': [0,0,0,0], 'down': [0,0,0,0], 'left': [0,0,0,0], 'up': [0,0,0,0]}

# zmienna pory dnia
global timeDay  # zmienna globalna okreslajaca pore dnia
t = 0   # domyslny ustawiony czas to rano
timeOfDay = ['morning','afternoon','evening', 'night'] # pory dnia (rano, popoludnie, wieczor, noc)
timeDay = timeOfDay[t] # ustawienie pory dnia

# Domyslne czasy swiatel
if timeDay == 'morning' or timeDay == 'evening':
    defaultGreen = {0:10, 1:10, 2:5, 3:5} # ile trwa zielony
elif timeDay == ' afternoon':
    defaultGreen = {0:10, 1:10, 2:10, 3:10}
elif timeDay == 'night':
    defaultGreen = {0:5,1:5,2:5,3:5}

# Czas swiatla zoltego 
defaultYellow = 3 # domyslnie zolty

# Tablica pojazdow, ktore przejechaly przez skrzyzowanie
global after
after = {'right': {0:[], 1:[], 2:[], 3:[]}, 'down': {0:[], 1:[], 2:[], 3:[]}, 'left': {0:[], 1:[], 2:[], 3:[]}, 'up': {0:[], 1:[], 2:[], 3:[]}}

# Pierwsze wspolrzedne tworzenia samochodow
x = {'right':[0,0,0,0], 'down':[755,666,625,586], 'left':[1400,1400,1400,1400], 'up':[602,711,752,790]}
y = {'right':[348,410,448,484], 'down':[0,0,0,0], 'left':[265,369,334,295], 'up':[800,800,800,800]}

# Tworzenie pustych setow danych poszczegolnych pojazdow
vehicles = {'right': {0:[], 1:[], 2:[], 3:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 3:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 3:[],'crossed':0}, 'up': {0:[], 1:[], 2:[], 3:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'} # rodzaje pojazdow
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'} # kierunki pojazdow
destinationNumbers = {0:'turn_right',1:'turn_left',2:'stright'} # przeznaczenie pojazdu

# Wspolrzedne semaforow i ich licznikow
signalCoods = [(435,590),(465,145),(435,540),(515,145),(880,177),(905,565),(880,225),(853,565),(435,640),(880,130),(415,145),(955,565)]
signalTimerCoods = [(390,595),(465,115),(980,226),(852,660),(980,180),(905,660),(390,545),(515,115),(390,645),(980,133),(415,115),(955,660)]

# Wsporzedne miejsc zatrzymania pojazdow przed semaforem
stopLines = {'right': 550, 'down': 270, 'left': 850, 'up': 540}
defaultStop = {'right': 540, 'down': 260, 'left': 860, 'up': 550}

# Przestrzen pomiedzy samochodowami
movingGap = 10   # w trakcie ruchu

# Inicjalizacja pygame i symulacji zwierajacej obiekty typu sprite
pygame.init()
simulation = pygame.sprite.Group()

# Klasa semaforu
class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red       # swiatlo czerowne
        self.yellow = yellow # swiatlo zolte
        self.green = green   # swiatlo zielone
        self.signalText = "" # licznik

# Klasa pojadu
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, laneAfter, vehicleClass, directionNumber, direction, directionAfter, destinationNumber, destination, maxSpeedVehicle, actualSpeed, accelerationVehicle, whenStart, whenStop, whenBraking, natureDriver, techcond):
        pygame.sprite.Sprite.__init__(self)
        path = "images/" + direction + "/" + vehicleClass + ".png" # sciezka obrazu
        self.image = pygame.image.load(path)  # obraz
        self.natureDriver = natureDriver # zmienna humoru kierowcy
        self.techcond = techcond # zmienna stanu technicznego
        self.maxSpeed = maxSpeedVehicle # maksymalna predkosc
        self.angle = 0  # kat pojazdu
        self.lane = lane  # pas
        self.actualSpeed = actualSpeed  # aktualna predkosc
        self.vehicleClass = vehicleClass # ogolna klasa
        self.accelerationVehicle = accelerationVehicle # przyspieszenie
        self.whenStart = whenStart  # odstep po przekroczeniu, ktorego ruszy pojazd i odleglosc od poprzedzajacego pojazdu w trakcie ruchu
        self.whenStop = whenStop # gdzie samochod ma sie zatrzymac
        self.whenBraking = whenBraking # odstep przy ktorym pojazd zaczyna hamowac
        self.destinationNumber = destinationNumber # liczba definiujaca przeznaczenie 
        self.destination = destination # przeznaczenie pojazdu
        self.directionNumber = directionNumber # numer okreslajacy przeznaczenie
        self.direction = direction # kierunek
        self.x = x[direction][lane] # wspolrzedna x
        self.y = y[direction][lane] # wspolrzedna y
        self.selfRotated = [] # tablica rotacji
        self.selfRotated_rect = [] # talbica rotacji obszaru
        self.crossed = 0 # zmienna przejechania linii zatrzymania
        vehicles[direction][lane].append(self) # przypisanie do tablicy stworzonego pojazdu
        self.index = len(vehicles[direction][lane]) - 1 # przypisanie do pojazdu indexu w celu zachowania kolejnosci przejazdu
        self.laneAfter = laneAfter # zajmowany pas po skrecie
        self.directionAfter = directionAfter # kierunek po skrecie
        self.indexAfter = 0 # index po skrecie
        self.turningleft = 0 # zmienna skretu pojazdu w lewo
        self.turningright = 0 # zmienna skretu pojazdu w prawo
        self.counterflag = 0
        self.detectcounterflag = 0 # flaga umozliwiajaca zliczanie pojazdow przed swiatlami
        self.boundariesCount = [0,0] # granica zliczania pojazdu
        self.countAfter = 0 # flaga zliczania pojazdów po skrzyżowaniu 

        # Definiowanie miejsca zatrzymania pojazdow
        if(self.index != 0 and vehicles[direction][lane][self.index-1].crossed==0): 
            # ustawienie wzgledem kierunku miejsca zatrzymania sie kolejnych pojazdow
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().width - self.whenStop
            elif(direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().width + self.whenStop
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].image.get_rect().height - self.whenStop
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].image.get_rect().height + self.whenStop
        else:
            self.stop = defaultStop[direction]
            
        # Ustawienie miejsca tworzenia nowych pojazdow
        if(direction=='right'):
            temp = self.image.get_rect().width + self.whenStop
            x[direction][lane] -= temp
        elif(direction=='left'):
            temp = self.image.get_rect().width + self.whenStop
            x[direction][lane] += temp
        elif(direction=='down'):
            temp = self.image.get_rect().height + self.whenStop
            y[direction][lane] -= temp
        elif(direction=='up'):
            temp = self.image.get_rect().height + self.whenStop
            y[direction][lane] += temp
        simulation.add(self)
    
    # Wyswietlenie pojazdu na tle
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))
        
    # Ruch pojazdow
    def move(self):
        if(self.direction=='right'):
                # Zliczanie ilosci pojazdow ogolnie
                if self.crossed == 0 and self.counterflag == 0:
                    self.counterflag = 1
                    numberOfCars[self.direction][self.lane] = numberOfCars[self.direction][self.lane] + 1
                if self.crossed == 1 and self.counterflag == 1:
                    self.counterflag = 0
                    numberOfCars[self.direction][self.lane] = numberOfCars[self.direction][self.lane] - 1

                # Zliczanie ilosci pojazdow do adaptacji
                if self.crossed == 0 and self.detectcounterflag == 0 and self.x + self.image.get_rect().width > 0:
                    self.detectcounterflag = 1
                    numberOfDetectCars[self.direction][self.lane] = numberOfDetectCars[self.direction][self.lane] + 1
                if(self.crossed == 1 and self.detectcounterflag == 1):
                    self.detectcounterflag = 0
                    numberOfDetectCars[self.direction][self.lane] = numberOfDetectCars[self.direction][self.lane] - 1

                # Zmienna przejazdu pojazdu przez skrzyzowanie
                if(self.crossed==0 and self.x+self.image.get_rect().width >= stopLines[self.direction]):
                    self.crossed = 1
                # Dopisywanie do tablicy 'po skrzyzowaniu'
                if self.crossed == 1 and self.destination == 'stright':
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                if self.crossed == 1 and self.destination == 'turn_left':
                    self.turningleft = 1
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                    # zmiana katow skretu dla roznego rodzaju pojazdow (pojazdy posiadaja rozne wymiary)
                    if self.angle <= 90:
                        if self.vehicleClass == 'car':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.5
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4.25
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.9
                        elif self.vehicleClass == 'bus':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.7
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4.4
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/5.1
                        elif self.vehicleClass == 'truck':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.65
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4.3
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/5
                        elif self.vehicleClass == 'bike':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.35
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.7
                    if self.angle > 90:
                        self.angle = 90

                if self.crossed == 1 and self.destination == 'turn_right':
                    self.turningright = 1
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                    if self.angle >= -90:
                        if self.vehicleClass == 'car':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.7
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/2.05
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.3
                        if self.vehicleClass == 'bus':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.9
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/2.25
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.5
                        if self.vehicleClass == 'truck':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.75
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/2.1
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.4
                        if self.vehicleClass == 'bike':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.55
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.85
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.15
                    if self.angle <= -90:
                        self.angle = -90

                # Możliwe sytuacje pojazdu:
                # 1.Skręt w prawo
                if self.turningright == 1 and self.indexAfter != 0:
                    if self.y+self.image.get_rect().height<after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStart:
                        self.actualSpeed += self.accelerationVehicle 
                        if abs(self.actualSpeed) >= self.maxSpeed: 
                            self.actualSpeed = self.maxSpeed
                    if after[self.directionAfter][self.laneAfter][self.indexAfter-1].y > screenHeight:
                        self.actualSpeed = self.actualSpeed
                    elif after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStop - self.y - self.image.get_rect().height > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed -= self.actualSpeed**2/(2*((after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStop) - self.y - self.image.get_rect().height))
                    if self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                elif self.turningright == 1:
                    self.actualSpeed += self.accelerationVehicle
                    if abs(self.actualSpeed) >= self.maxSpeed:
                        self.actualSpeed = self.maxSpeed

                # 2.Skręt w lewo
                if self.turningleft == 1 and self.indexAfter != 0:
                    if(self.y > (after[self.directionAfter][self.laneAfter][self.indexAfter-1].y+after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().height + self.whenStart)):
                        self.actualSpeed += self.accelerationVehicle 
                        if abs(self.actualSpeed) >= self.maxSpeed:
                            self.actualSpeed = self.maxSpeed
                    if after[self.directionAfter][self.laneAfter][self.indexAfter-1].y < 0:
                        self.actualSpeed = self.actualSpeed
                    elif self.y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().height - self.whenStop > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed -= self.actualSpeed**2/(2*(self.y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().height - self.whenStop + 1))
                    elif self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                elif self.turningleft == 1:
                    self.actualSpeed += self.accelerationVehicle
                    if abs(self.actualSpeed) >= self.maxSpeed:
                        self.actualSpeed = self.maxSpeed

                # 3.Jazda prosto:
                # a) samochod przy zapalonym swietle zielonym     
                if((self.x+self.image.get_rect().width <= self.stop or self.crossed == 1 or ((self.lane !=1 and currentGreen==0 and currentYellow==0) or (self.lane ==1 and currentGreen==2 and currentYellow==0))) and self.turningleft == 0 and self.turningright == 0):    
                    # przed skrzyzowaniem
                    # gdy samochody sa w ruchu
                    if self.crossed == 0 and self.index != 0 and self.x+self.image.get_rect().width >= vehicles[self.direction][self.lane][self.index-1].x - self.whenBraking:
                        if self.x+self.image.get_rect().width >= vehicles[self.direction][self.lane][self.index-1].x - self.whenBraking:
                            if vehicles[self.direction][self.lane][self.index-1].x > screenWidth:
                                self.actualSpeed = self.actualSpeed
                            elif vehicles[self.direction][self.lane][self.index-1].x - self.whenStop - self.x - self.image.get_rect().width > 0 and self.actualSpeed > vehicles[self.direction][self.lane][self.index-1].actualSpeed:
                                self.actualSpeed -= self.actualSpeed**2/(2*((vehicles[self.direction][self.lane][self.index-1].x - self.whenStop) - self.x - self.image.get_rect().width))
                            elif self.actualSpeed == vehicles[self.direction][self.lane][self.index-1].actualSpeed:
                                self.actualSpeed = vehicles[self.direction][self.lane][self.index-1].actualSpeed
                    # gdy samochody nie są w ruchu
                    if self.crossed == 0 and self.index != 0: 
                        if(self.x+self.image.get_rect().width<vehicles[self.direction][self.lane][self.index-1].x - self.whenStart or vehicles[self.direction][self.lane][self.index-1].y > screenHeight):
                            self.actualSpeed += self.accelerationVehicle
                            if abs(self.actualSpeed) >= self.maxSpeed: 
                                self.actualSpeed = self.maxSpeed
                        elif self.actualSpeed < 0.2: 
                            self.actualSpeed = 0
                    # po skrzyzowaniu
                    elif self.crossed == 1 and self.index != 0 and self.indexAfter != 0:
                        if(self.x+self.image.get_rect().width<(after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStart)):
                            self.actualSpeed += self.accelerationVehicle 
                            if abs(self.actualSpeed) >= self.maxSpeed:
                                self.actualSpeed = self.maxSpeed
                        if after[self.directionAfter][self.laneAfter][self.indexAfter-1].x > screenWidth:
                            self.actualSpeed = self.actualSpeed
                        elif after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStop - self.x - self.image.get_rect().width > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed -= self.actualSpeed**2/(2*((after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStop) - self.x - self.image.get_rect().width - 1))
                        elif self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                    elif self.index == 0 or self.indexAfter == 0:
                        self.actualSpeed += self.accelerationVehicle
                        if abs(self.actualSpeed) >= self.maxSpeed: 
                            self.actualSpeed = self.maxSpeed
                # b) samochod przy zapalonym swietle czerwonym/zoltym
                if(not(self.lane !=1 and currentGreen==0 and currentYellow==0 or self.lane ==1 and currentGreen==2 and currentYellow==0 ) and self.x + self.image.get_rect().width > self.stop - self.whenBraking and self.crossed == 0):
                    if (self.stop - self.x-self.image.get_rect().width > 0 and self.actualSpeed > 0):
                        self.actualSpeed -= self.actualSpeed**2/(2*(self.stop-self.x-self.image.get_rect().width))
                    else:
                        self.actualSpeed = 0

                # Wyswietlanie pojazdu
                rotated_image = pygame.transform.rotate(self.image, self.angle)
                new_rect = rotated_image.get_rect(
                center=self.image.get_rect(topleft=(self.x,self.y)).center)
                screen.blit(rotated_image, new_rect.topleft)

                # Przemieszczanie pojazdu
                self.y += self.actualSpeed * math.sin(math.radians(-self.angle))
                self.x += self.actualSpeed * math.cos(math.radians(self.angle))

                # Wyswietlanie informacji o pojezdzie oraz usuwanie go z symulacji
                if(self.x > screenWidth or self.y > screenHeight or self.y < 0):
                    print("Pas:",self.lane,
                     "Rodzaj:", self.vehicleClass,
                     "Kierunek:", self.direction,
                     "Przeznaczenie:",self.destination,
                     "V:", self.actualSpeed,
                     "Vmax:", self.maxSpeed,
                     "Przyspieszenie:", self.accelerationVehicle, 
                     "Humor:", self.natureDriver,
                     "Stan:", self.techcond,
                     "Index:", self.index,
                     "indexAfter:", self.indexAfter,
                     "laneAfter:", self.laneAfter)
                    self.kill()
                    simulation.remove(self)

        elif(self.direction=='down'):
                # Zliczanie ilosci pojazdow ogolnie
                if self.crossed == 0 and self.counterflag == 0:
                    self.counterflag = 1
                    numberOfCars[self.direction][self.lane] = numberOfCars[self.direction][self.lane] + 1
                if(self.crossed == 1 and self.counterflag == 1):
                    self.counterflag = 0
                    numberOfCars[self.direction][self.lane] = numberOfCars[self.direction][self.lane] - 1

                # Zliczanie ilosci pojazdow do adaptacji
                if self.crossed == 0 and self.detectcounterflag == 0 and self.y + self.image.get_rect().height > 0:
                    self.detectcounterflag = 1
                    numberOfDetectCars[self.direction][self.lane] = numberOfDetectCars[self.direction][self.lane] + 1
                if(self.crossed == 1 and self.detectcounterflag == 1):
                    self.detectcounterflag = 0
                    numberOfDetectCars[self.direction][self.lane] = numberOfDetectCars[self.direction][self.lane] - 1
                    
                # Zmienna przejazdu pojazdu przez skrzyzowanie
                if(self.crossed==0 and self.y+self.image.get_rect().height>=stopLines[self.direction]):
                    self.crossed = 1
                # Dopisywanie do tablicy 'po skrzyzowaniu'
                if self.crossed == 1 and self.destination == 'stright':
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                if self.crossed == 1 and self.destination == 'turn_left':
                    self.turningleft = 1
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                    if self.angle <= 90:
                        if self.vehicleClass == 'car':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.1
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/3.75
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.4
                        if self.vehicleClass == 'bus':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.3
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/3.9
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.6
                        if self.vehicleClass == 'truck':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.2
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/3.8
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.45
                        if self.vehicleClass == 'bike':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/2.95
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/3.55
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.25
                    if self.angle >= 90:
                        self.angle = 90

                if self.crossed == 1 and self.destination == 'turn_right':
                    self.turningright = 1
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                    if self.angle >= -90:
                        if self.vehicleClass == 'car':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.35
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.75
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.1
                        if self.vehicleClass == 'bus':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.55
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.9
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.3
                        if self.vehicleClass == 'truck':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.45
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.8
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.15
                        if self.vehicleClass == 'bike':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.25
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.6
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed
                    if self.angle <= -90:
                        self.angle = -90

                # Możliwe sytuacje pojazdu:
                # 1.Skręt w prawo
                if self.turningright == 1 and self.indexAfter != 0:
                    if(self.x>after[self.directionAfter][self.laneAfter][self.indexAfter-1].x+after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width + self.whenStart):
                        self.actualSpeed += self.accelerationVehicle 
                        if abs(self.actualSpeed) >= self.maxSpeed: 
                            self.actualSpeed = self.maxSpeed
                    if after[self.directionAfter][self.laneAfter][self.indexAfter-1].x < 0:
                        self.actualSpeed = self.actualSpeed
                    elif self.x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width - self.whenStop > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed -= self.actualSpeed**2/(2*(self.x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width - self.whenStop))
                    if self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                elif self.turningright == 1:
                    self.actualSpeed += self.accelerationVehicle
                    if abs(self.actualSpeed) >= self.maxSpeed:
                        self.actualSpeed = self.maxSpeed

                # 2.Skręt w lewo
                if self.turningleft == 1 and self.indexAfter != 0:
                    if(self.x+self.image.get_rect().width<(after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStart)):
                        self.actualSpeed += self.accelerationVehicle 
                        if abs(self.actualSpeed) >= self.maxSpeed: 
                            self.actualSpeed = self.maxSpeed
                    if after[self.directionAfter][self.laneAfter][self.indexAfter-1].x > screenWidth:
                        self.actualSpeed = self.actualSpeed
                    elif after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStop - self.x - self.image.get_rect().width > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed -= self.actualSpeed**2/(2*((after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStop) - self.x - self.image.get_rect().width - 1))
                    if self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                elif self.turningleft == 1:
                    self.actualSpeed += self.accelerationVehicle 
                    if abs(self.actualSpeed) >= self.maxSpeed: 
                        self.actualSpeed = self.maxSpeed

                # 3. Jazda prosto
                # a) samochod przy zapalonym swietle zielonym   
                if((self.y+self.image.get_rect().height <= self.stop or self.crossed == 1 or ((self.lane !=1 and currentGreen==1 and currentYellow==0) or (self.lane ==1 and currentGreen==3 and currentYellow==0)))):    
                    # przed skrzyzowaniem
                    # gdy samochody sa w ruchu 
                    if self.crossed == 0 and self.index != 0 and self.y+self.image.get_rect().height >= vehicles[self.direction][self.lane][self.index-1].y - self.whenBraking:
                        if vehicles[self.direction][self.lane][self.index-1].y > screenHeight:
                            self.actualSpeed = self.actualSpeed
                        elif vehicles[self.direction][self.lane][self.index-1].y - self.whenStop - self.y - self.image.get_rect().height > 0 and self.actualSpeed > vehicles[self.direction][self.lane][self.index-1].actualSpeed:
                            self.actualSpeed -= self.actualSpeed**2/(2*((vehicles[self.direction][self.lane][self.index-1].y - self.whenStop) - self.y - self.image.get_rect().height))
                        elif self.actualSpeed == vehicles[self.direction][self.lane][self.index-1].actualSpeed:
                            self.actualSpeed = vehicles[self.direction][self.lane][self.index-1].actualSpeed
                    # gdy samochody nie sa w ruchu
                    if self.crossed == 0 and self.index != 0:
                        if(self.y+self.image.get_rect().height<vehicles[self.direction][self.lane][self.index-1].y - self.whenStart or vehicles[self.direction][self.lane][self.index-1].x < 0):
                            self.actualSpeed += self.accelerationVehicle 
                            if abs(self.actualSpeed) >= self.maxSpeed: 
                                self.actualSpeed = self.maxSpeed
                        elif self.actualSpeed < 0.2:
                            self.actualSpeed = 0
                    # po skrzyzowaniu
                    elif self.crossed == 1 and self.index != 0 and self.indexAfter != 0:
                        if(self.y+self.image.get_rect().height<after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStart):
                            self.actualSpeed += self.accelerationVehicle 
                            if abs(self.actualSpeed) >= self.maxSpeed:
                                self.actualSpeed = self.maxSpeed
                        if after[self.directionAfter][self.laneAfter][self.indexAfter-1].y > screenHeight:
                            self.actualSpeed = self.actualSpeed
                        elif after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStop - self.y - self.image.get_rect().height > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed -= self.actualSpeed**2/(2*((after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStop) - self.y - self.image.get_rect().height))
                        elif self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                    elif self.index == 0 or self.indexAfter == 0:
                        self.actualSpeed += self.accelerationVehicle
                        if abs(self.actualSpeed) >= self.maxSpeed: 
                            self.actualSpeed = self.maxSpeed
                # b) pojazd przy zapolonym swietle czerwonym/zoltym
                if(not(self.lane !=1 and currentGreen==1 and currentYellow==0 or self.lane ==1 and currentGreen==3 and currentYellow==0 ) and self.y + self.image.get_rect().height > self.stop - self.whenBraking and self.crossed == 0):
                    if (self.stop - self.y-self.image.get_rect().height > 0 and self.actualSpeed > 0):
                        self.actualSpeed -= self.actualSpeed**2/(2*(self.stop-self.y-self.image.get_rect().height))
                    else:
                        self.actualSpeed = 0
                    
                # Wyswietlanie pojazdu
                rotated_image = pygame.transform.rotate(self.image, self.angle)
                new_rect = rotated_image.get_rect(
                center=self.image.get_rect(topleft=(self.x,self.y)).center)
                screen.blit(rotated_image, new_rect.topleft)

                # Przemieszczanie pojazdu
                self.y += self.actualSpeed * math.cos(math.radians(-self.angle))
                self.x += self.actualSpeed * math.sin(math.radians(self.angle))

                if(self.x > screenWidth or self.y > screenHeight or self.x < 0):
                    print("Pas:",self.lane,
                     "Rodzaj:", self.vehicleClass,
                     "Kierunek:", self.direction,
                     "Przeznaczenie:",self.destination,
                     "V:", self.actualSpeed,
                     "Vmax:", self.maxSpeed,
                     "Przyspieszenie:", self.accelerationVehicle, 
                     "Humor:", self.natureDriver,
                     "Stan:", self.techcond)
                    self.kill()
                    simulation.remove(self)

        elif(self.direction=='left'):
                # Zliczanie ilosci pojazdow ogolnie
                if self.crossed == 0 and self.counterflag == 0:
                    self.counterflag = 1
                    numberOfCars[self.direction][self.lane] = numberOfCars[self.direction][self.lane] + 1
                if(self.crossed == 1 and self.counterflag == 1):
                    self.counterflag = 0
                    numberOfCars[self.direction][self.lane] = numberOfCars[self.direction][self.lane] - 1
                
                # Zliczanie ilosci pojazdow do adaptacji
                if self.crossed == 0 and self.detectcounterflag == 0 and self.x<screenWidth:
                    self.detectcounterflag = 1
                    numberOfDetectCars[self.direction][self.lane] = numberOfDetectCars[self.direction][self.lane] + 1
                if(self.crossed == 1 and self.detectcounterflag == 1):
                    self.detectcounterflag = 0
                    numberOfDetectCars[self.direction][self.lane] = numberOfDetectCars[self.direction][self.lane] - 1
                    
                # Zmienna przejazdu pojazdu przez skrzyzowanie
                if(self.crossed==0 and self.x < stopLines[self.direction]):
                    self.crossed = 1
                # Dopisywanie do tablicy 'po skrzyzowaniu'
                if self.crossed == 1 and self.destination == 'stright':
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                if self.crossed == 1 and self.destination == 'turn_left':
                    self.turningleft = 1
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                    # zmiana katow skretu dla roznego rodzaju pojazdow (pojazdy posiadaja rozne wymiary)
                    if self.angle <= 90:
                        if self.vehicleClass == 'car':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.5
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4.25
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.9
                        if self.vehicleClass == 'bus':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.7
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4.4
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/5.1
                        if self.vehicleClass == 'truck':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.6
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4.3
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/5
                        if self.vehicleClass == 'bike':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.35
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.7
                    if self.angle > 90:
                        self.angle = 90

                if self.crossed == 1 and self.destination == 'turn_right':
                    self.turningright = 1
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                    if self.angle >= -90:
                        if self.vehicleClass == 'car':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.6
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.95
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.25
                        if self.vehicleClass == 'bus':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.8
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/2.15
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.5
                        if self.vehicleClass == 'truck':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.7
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/2
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.35
                        if self.vehicleClass == 'bike':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.5
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.8
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.15
                    if self.angle <= -90:
                        self.angle = -90
                
                # Możliwe sytuacje pojazdu:
                # 1.Skręt w prawo
                if self.turningright == 1 and self.indexAfter != 0:
                    if(self.y > after[self.directionAfter][self.laneAfter][self.indexAfter-1].y+after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().height + self.whenStart):
                        self.actualSpeed += self.accelerationVehicle 
                        if abs(self.actualSpeed) >= self.maxSpeed:
                            self.actualSpeed = self.maxSpeed
                    if after[self.directionAfter][self.laneAfter][self.indexAfter-1].y < 0:
                        self.actualSpeed = self.actualSpeed
                    elif self.y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().height - self.whenStop > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed -= self.actualSpeed**2/(2*(self.y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().height - self.whenStop))
                    if self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                elif self.turningright == 1:
                    self.actualSpeed += self.accelerationVehicle
                    if abs(self.actualSpeed) >= self.maxSpeed:
                        self.actualSpeed = self.maxSpeed

                # 2.Skręt w lewo
                if self.turningleft == 1 and self.indexAfter != 0:
                    if(self.y+self.image.get_rect().height<(after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStart)):
                        self.actualSpeed += self.accelerationVehicle 
                        if abs(self.actualSpeed) >= self.maxSpeed: 
                            self.actualSpeed = self.maxSpeed
                    if after[self.directionAfter][self.laneAfter][self.indexAfter-1].y > screenHeight:
                        self.actualSpeed = self.actualSpeed
                    elif after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStop - self.y - self.image.get_rect().height > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed -= self.actualSpeed**2/(2*((after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - self.whenStop) - self.y - self.image.get_rect().height + 1))
                    elif self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                elif self.turningleft == 1:
                    self.actualSpeed += self.accelerationVehicle 
                    if abs(self.actualSpeed) >= self.maxSpeed:
                        self.actualSpeed = self.maxSpeed
                
                # 3. Jazda prosto
                # a) pojazd przy zapalonym swietle zielonym
                if((self.x >= self.stop or self.crossed == 1 or ((self.lane !=1 and currentGreen==0 and currentYellow==0) or (self.lane ==1 and currentGreen==2 and currentYellow==0)))):    
                    # przed skrzyzowaniem
                    # gdy pojazdy sa w ruchu
                    if self.crossed == 0 and self.index != 0 and self.x <= (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + self.whenBraking):
                        if vehicles[self.direction][self.lane][self.index-1].x < 0:
                            self.actualSpeed = self.actualSpeed
                        elif self.x - vehicles[self.direction][self.lane][self.index-1].x - vehicles[self.direction][self.lane][self.index-1].image.get_rect().width - self.whenStop > 0 and self.actualSpeed > vehicles[self.direction][self.lane][self.index-1].actualSpeed:
                            self.actualSpeed -= self.actualSpeed**2/(2*(self.x - vehicles[self.direction][self.lane][self.index-1].x - vehicles[self.direction][self.lane][self.index-1].image.get_rect().width - self.whenStop))
                        elif self.actualSpeed == vehicles[self.direction][self.lane][self.index-1].actualSpeed:
                            self.actualSpeed = vehicles[self.direction][self.lane][self.index-1].actualSpeed
                    # gdy pojazdy nie sa w ruchu
                    if self.crossed == 0 and self.index != 0:
                        if(self.x>(vehicles[self.direction][self.lane][self.index-1].x+vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + self.whenStart) or vehicles[self.direction][self.lane][self.index-1].y < 0):
                            self.actualSpeed += self.accelerationVehicle
                            if abs(self.actualSpeed) >= self.maxSpeed:  
                                self.actualSpeed = self.maxSpeed
                        elif self.actualSpeed < 0.2: 
                            self.actualSpeed = 0
                    # po skrzyzowaniu
                    elif self.crossed == 1 and self.index != 0 and self.indexAfter != 0:
                        if(self.x>(after[self.directionAfter][self.laneAfter][self.indexAfter-1].x+after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width + self.whenStart)):
                            self.actualSpeed += self.accelerationVehicle 
                            if abs(self.actualSpeed) >= self.maxSpeed:  
                                self.actualSpeed = self.maxSpeed
                        if after[self.directionAfter][self.laneAfter][self.indexAfter-1].x < 0:
                            self.actualSpeed = self.actualSpeed
                        elif self.x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width - self.whenStop > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed -= self.actualSpeed**2/(2*(self.x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width - self.whenStop))
                        elif self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                    elif self.index == 0 or self.indexAfter == 0:
                        self.actualSpeed += self.accelerationVehicle
                        if abs(self.actualSpeed) >= self.maxSpeed: 
                            self.actualSpeed = self.maxSpeed
                # b) pojazd przy zapalonym swietle czerwonym/zoltym
                if(not(self.lane !=1 and currentGreen==0 and currentYellow==0 or self.lane ==1 and currentGreen==2 and currentYellow==0 ) and self.x < self.stop + self.whenBraking and self.crossed == 0 and self.turningleft == 0):
                    if (self.x - self.stop > 0 and self.actualSpeed > 0):
                        self.actualSpeed -= self.actualSpeed**2/(2*(self.x-self.stop))
                    else:
                        self.actualSpeed = 0

                # Wyswietlanie pojazdu
                rotated_image = pygame.transform.rotate(self.image, self.angle)
                new_rect = rotated_image.get_rect(
                center=self.image.get_rect(topleft=(self.x,self.y)).center)
                screen.blit(rotated_image, new_rect.topleft)

                # Przemieszczanie pojazdu
                self.y += -self.actualSpeed * math.sin(math.radians(-self.angle))
                self.x += -self.actualSpeed * math.cos(math.radians(self.angle))

                if(self.x < 0 or self.y > screenHeight or self.y < 0):
                    print("Pas:",self.lane,
                     "Rodzaj:", self.vehicleClass,
                     "Kierunek:", self.direction,
                     "Przeznaczenie:",self.destination,
                     "V:", self.actualSpeed,
                     "Vmax:", self.maxSpeed,
                     "Przyspieszenie:", self.accelerationVehicle, 
                     "Humor:", self.natureDriver,
                     "Stan:", self.techcond)
                    self.kill()
                    simulation.remove(self)

        elif(self.direction=='up'):
                # Zliczanie ilosci pojazdow ogolnie
                if self.crossed == 0 and self.counterflag == 0:
                    self.counterflag = 1
                    numberOfCars[self.direction][self.lane] = numberOfCars[self.direction][self.lane] + 1
                if(self.crossed == 1 and self.counterflag == 1):
                    self.counterflag = 0
                    numberOfCars[self.direction][self.lane] = numberOfCars[self.direction][self.lane] - 1
                
                # Zliczanie ilosci pojazdow do adaptacji
                if self.crossed == 0 and self.detectcounterflag == 0 and self.y<screenHeight:
                    self.detectcounterflag = 1
                    numberOfDetectCars[self.direction][self.lane] = numberOfDetectCars[self.direction][self.lane] + 1
                if(self.crossed == 1 and self.detectcounterflag == 1):
                    self.detectcounterflag = 0
                    numberOfDetectCars[self.direction][self.lane] = numberOfDetectCars[self.direction][self.lane] - 1
                    
                # Zmienna przejazdu pojazdu przez skrzyzowanie
                if(self.crossed==0 and self.y < stopLines[self.direction]):
                    self.crossed = 1
                # Dopisywanie do tablicy 'po skrzyzowaniu'
                if self.crossed == 1 and self.destination == 'stright':
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                if self.crossed == 1 and self.destination == 'turn_left':
                    self.turningleft = 1
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                    if self.angle <= 90:
                        if self.vehicleClass == 'car':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.3
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/3.95
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.6
                        if self.vehicleClass == 'bus':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.5
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4.1
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.75
                        if self.vehicleClass == 'truck':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.35
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/4
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.65
                        if self.vehicleClass == 'bike':
                            if self.natureDriver == 'aggresive':
                                self.angle += self.actualSpeed/3.1
                            if self.natureDriver == 'normal':
                                self.angle += self.actualSpeed/3.8
                            if self.natureDriver == 'calm':
                                self.angle += self.actualSpeed/4.45
                    if self.angle >= 90:
                        self.angle = 90

                if self.crossed == 1 and self.destination == 'turn_right':
                    self.turningright = 1
                    if self.countAfter == 0:
                        after[self.directionAfter][self.laneAfter].append(self)
                        self.indexAfter = len(after[self.directionAfter][self.laneAfter]) - 1
                        self.countAfter = 1
                    if self.angle >= -90:
                        if self.vehicleClass == 'car':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.55
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.9
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.3
                        if self.vehicleClass == 'bus':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.75
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/2.1
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.45
                        if self.vehicleClass == 'truck':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.6
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.95
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.35
                        if self.vehicleClass == 'bike':
                            if self.natureDriver == 'aggresive':
                                self.angle -= self.actualSpeed/2.4
                            if self.natureDriver == 'normal':
                                self.angle -= self.actualSpeed/1.75
                            if self.natureDriver == 'calm':
                                self.angle -= self.actualSpeed/1.1
                    if self.angle <= -90:
                        self.angle = -90
                # Możliwe sytuacje pojazdu:
                # 1.Skręt w prawo
                if self.turningright == 1 and self.indexAfter != 0:
                    if(self.x+self.image.get_rect().width<(after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStart)):
                        self.actualSpeed += self.accelerationVehicle 
                        if abs(self.actualSpeed) >= self.maxSpeed:
                            self.actualSpeed = self.maxSpeed
                    if after[self.directionAfter][self.laneAfter][self.indexAfter-1].x > screenWidth:
                        self.actualSpeed = self.actualSpeed
                    elif after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStop - self.x - self.image.get_rect().width > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed -= self.actualSpeed**2/(2*((after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - self.whenStop) - self.x - self.image.get_rect().width - 1))
                    elif self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                elif self.index == 0 or self.indexAfter == 0:
                    self.actualSpeed += self.accelerationVehicle
                    if abs(self.actualSpeed) >= self.maxSpeed: 
                        self.actualSpeed = self.maxSpeed

                # 2.Skret w lewo
                if self.turningleft == 1 and self.indexAfter != 0:
                    if(self.x>(after[self.directionAfter][self.laneAfter][self.indexAfter-1].x+after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width + self.whenStart)):
                        self.actualSpeed += self.accelerationVehicle 
                        if abs(self.actualSpeed) >= self.maxSpeed:
                            self.actualSpeed = self.maxSpeed
                    if after[self.directionAfter][self.laneAfter][self.indexAfter-1].x < 0:
                        self.actualSpeed = self.actualSpeed
                    elif self.x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width - self.whenStop > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed -= self.actualSpeed**2/(2*(self.x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].x - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().width - self.whenStop))
                    elif self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                        self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                elif self.turningleft == 1:
                    self.actualSpeed += self.accelerationVehicle 
                    if abs(self.actualSpeed) >= self.maxSpeed: 
                        self.actualSpeed = self.maxSpeed

                # 3. Jazda prosto
                # a) pojazd przy zapalonym swietle zielonym
                if((self.y >= self.stop or self.crossed == 1 or ((self.lane !=1 and currentGreen==1 and currentYellow==0) or (self.lane ==1 and currentGreen==3 and currentYellow==0)))):    
                    # przed skrzyzowaniem
                    # gdy pojazdy sa w ruchu
                    if self.crossed == 0 and self.index != 0 and self.y <= vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + self.whenBraking:
                        if  vehicles[self.direction][self.lane][self.index-1].y < 0:
                            self.actualSpeed = self.actualSpeed
                        elif vehicles[self.direction][self.lane][self.index-1].turningright == 0 and self.y - vehicles[self.direction][self.lane][self.index-1].y - vehicles[self.direction][self.lane][self.index-1].image.get_rect().height - self.whenStop > 0 and self.actualSpeed > vehicles[self.direction][self.lane][self.index-1].actualSpeed:
                            self.actualSpeed -= self.actualSpeed**2/(2*(self.y - vehicles[self.direction][self.lane][self.index-1].y - vehicles[self.direction][self.lane][self.index-1].image.get_rect().height - self.whenStop))
                        elif self.actualSpeed == vehicles[self.direction][self.lane][self.index-1].actualSpeed:
                            self.actualSpeed = vehicles[self.direction][self.lane][self.index-1].actualSpeed
                    # gdy pojazdy nie sa w ruchu
                    if self.crossed == 0 and self.index != 0:
                        if (self.y > (vehicles[self.direction][self.lane][self.index-1].y+vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + self.whenStart) or vehicles[self.direction][self.lane][self.index-1].x > screenWidth):
                            self.actualSpeed += self.accelerationVehicle
                            if abs(self.actualSpeed) >= self.maxSpeed: 
                                self.actualSpeed = self.maxSpeed
                        elif self.actualSpeed < 0.2: 
                            self.actualSpeed = 0
                    # po skrzyzowaniu
                    elif self.crossed == 1 and self.index != 0 and self.indexAfter != 0:
                        if (self.y > (after[self.directionAfter][self.laneAfter][self.indexAfter-1].y+vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + self.whenStart) or vehicles[self.direction][self.lane][self.index-1].x > screenWidth):
                            self.actualSpeed += self.accelerationVehicle
                            if abs(self.actualSpeed) >= self.maxSpeed: 
                                self.actualSpeed = self.maxSpeed
                        if after[self.directionAfter][self.laneAfter][self.indexAfter-1].y < 0:
                            self.actualSpeed = self.actualSpeed
                        elif self.y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().height - self.whenStop > 0 and self.actualSpeed > after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed -= self.actualSpeed**2/(2*(self.y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].y - after[self.directionAfter][self.laneAfter][self.indexAfter-1].image.get_rect().height - self.whenStop))
                        elif self.actualSpeed == after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed:
                            self.actualSpeed = after[self.directionAfter][self.laneAfter][self.indexAfter-1].actualSpeed
                    elif self.index == 0 or self.indexAfter == 0:
                        self.actualSpeed += self.accelerationVehicle
                        if abs(self.actualSpeed) >= self.maxSpeed: 
                            self.actualSpeed = self.maxSpeed
                # b) pojazd przy zapalonym swietle czerwony/zoltym
                if(not(self.lane !=1 and currentGreen==1 and currentYellow==0 or self.lane ==1 and currentGreen==3 and currentYellow==0 ) and self.y < self.stop + self.whenBraking and self.crossed == 0 and self.turningleft == 0):
                    if (self.y - self.stop > 0 and self.actualSpeed > 0):
                        self.actualSpeed -= self.actualSpeed**2/(2*(self.y-self.stop))
                    else:
                        self.actualSpeed = 0
                        
                # Wyswietlanie pojazdu
                rotated_image = pygame.transform.rotate(self.image, self.angle)
                new_rect = rotated_image.get_rect(
                center=self.image.get_rect(topleft=(self.x,self.y)).center)
                screen.blit(rotated_image, new_rect.topleft)

                # Przemieszczanie pojazdu
                self.y += -self.actualSpeed * math.cos(math.radians(-self.angle))
                self.x += -self.actualSpeed * math.sin(math.radians(self.angle))

                if(self.x < 0 or self.x > screenWidth or self.y < 0):
                    print("Pas:",self.lane,
                     "Rodzaj:", self.vehicleClass,
                     "Kierunek:", self.direction,
                     "Przeznaczenie:",self.destination,
                     "V:", self.actualSpeed,
                     "Vmax:", self.maxSpeed,
                     "Przyspieszenie:", self.accelerationVehicle, 
                     "Humor:", self.natureDriver,
                     "Stan:", self.techcond,
                     "AfterIndex:", self.indexAfter,
                     "AfterDirection", self.directionAfter,
                     "AfterLane:", self.laneAfter)
                    self.kill()
                    simulation.remove(self)
        

# Inicjalizacja licznikow swiatel
def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.green+ts1.red, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    ts3 = TrafficSignal(ts2.green+ts2.red, defaultYellow, defaultGreen[2])
    signals.append(ts3)
    ts4 = TrafficSignal(ts3.green+ts3.red, defaultYellow, defaultGreen[3])
    signals.append(ts4)
    repeat()

# Powatrzalnosc licznikow
def repeat():
    global currentGreen, currentYellow, nextGreen, nextYellow
    while(signals[currentGreen].green > defaultYellow):   # czas do ktorego ma sie palic swiatlo zielone
        updateValues()
        time.sleep(0.75)
    currentYellow = 1   # wlacz swiatlo zolte
    # Resetowanie miejsca zatrzymania pojazdow
    for i in range(0,4):
        if currentGreen == 0 or currentGreen == 2:
            for vehicle in vehicles[directionNumbers[0]][i]:
                vehicle.stop = defaultStop[directionNumbers[0]]
            for vehicle in vehicles[directionNumbers[2]][i]:
                vehicle.stop = defaultStop[directionNumbers[2]]
        if currentGreen == 1 or currentGreen == 3:
            for vehicle in vehicles[directionNumbers[1]][i]:
                vehicle.stop = defaultStop[directionNumbers[1]]
            for vehicle in vehicles[directionNumbers[3]][i]:
                vehicle.stop = defaultStop[directionNumbers[3]]

    while(signals[nextGreen].red > defaultYellow): # czas od ktorego pali sie swiatlo zolte
        updateValues()
        time.sleep(0.75)
    nextYellow = 1 
    while(signals[currentGreen].yellow > 0):  # czas do ktorego ma palic sie swiatlo zolte
        updateValues()
        time.sleep(0.75)
    currentYellow = 0
    while(signals[currentGreen].red > 0):
        updateValues()
        time.sleep(0.75)
    nextYellow = 0 # wlacz swiatlo czerwone+zolte
    
    # Resetowanie wartosci licznikow swiatel
    if currentGreen == 0:
        signals[currentGreen].green = defaultGreen[currentGreen]+(max(numberOfDetectCars['left'][2],numberOfDetectCars['left'][3],numberOfDetectCars['right'][2],numberOfDetectCars['right'][3])+1)*3
    if currentGreen == 1:
        signals[currentGreen].green = defaultGreen[currentGreen]+(max(numberOfDetectCars['up'][2],numberOfDetectCars['up'][3],numberOfDetectCars['down'][2],numberOfDetectCars['down'][3])+1)*3     
    if currentGreen == 2:
        signals[currentGreen].green = defaultGreen[currentGreen]+(max(numberOfDetectCars['left'][1],numberOfDetectCars['right'][1])+1)*3
    if currentGreen == 3:
        signals[currentGreen].green = defaultGreen[currentGreen]+(max(numberOfDetectCars['down'][1],numberOfDetectCars['up'][1])+1)*3
    signals[currentGreen].yellow = defaultYellow
    signals[nextGreen].yellow = defaultYellow
    signals[currentGreen].red = signals[(currentGreen+1)%noOfSignals].green+signals[(currentGreen+2)%noOfSignals].green+signals[(currentGreen+3)%noOfSignals].green

    currentGreen = nextGreen # zmiana obecnie swiecacego sie swiatla zielonego (przejscie do kolejnej fazy)
    nextGreen = (currentGreen+1)%noOfSignals # przewidz ktory sygnal bedzie nastepny
    signals[nextGreen].red = signals[currentGreen].green # ustaw czas swiatla czerownego dla kolejnego swiatla
    repeat() # powtorz caly proces

# Aktualizowanie wartosci licznikow swiatel
def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

# Generowanie pojazdow
def generateVehicles():
    while(True):
        
        # losowanie cech pojazdow
        temp_techcond = random.randint(0,99)
        temp_type = random.randint(0,99)
        temp_nature = random.randint(0,99)

        # losowanie ruchu pojazdow
        temp_dir = random.randint(0,99)
        temp_dest = random.randint(0,99)
        
        # wartosci poczatkowe cech pojazdow
        actualSpeed = 0 
        laneAfter = 0
        directionAfter = ''
        vehicle_type = 0
        direction_number = 0
        destination_number = 0
        whenStart = 0
        whenStop = 0
        
        # zmiana pory dnia symulacji
        global timeDay
        if(timeDay == 'morning'):
            chance_dir = [60,75,95,100]
            chance_type = [60,75,90,100]
            chance_dest = [20,35,100]
            delay = 1
        elif(timeDay == 'afternoon'):
            chance_dir = [20,50,80,100]
            chance_type = [30,70,85,100]
            chance_dest = [30,60,100]
            delay = 2
        elif(timeDay == 'evening'):
            chance_dir = [10,20,90,100]
            chance_type = [60,75,90,100]
            chance_dest = [10,20,100]
            delay = 1.5
        elif(timeDay == 'night'):
            chance_dir = [35,50,85,100]
            chance_type = [30,40,95,100]
            chance_dest = [35,70,100]
            delay = 3
        
        # Kierunek ruchu pojazdow
        if(temp_dir<chance_dir[0]):
            direction_number = 0
        elif(temp_dir<chance_dir[1]):
            direction_number = 1
        elif(temp_dir<chance_dir[2]):
            direction_number = 2
        elif(temp_dir<chance_dir[3]):
            direction_number = 3

        # Przeznaczenie pojazdow
        if(temp_dest<chance_dest[0]):
            destination_number = 0
            lane_number = 3
        elif(temp_dest<chance_dest[1]):
            destination_number = 1
            lane_number = 1
        elif(temp_dest<chance_dest[2]):
            destination_number = 2
            lane_number = random.randint(2,3)

        # Wplyw rodzaju pojazdu
        if(temp_type<chance_type[0]):
            vehicle_type = 0 # samochod 
            maxSpeed = 5 # maksymalna predkosc
            acceleration = .04 # przyspieszenie
            chance_techcond = [30,80,100] # szansa stanu technicznego (zly, w normie, perfekcyjny)
            #chance_nature = [30,80,100] # szansa humoru kierowcy (spokojny, przecietny, agresywny)
            chance_nature = [30,80,100]
            if(temp_nature<chance_nature[0]): 
                natureDriver = 'calm' # spokojny
                whenStart = 45
                whenStop = 40
                whenBraking = 75
                maxSpeedVehicle = maxSpeed/1.5
                accelerationVehicle = acceleration/2
            elif(temp_nature<chance_nature[1]):
                natureDriver = 'normal' # przecietny
                whenStart = 30
                whenStop = 25
                whenBraking = 60
                maxSpeedVehicle = maxSpeed/1.2
                accelerationVehicle = acceleration/1.5
            elif(temp_nature<chance_nature[2]):
                natureDriver = 'aggresive' # agresywny
                whenStart = 15
                whenStop = 10
                whenBraking = 45
                maxSpeedVehicle = maxSpeed   
                accelerationVehicle = acceleration
                
        elif(temp_type<chance_type[1]):
            vehicle_type = 1 # autobus
            maxSpeed = 3 # maksymalna predkosc
            acceleration = .02 # przyspieszenie
            chance_techcond = [30,80,100] # szansa stanu technicznego (zly, w normie, perfekcyjny)
            chance_nature = [20,70,100] # szansa humoru kierowcy (spokojny, przecietny, agresywny)
            if(temp_nature<chance_nature[0]): 
                natureDriver = 'calm' # spokojny
                whenStart = 80
                whenStop = 55
                whenBraking = 90
                maxSpeedVehicle = maxSpeed/1.5
                accelerationVehicle = acceleration/2
            elif(temp_nature<chance_nature[1]): 
                natureDriver = 'normal' # przecietny
                whenStart = 60
                whenStop = 40
                whenBraking = 70
                maxSpeedVehicle = maxSpeed/1.2
                accelerationVehicle = acceleration/1.5
            elif(temp_nature<chance_nature[2]): 
                natureDriver = 'aggresive' # agresywny
                whenStart = 40
                whenStop = 25
                whenBraking = 50
                maxSpeedVehicle = maxSpeed    
                accelerationVehicle = acceleration


        elif(temp_type<chance_type[2]):
            vehicle_type = 2 # ciezarowka
            maxSpeed = 3 # maksymalna predkosc
            acceleration = .015 # przyspieszenie
            chance_techcond = [60,90,100] # szansa stanu technicznego (zly, w normie, perfekcyjny)
            chance_nature = [30,70,100] # szansa humoru kierowcy (spokojny, przecietny, agresywny)
            
            if(temp_nature<chance_nature[0]): 
                natureDriver = 'calm' # spokojny
                whenStart = 80
                whenStop = 55
                whenBraking = 90
                maxSpeedVehicle = maxSpeed/1.5
                accelerationVehicle = acceleration/2
            elif(temp_nature<chance_nature[1]): 
                natureDriver = 'normal' # przecietny
                whenStart = 60
                whenStop = 40
                whenBraking = 70
                maxSpeedVehicle = maxSpeed/1.2
                accelerationVehicle = acceleration/1.5
            elif(temp_nature<chance_nature[2]):
                natureDriver = 'aggresive' # agresywny
                whenStart = 40
                whenStop = 25
                whenBraking = 50
                maxSpeedVehicle = maxSpeed   
                accelerationVehicle = acceleration 

        elif(temp_type<chance_type[3]):
            vehicle_type = 3 # motocykl
            maxSpeed = 6 # maksymalna predkosc
            acceleration = .05 # przyspieszenie
            chance_techcond = [10,40,100] # szansa stanu technicznego (zly, w normie, perfekcyjny)
            chance_nature = [10,60,100] # szansa humoru kierowcy (spokojny, przecietny, agresywny)
            
            if(temp_nature<chance_nature[0]): 
                natureDriver = 'calm' # spokojny 
                whenStart = 60
                whenStop = 55
                whenBraking = 100
                maxSpeedVehicle = maxSpeed/1.5
                accelerationVehicle = acceleration/2
            elif(temp_nature<chance_nature[1]): 
                natureDriver = 'normal' # przecietny
                whenStart = 45
                whenStop = 40
                whenBraking = 80
                maxSpeedVehicle = maxSpeed/1.2
                accelerationVehicle = acceleration/1.5
            elif(temp_nature<chance_nature[2]): 
                natureDriver = 'aggresive' # agresywny
                whenStart = 30
                whenStop = 25
                whenBraking = 60
                maxSpeedVehicle = maxSpeed    
                accelerationVehicle = acceleration

        # Ktory pas zajmie kierowca
        if destination_number == 0 or destination_number == 1:
            if natureDriver == 'calm':
                laneAfter = 3
            elif natureDriver == 'normal':
                laneAfter = 2
            elif natureDriver == 'aggresive':
                laneAfter = 1
        if destination_number == 2:
            laneAfter = lane_number

        # Jaki kierunek bedzie mial kierowca po skrecie
        if directionNumbers[direction_number] == 'right':
            if destinationNumbers[destination_number] == 'turn_right':
                directionAfter = 'down'
            if destinationNumbers[destination_number] == 'turn_left':
                directionAfter = 'up'
            if destinationNumbers[destination_number] == 'stright':
                directionAfter = 'right'   
        if directionNumbers[direction_number] == 'down':
            if destinationNumbers[destination_number] == 'turn_right':
                directionAfter = 'left'
            if destinationNumbers[destination_number] == 'turn_left':
                directionAfter = 'right' 
            if destinationNumbers[destination_number] == 'stright':
                directionAfter = 'down'
        if directionNumbers[direction_number] == 'left':
            if destinationNumbers[destination_number] == 'turn_right':
                directionAfter = 'up'
            if destinationNumbers[destination_number] == 'turn_left':
                directionAfter = 'down' 
            if destinationNumbers[destination_number] == 'stright':
                directionAfter = 'left'
        if directionNumbers[direction_number] == 'up':
            if destinationNumbers[destination_number] == 'turn_right':
                directionAfter = 'right'
            if destinationNumbers[destination_number] == 'turn_left':
                directionAfter = 'left' 
            if destinationNumbers[destination_number] == 'stright':
                directionAfter = 'up'

        # Wplyw stanu technicznego pojazdu
        if(temp_techcond<chance_techcond[0]): 
            techcond = 'bad' # zly stan pojazdu
            maxSpeedVehicle = maxSpeedVehicle/1.5
            accelerationVehicle = accelerationVehicle/2
            
        elif(temp_techcond<chance_techcond[1]): 
            techcond = 'normal' # przecietny stan pojazdu
            maxSpeedVehicle = maxSpeedVehicle/1.2
            accelerationVehicle = accelerationVehicle/1.2
            
        elif(temp_techcond<chance_techcond[2]): 
            techcond = 'perfect' # perfekcyjny
            maxSpeedVehicle = maxSpeedVehicle    
            accelerationVehicle = accelerationVehicle

        Vehicle(lane_number, laneAfter, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], directionAfter, destination_number, destinationNumbers[destination_number], maxSpeedVehicle, actualSpeed ,accelerationVehicle, whenStart, whenStop , whenBraking, natureDriver, techcond)
        time.sleep(delay)

class Main:
    
    # Powielanie inicjalizacji swiatel niezaleznie od symulacji
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()
    
    # Wykorzystywana czcionka
    font = pygame.font.Font(None, 40)

    # Powielanie tworzenia pojazdow
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread2.daemon = True
    thread2.start()

    while True:
        screen.blit(background,(0,0)) 

        # Wyswietlanie predkosci symulacji
        fps = str(int(clock.get_fps()))
        fps_text = font.render(fps, 1, pygame.Color("coral"))
        screen.blit(fps_text, (10,0))

        #Ikona pory dnia
        if timeDay == 'morning':
            screen.blit(morning,(300,60))
        elif timeDay == 'afternoon':
            screen.blit(afternoon,(300,60))
        elif timeDay == 'evening':
            screen.blit(evening,(300,60))
        elif timeDay == 'night':
            screen.blit(night,(300,60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if(pos[0] >= 300 and pos[0] <= 360 and pos[1] >= 60 and pos[1] <= 120):
                    t+=1
                    if(t>3):
                        t = 0
                    timeDay = timeOfDay[t] 

        # Wyswietlanie swiatel zaleznie od stanu symulacji
        for i in range(0,noOfSignals):
            if i == 0 or i == 2:
                if(i==currentGreen):
                    if(currentYellow==1):
                        signals[i].signalText = signals[i].yellow
                        screen.blit(LEFTyellowSignal, signalCoods[i])
                        screen.blit(RIGHTyellowSignal, signalCoods[i+4])
                        if i == 0:
                            screen.blit(LEFTyellowSignal, signalCoods[8])
                            screen.blit(RIGHTyellowSignal, signalCoods[9])
                    else:
                        signals[i].signalText = signals[i].green
                        screen.blit(LEFTgreenSignal, signalCoods[i])
                        screen.blit(RIGHTgreenSignal, signalCoods[i+4])
                        if i == 0:
                            screen.blit(LEFTgreenSignal, signalCoods[8])
                            screen.blit(RIGHTgreenSignal, signalCoods[9])
                elif(i==nextGreen):
                    if(nextYellow==1):
                        signals[i].signalText = signals[i].red
                        screen.blit(LEFTredyellowSignal, signalCoods[i])
                        screen.blit(RIGHTredyellowSignal, signalCoods[i+4])
                        if i == 0:
                            screen.blit(LEFTredyellowSignal, signalCoods[8])
                            screen.blit(RIGHTredyellowSignal, signalCoods[9])
                    else:
                        signals[i].signalText = signals[i].red
                        screen.blit(LEFTredSignal, signalCoods[i])
                        screen.blit(RIGHTredSignal, signalCoods[i+4])
                        if i == 0:
                            screen.blit(LEFTredSignal, signalCoods[8])
                            screen.blit(RIGHTredSignal, signalCoods[9])
                else:
                    signals[i].signalText = signals[i].red
                    screen.blit(LEFTredSignal, signalCoods[i])
                    screen.blit(RIGHTredSignal, signalCoods[i+4])
                    if i == 0:
                            screen.blit(LEFTredSignal, signalCoods[8])
                            screen.blit(RIGHTredSignal, signalCoods[9])
            if i == 1 or i == 3:
                if(i==currentGreen):
                    if(currentYellow==1):
                        signals[i].signalText = signals[i].yellow
                        screen.blit(DOWNyellowSignal, signalCoods[i])
                        screen.blit(UPyellowSignal, signalCoods[i+4])
                        if i == 1:
                            screen.blit(DOWNyellowSignal, signalCoods[10])
                            screen.blit(UPyellowSignal, signalCoods[11])
                    else:
                        signals[i].signalText = signals[i].green
                        screen.blit(DOWNgreenSignal, signalCoods[i])
                        screen.blit(UPgreenSignal, signalCoods[i+4])
                        if i == 1:
                            screen.blit(DOWNgreenSignal, signalCoods[10])
                            screen.blit(UPgreenSignal, signalCoods[11])
                elif(i==nextGreen):
                    if(nextYellow==1):
                        signals[i].signalText = signals[i].red
                        screen.blit(DOWNredyellowSignal, signalCoods[i])
                        screen.blit(UPredyellowSignal, signalCoods[i+4])
                        if i == 1:
                            screen.blit(DOWNredyellowSignal, signalCoods[10])
                            screen.blit(UPredyellowSignal, signalCoods[11])
                    else:
                        signals[i].signalText = signals[i].red
                        screen.blit(DOWNredSignal, signalCoods[i])
                        screen.blit(UPredSignal, signalCoods[i+4])
                        if i == 1:
                            screen.blit(DOWNredSignal, signalCoods[10])
                            screen.blit(UPredSignal, signalCoods[11])
                else:
                    signals[i].signalText = signals[i].red
                    screen.blit(DOWNredSignal, signalCoods[i])
                    screen.blit(UPredSignal, signalCoods[i+4])
                    if i == 1:
                            screen.blit(DOWNredSignal, signalCoods[10])
                            screen.blit(UPredSignal, signalCoods[11])
                    
        signalTexts = ["","","","","","","","","","","",""]
        
        # Wyswietlenie licznikow swiatel
        for i in range(0,noOfSignals): 
            if i == currentGreen: 
                signalTexts[i] = font.render(str(signals[i].signalText), True, green, backgroundGreen)
                signalTexts[i+4] = font.render(str(signals[i].signalText), True, green, backgroundGreen)
                signalTexts[i+8] = font.render(str(signals[i].signalText), True, green, backgroundGreen)
            else:
                signalTexts[i] = font.render(str(signals[i].signalText), True, red , backgroundGreen)
                signalTexts[i+4] = font.render(str(signals[i].signalText), True, red, backgroundGreen)
                signalTexts[i+8] = font.render(str(signals[i].signalText), True, red, backgroundGreen)

            screen.blit(signalTexts[i],signalTimerCoods[i])
            screen.blit(signalTexts[i+4],signalTimerCoods[i+4])
            if i == 0:
                screen.blit(signalTexts[i+8],signalTimerCoods[8])
                screen.blit(signalTexts[i+8],signalTimerCoods[9])  
            if i == 1:
                screen.blit(signalTexts[i+8],signalTimerCoods[10])
                screen.blit(signalTexts[i+8],signalTimerCoods[11])
        

        # Wyswietlenie znakow drogowych nad swiatlami
        screen.blit(RIGHTsign1,(532,535))
        screen.blit(RIGHTsign2,(532,585))
        screen.blit(RIGHTsign3,(532,635))

        screen.blit(DOWNsign1,(510,240))
        screen.blit(DOWNsign2,(460,240))
        screen.blit(DOWNsign3,(410,240))

        screen.blit(LEFTsign1,(830,221))
        screen.blit(LEFTsign2,(830,173))
        screen.blit(LEFTsign3,(830,125))

        screen.blit(UPsign1,(850,520))
        screen.blit(UPsign2,(900,520))
        screen.blit(UPsign3,(950,520))

        # Wyswietlenie ilosci pojazdow na pasach
        RIGHTnumberOfCars1 = font.render(str(numberOfCars['right'][1]), True, white, backgroundGreen)
        RIGHTnumberOfCars2 = font.render(str(numberOfCars['right'][2]), True, white, backgroundGreen)
        RIGHTnumberOfCars3 = font.render(str(numberOfCars['right'][3]), True, white, backgroundGreen)

        DOWNnumberOfCars1 = font.render(str(numberOfCars['down'][1]), True, white, backgroundGreen)
        DOWNnumberOfCars2 = font.render(str(numberOfCars['down'][2]), True, white, backgroundGreen)
        DOWNnumberOfCars3 = font.render(str(numberOfCars['down'][3]), True, white, backgroundGreen)

        LEFTnumberOfCars1 = font.render(str(numberOfCars['left'][1]), True, white, backgroundGreen)
        LEFTnumberOfCars2 = font.render(str(numberOfCars['left'][2]), True, white, backgroundGreen)
        LEFTnumberOfCars3 = font.render(str(numberOfCars['left'][3]), True, white, backgroundGreen)

        UPnumberOfCars1 = font.render(str(numberOfCars['up'][1]), True, white, backgroundGreen)
        UPnumberOfCars2 = font.render(str(numberOfCars['up'][2]), True, white, backgroundGreen)
        UPnumberOfCars3 = font.render(str(numberOfCars['up'][3]), True, white, backgroundGreen)

        screen.blit(RIGHTnumberOfCars1,(10,545))
        screen.blit(RIGHTnumberOfCars2,(10,595))
        screen.blit(RIGHTnumberOfCars3,(10,645))

        screen.blit(DOWNnumberOfCars1,(525,10))
        screen.blit(DOWNnumberOfCars2,(475,10))
        screen.blit(DOWNnumberOfCars3,(420,10))

        screen.blit(LEFTnumberOfCars1,(screenWidth-50,230))
        screen.blit(LEFTnumberOfCars2,(screenWidth-50,180))
        screen.blit(LEFTnumberOfCars3,(screenWidth-50,130))

        screen.blit(UPnumberOfCars1,(860,screenHeight-30))
        screen.blit(UPnumberOfCars2,(915,screenHeight-30))
        screen.blit(UPnumberOfCars3,(970,screenHeight-30))

        # Wyswietlenie ilosci pojazdow wykrytych przez czujniki
        RIGHTnumberOfDetectCars1 = font.render(str(numberOfDetectCars['right'][1]), True, white, backgroundGreen)
        RIGHTnumberOfDetectCars2 = font.render(str(numberOfDetectCars['right'][2]), True, white, backgroundGreen)
        RIGHTnumberOfDetectCars3 = font.render(str(numberOfDetectCars['right'][3]), True, white, backgroundGreen)

        DOWNnumberOfDetectCars1 = font.render(str(numberOfDetectCars['down'][1]), True, white, backgroundGreen)
        DOWNnumberOfDetectCars2 = font.render(str(numberOfDetectCars['down'][2]), True, white, backgroundGreen)
        DOWNnumberOfDetectCars3 = font.render(str(numberOfDetectCars['down'][3]), True, white, backgroundGreen)

        LEFTnumberOfDetectCars1 = font.render(str(numberOfDetectCars['left'][1]), True, white, backgroundGreen)
        LEFTnumberOfDetectCars2 = font.render(str(numberOfDetectCars['left'][2]), True, white, backgroundGreen)
        LEFTnumberOfDetectCars3 = font.render(str(numberOfDetectCars['left'][3]), True, white, backgroundGreen)

        UPnumberOfDetectCars1 = font.render(str(numberOfDetectCars['up'][1]), True, white, backgroundGreen)
        UPnumberOfDetectCars2 = font.render(str(numberOfDetectCars['up'][2]), True, white, backgroundGreen)
        UPnumberOfDetectCars3 = font.render(str(numberOfDetectCars['up'][3]), True, white, backgroundGreen)

        screen.blit(RIGHTnumberOfDetectCars1,(80,545))
        screen.blit(RIGHTnumberOfDetectCars2,(80,595))
        screen.blit(RIGHTnumberOfDetectCars3,(80,645))

        screen.blit(DOWNnumberOfDetectCars1,(525,60))
        screen.blit(DOWNnumberOfDetectCars2,(475,60))
        screen.blit(DOWNnumberOfDetectCars3,(420,60))

        screen.blit(LEFTnumberOfDetectCars1,(screenWidth-105,230))
        screen.blit(LEFTnumberOfDetectCars2,(screenWidth-105,180))
        screen.blit(LEFTnumberOfDetectCars3,(screenWidth-105,130))

        screen.blit(UPnumberOfDetectCars1,(860,screenHeight-80))
        screen.blit(UPnumberOfDetectCars2,(915,screenHeight-80))
        screen.blit(UPnumberOfDetectCars3,(970,screenHeight-80))

        # Wyswietlenie pojazdow
        for vehicle in simulation: 
            vehicle.move()
  
        # Odmierzenie predkosci symulacji
        clock.tick(60)

        # Aktualizacja okna
        pygame.display.update()

        # Resetowanie grup typu Sprites
        spriteGroup.clear(screen, background)
        textboxGroup.clear(screen, background)
        

Main()
