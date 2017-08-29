import gestionBDD
import datetime
import math
import numpy as np
import matplotlib.pyplot as plt
import turtle
import Calculs

cleAPI = 'AIzaSyCjrrMzllhGLtrCvcudwJuPchbkUHoqdSQ';

coefDepVent = 0.05; #1m/s de vent entraine 0,05m/s de déplacement drone

[resX, resY] = [1280, 1280];

def getDepRepos(id_lieu, minutesDer):#Nouvelle version

    deb = datetime.datetime.today()+ datetime.timedelta(hours = 0);
    fin = deb + datetime.timedelta(minutes = minutesDer);
    vents = gestionBDD.getVent(id_lieu, deb+ datetime.timedelta(hours = -3), fin);#On récupère les vecteurs vents, on commence 3h avant le début pour prendre le vecteur vent qui est actuellement effectif

    heuresMAJ = [2, 5, 8, 11, 14, 17, 20, 23];#Les heures de mise à jour des valeurs de vecteurs
    
    #On doit trouver quelles sont les heures du même jour de dérive, et celles du ou des lendemains
    i = 0;#i est l'index de l'heure D. L'heure D est l'heure de référence du vecteur de début de dérive
    heureD = deb;
    while i < len(heuresMAJ) and deb.hour > heuresMAJ[i]:
        i = i + 1;
    if i == 0:#Si deb.hour < 2
        heureD = heureD + datetime.timedelta(days = - 1, hours = -heureD.hour + 23, minutes = -heureD.minute, second = -heureD.seconds, microseconds = -heureD.microsecond);#On set heureD à 23h le jour précédent        
    else:
        heureD = heureD + datetime.timedelta(hours = -heureD.hour + heuresMAJ[i], minutes = -heureD.minute, seconds = -heureD.second, microseconds = -heureD.microsecond);
    #On a à présent heureD l'heure de référence antérieur à l'heure de début
        
    lesHeuresRef = [heureD];
    while lesHeuresRef[-1] + datetime.timedelta(hours = 3) < fin:
        lesHeuresRef.append(lesHeuresRef[-1]+datetime.timedelta(hours = 3));

    coefsTemps = [];#Secondes de dérive par vecteur.

    if(len(lesHeuresRef)) == 1:#Si on est sur seulement une portion de vecteur
        coefsTemps = [minutesDer*60];#On ajoute directement le temps de dérive, celui appliqué au premier et seul vecteur

    else:#Si on est sur plus d'un vecteur
        coefsTemps = [(lesHeuresRef[1]-deb).seconds];#On récupère au début le nombre de secondes jusqu'au prochain
        tempsActuel = lesHeuresRef[1];
        #Obention du temps qui sépare le temps actuel du temps de fin de vecteur
        k = 1;#k parcours lesHeuresRef. On part à 1 car on a déja traité le premier vecteur
        while k < len(lesHeuresRef):#On parcourt les sessions pleines
            coefsTemps.append(3*3600);#Ajout d'une session complète, i.e. 3h
            tempsActuel = lesHeuresRef[k];
            k = k+1;
        coefsTemps.append( (fin-tempsActuel).seconds );#On ajoute les secondes entre la fin et le début de la dernière session.
        
    while(len(coefsTemps) < len(vents)):
        del vents[-1];

    print('coefsTemps = ' + str(coefsTemps));
    print('vents = ' + str(vents));
    
    dep = [];
    for i in range(len(vents)):#Pondération des déplacements par le temps resté sur chaque vecteur
        dep.append([vents[i][0]*coefDepVent*coefsTemps[i], vents[i][1]*coefDepVent*coefsTemps[i]]);
    return(dep);


##latA = 45.333836;
##lonA = 72.041905;
##latB = 45.317091;
##lonB = 72.041847;
##[latC, lonC] = Calculs.angleGPS(0, -1860);
##print(Calculs.distanceGPS([latB, lonB], [latA+latC, lonA+lonC]));

def calculAnticipation(id_lieu, dep, pos = [0,0]):#Renvoie la taille de la zone de dérive et le lieu de pose optimal. 
    lesX = [0];                                   #pos est facultatif : position du drone dans le lac si cela doit influencer le choix de la zone
    lesY = [0];
    
    for i in range(len(dep)):
        depX, depY = dep[i][0], dep[i][1];
        lesX.append(lesX[-1] + depX);#Historique de la position absolue depuis l'origine du drone
        lesY.append(lesY[-1] + depY);#- permettera de déterminer la taille de la zone de sécurité

    zoneX = int(abs(max(lesX) - min(lesX)));#Largeur de zone occupée par le drone durant son déplacement réduite à un rectangle
    zoneY = int(abs(max(lesY) - min(lesY)));#- en mètres

    if zoneX < 1:
        zoneX = 1;
    if zoneY < 1:
        zoneY = 1; 
    
    startX = -int(max(lesX))+zoneX; 
    startY = int(max(lesY));
    zoneU = [zoneX, zoneY];
    zoneD = choixZoneD(id_lieu, zoneU, pos);#Récupération zone disponible.
    [id_zone, latNO, lonNO, zoneDX, zoneDY, tropPetit] = zoneD;

    #On fait coïncider les centres des zones
    startDX = zoneDX/2-zoneX/2+startX;
    startDY = zoneDY/2-zoneY/2+startY;

    if startDX < 0:#Dans les cas de dépassements de la zone
        startDX = startX;
    if startDY < 0:
        startDY = startY;
    if startDX > zoneDX:
        startDX = zoneDX-(zoneX-startX);
    if startDY > zoneDY:
        startDY = zoneDY-(zoneY-startY);
        
    startU = [startX, startY];#Lieu de départ dans la zone U par rapport à l'angle NO (en cartésien)
    startD = [startDX, startDY];#Lieu de départ dans la zone D par rapport à l'angle NO
                            
    [latRel, lonRel]=Calculs.angleGPS(startDX, startDY)#Calcul latitude et longitude relative GPS par rapport au point NO zone D
    GPSOptm=[Calculs.arrondir(latNO-latRel,6), Calculs.arrondir(lonNO+lonRel,6)];

    zoneD = [id_zone, latNO, lonNO, zoneDX, zoneDY, tropPetit];
    
    return(zoneU, startU, zoneD, startD, GPSOptm);

def affichageAnticipation(zoneU, startU, zoneD, startD, dep, nom_lieu, GPSOptm):#ZoneU : zone utile, zone minimale nécessaire au déplacement. ZoneD : zone disponible, zone maximale identifiée sur le lac

    [zoneX, zoneY] = zoneU;
    [id_zone, latNO, lonNO, zoneDX, zoneDY, tropPetit] = zoneD;
    [startX, startY] = startU;
    [startDX, startDY] = startD;
    [latOptm, lonOptm] = GPSOptm;

    coefAff = Calculs.arrondir(min([resX/zoneDX, resX/zoneX, resY/zoneY, resY/zoneDY])*0.5, 2);

    #getImageMaps(latNO, lonNO, zoneU#....
    
    affDep = [];
    for i in range(len(dep)):#Affectation du coefficient d'affichage
        affDepX, affDepY = dep[i][0]*coefAff, dep[i][1]*coefAff;
        affDep.append([affDepX, affDepY]);
        
    #turtle.setup()#Initialisation de la fenêtre tortue
    turtle.TurtleScreen._RUNNING = True;
    #turtle.setup(width=resX, height=resY);
    #turtle.setup(width=zoneX*1.1, height=zoneY*1.5);
    
    turtle.title("Anticipation dérive SUWAVE");
    turtle.reset();
    turtle.speed(0);
    #--Calcul pour affichage Zone U--
    affZoneX = zoneX*coefAff;
    affZoneY = zoneY*coefAff;
    orgX = int(-affZoneX/2);#Coordonnées de l'origine de la tortue pour dessin zone
    orgY = int(affZoneY/2);
    
    #--Affichage Zone D--
    affZoneDX = zoneDX*coefAff;
    affZoneDY = zoneDY*coefAff;
    orgDX = -int(affZoneDX/2);
    orgDY = int(affZoneDY/2);

    if(tropPetit):#On recalle visuellement la zone D en haut à droite de la zone U
        if(orgX < orgDX):#(opération déjà faite dans le calculs d'anticipation,
            orgDX = orgX;#mais à implémenter différement pour l'affichage turtle.
        if(orgY < orgDY):
            orgDY = orgY;
        if(orgY > orgDY):
            orgDY = orgY;
        if(orgX > orgDX):
            orgDX = orgX;
    turtle.up()
    turtle.goto(orgDX,orgDY);#Placement de la tortue à l'origine de visualisation de D
    turtle.color('blue');
    turtle.down();
    
    turtle.goto(orgDX + affZoneDX, orgDY);#Dessin de la zone de sécurité et affichage largeur - Horizontal haut vers droite
    turtle.goto(orgDX + affZoneDX, orgDY-affZoneDY);
    turtle.goto(orgDX + affZoneDX/2, orgDY-affZoneDY);
    turtle.write('Largeur = ' + str(int(zoneDX)) + 'm', False, align="center", font=("Arial", 12, "normal"));
    turtle.goto(orgDX + affZoneDX, orgDY-affZoneDY);
    turtle.goto(orgDX, orgDY-affZoneDY);
    turtle.goto(orgDX,0);
    turtle.write(' Hauteur = ' + str(int(zoneDY)) + 'm', False, align="right", font=("Arial", 12, "normal"));
    turtle.goto(orgDX,orgDY);

    #--Affichage Zone U--
    
    
    turtle.up()
    turtle.goto(orgX,orgY);#Placement de la tortue à l'origine de visualisation de U
    turtle.color('black');
    turtle.down();
    

    turtle.goto(orgX + affZoneX/2, orgY);
    turtle.write('Largeur = ' + str(int(zoneX)) + 'm\n', False, align="center", font=("Arial", 12, "normal"));
    turtle.goto(orgX + affZoneX, orgY);#Dessin de la zone de sécurité et affichage largeur - Horizontal haut vers droite
    turtle.goto(orgX + affZoneX, orgY-affZoneY/2);
    turtle.write(' Hauteur = ' + str(int(zoneY)) + 'm', False, align="left", font=("Arial", 12, "normal"));
    turtle.goto(orgX + affZoneX, orgY-affZoneY);
    turtle.goto(orgX, orgY-affZoneY);
    turtle.goto(orgX,orgY);
    
    turtle.up()

    affStartX = (startX)*coefAff-orgX-affZoneX;
    affStartY = (-startY)*coefAff-orgY+affZoneY;
    turtle.goto(affStartX,affStartY);
    turtle.speed(3);
    turtle.dot(10, 'red');
    turtle.write(' Départ = (' + str(int(startX)) + 'm, ' + str(int(startY)) + 'm)\nGPS     =  (' + str(latOptm)+ ', '+ str(lonOptm) +')', False, align="left", font=("Arial", 12, "normal"))
    turtle.color('red');
    turtle.down()
    
    for i in range(len(affDep)):#Dessin des déplacements
        posx, posy = turtle.pos();
        turtle.goto(posx+affDep[i][0], posy+affDep[i][1]);
    angle = math.acos(affDep[-1][1]/math.sqrt(affDep[-1][0]**2 + affDep[-1][1]**2))*180/math.pi;
    if (affDep[-1][0] < 0):
        angle += 90;
    turtle.settiltangle(angle);#Orientation de la tortue dans le sens de déplacement (esthétique)

    #---Affichage des informations---
    print('\nAnticipation de la dérive pour le lac ' + str(nom_lieu) + '\n');
    print('La zone de sécurité minimale, orientée nord :\nlargeur ' + str(int(zoneX)) +'m, hauteur ' + str(int(zoneY)) + 'm');
    print('\nDépart du drone optimale aux coordonnées :\n(' + str(int(startX)) + ', ' + str(int(startY)) + ') mètres / angle suppérieur gauche\n');
    print('Position GPS Optimale ('+ str(latOptm) + ', '+str(lonOptm) + ')');
    turtle.mainloop();
    turtle.TurtleScreen._RUNNING = True;#Permer d'éviter les erreurs à la suite de la fermature de la fenêtre turtle. Je ne sais pas comment ça fonctionne, mais ça fonctionne très bien
    return(0);

def choixZoneD(id_lieu, zoneU, pos = [0,0]):#Si pos est donnée comme position GPS du drone et plusieurs positions valables, on choisi la zone valable la plus proche, sinon on choisi la plus grande.
    tropPetit = False;
    [zoneUX, zoneUY] = zoneU;
    zones = gestionBDD.getZones(id_lieu, zoneU);#Extraction des zones potentiels suceptibles d'accueillir le drone.   
    
    if len(zones) != 1:#Plusieurs choix valables ou aucun

        if len(zones) == 0:#Si pas de zone potentielle, on continue car on devra bien se poser. Booléen pour affichage avertissement
            zones = gestionBDD.getZones(id_lieu);#on sélectionne toutes les zones.
            tropPetit = True;

        if pos == [0,0] or tropPetit == True:#On n'est pas sur une stratégie en fonction de la position dans le lac. La stratégie de position ne peut s'appliquer que si on a le choix entre plusieurs zones valables.
        #On va chosir la meilleure zone avec une stratégie par coefficient. : le plus grand (zoneDX/zoneUX)*(zoneDY/zoneUY) l'emporte, petite variante pour trop petit

            coefMax = 0;
            iMax = 0;
            for i in range(len(zones)):
                tmpZoneDX = zones[i][3];
                tmpZoneDY = zones[i][4];
                coefX = (tmpZoneDX/zoneUX);
                coefY = (tmpZoneDY/zoneUY);

                if tropPetit and coefX >1:#Si on est trop petit et quand même bon en largeur :
                    coefX = 1;
                if tropPetit and coefY > 1:#Ou en hauteur, on réduit le coef à 1 (pour ne pas se faire influencer par les inutilement longs rectangles)
                    coefY = 1;

                coef = coefX*coefY;
                if coef > coefMax:
                    iMax = i;
                    coefMax = coef;

            zoneD = zones[iMax];
            
        else:#Stratégie positionnement
            print('Stratégie par position pas encore prête');
                
                
    else:#Si len(zones) == 1, on a pas de soucis pour choisir la meilleure zone, il n'y en a qu'une valable.
        zoneD = zones[0];

    #id_zone = zoneD[0];    
    #print('La meilleure zone est ' +str(zoneD));
    if tropPetit:
        print('Attention, zone trop petite');
    zoneD = zoneD + [tropPetit]
    return(zoneD);

