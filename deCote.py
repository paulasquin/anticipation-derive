# coding: utf-8
#Stratégie :
# - On établi plein de zone de pose possible à partir des données de carte de Cote. On créé les plus gros rectangle possible.
# - On défini pour chaque zone la station météo référence (la plus proche, par calcul distance entre centre zone et coord station météo)

import math
import sqlite3
import os
import Maps

nom_points = 'points_lacs.txt';
nom_BDD_zone = 'zones.db';
distanceMaxZone = 10000;#Distance maximale de recherche d'une zone en mètres.
distanceMaxCons = 250;#Distance maximale entre deux points consécutifs en mètres (maillage max).


#Fonction qui permet de créer la BDD de gestion des vecteurs et lieux
def initialisationBDD():

    os.remove(nom_BDD_zone);
    conn = sqlite3.connect(nom_BDD_zone);
    c = conn.cursor();
    c.execute('''CREATE TABLE IF NOT EXISTS Points (id_point integer NOT NULL PRIMARY KEY, x integer, y integer, lat varchar(10), lon varchar(10) );''');
    c.execute('''CREATE TABLE IF NOT EXISTS Zones (id_lieu integer, latNO varchar(10), lonNO varchar(10), largeur integer, hauteur integer, FOREIGN KEY (id_lieu) References Lieu(id_lieu));''');
    conn.commit();
    conn.close();
    return(0);

def lecturePoints():
    donnees = open(nom_points, 'r');
    tabDonnees = donnees.read().split('\n');

    for i in range(len(tabDonnees)):
        tabDonnees[i] = tabDonnees[i].split('\t');
    donnees.close();
    return(tabDonnees);

def initPoints():
    #On va donner des coord aux points dans le lac par rapport à un point de coord (min(lat) min(lon)) (en bas à gauche pour le Canada)
    initialisationBDD();
    tab = lecturePoints();
    
    minLon = tab[0][0];
    minLat = tab[0][1];
    
    for i in range(len(tab)):
        if tab[i][0] < minLon:
            minLon = tab[i][0];
        if tab[i][1] < minLat:
            minLat = tab[i][1];

    pointRef = [minLat, minLon];

    conn = sqlite3.connect(nom_BDD_zone);
    c = conn.cursor();
    
    for i in range(len(tab)):
        lat = tab[i][1];
        lon = tab[i][0];
        [norm, x, y] = distanceGPSAxes( pointRef, [lat, lon] );
        
        point = [i, x, y, lat, lon];
        c.execute('''INSERT INTO Points(id_point, x, y, lat, lon) VALUES (?, ?, ?, ?, ?);''', (i, x, y, lat, lon) );

    conn.commit();
    conn.close();
    loopCreaZone();
    return(0);

def distanceGPSAxes(a, b):#Donne la distance en mètres entre 2 points GPS, à partir de coord décimales, en norme en X et en Y (à la différence du code dans anticipation).
    latA = float(a[0])*math.pi/180;#B2
    lonA = float(a[1])*math.pi/180;#C2
    latB = float(b[0])*math.pi/180;#B3
    lonB = float(b[1])*math.pi/180;#C3
    dist=math.acos(math.sin(latA)*math.sin(latB)+math.cos(latA)*math.cos(latB)*math.cos(lonA-lonB))*6371000;

    #La coord en X, c'est la distance avec seulement la longitude (latitude à 0)
    X = int(abs((lonB-lonA)*6371000));
    #La coord en Y, seulement la latitude
    Y = int(abs((latB-latA)*6371000));
    
    return(int(dist), X, Y);


def creaZone(point):#Définir le plus grand rectangle possible partant du point "point" comme référence Nord Ouest
    conn = sqlite3.connect(nom_BDD_zone);
    c = conn.cursor();

    #On récolte les points qui sont éloignés à moins de distanceMaxZone
    [id_point, x, y, lat, lon] = point;

    xMin = x - distanceMaxZone;
    xMax = x + distanceMaxZone;
    yMin = y - distanceMaxZone;
    yMax = y + distanceMaxZone;

    ###On défini 2 types de rectangles : ceux où la largeur est limitante, et ceux où la hauteur est limitante

    ##-------------------------------------------------##
    ##----------- Largeur limitante--------------------##
    ##-------------------------------------------------##
    ##-------------------------------------------------##
    #On cherche la longueur max d'une colonne en dessous du point référent avant la terre. Sur ces colonnes, on devra prendre la plus petite distance à droite avant la terre pour faire la largeur.
    #Les points d'une colonne ont tous la même longitude.

    c.execute('''SELECT lat, lon FROM Points WHERE (x BETWEEN ? AND ?) AND (y BETWEEN ? AND ?) AND lon = ? AND lat < ?;''', (xMin, xMax, yMin, yMax, lon, lat));
    res = c.fetchall();
    if len(res) > 1:#Si on a plus d'un point en dessous du point référent (on peut construite une zone)
        hauteur = 0;
        colonne = [];
        for i in range(len(res)-1):
            [dist, X, Y] = distanceGPSAxes(res[i], res[i+1]);
            if dist < distanceMaxCons:
                hauteur = hauteur + dist;#On ajoute la distance entre les points à la hauteur de la zone
                colonne.append(res[i]);
            else:
                break;
        if hauteur == 0:#Si on a pas de hauteur, alors pas possible d'avoir une zone 2D. On peut arrêter la recherche
            return(0);
    else:
        return(0);#Si on a aucun point en dessous de la référence, impossible d'avoir une zone 2D. On arrête la recherche.

    #On a à présent la hauteur de la zone, reste à trouver la largeur. On part des latitudes de la colonne, et on cherche la distance à droite avant la terre. On devra prendre la plus petite valeur comme largeur de la zone.
    largeurLigne = [];
    for i in range(len(res)):
        [latCol, lonCol] = res[i];
        c.execute('''SELECT lat, lon FROM Points WHERE (x BETWEEN ? AND ?) AND (y BETWEEN ? AND ?) AND lon > ? AND lat = ?;''', (xMin, xMax, yMin, yMax, lonCol, latCol));
        ligne = c.fetchall();
        
        largeurLigne.append(0);
        for j in range(len(ligne)-1):
            [dist, X, Y] = distanceGPSAxes(ligne[j], ligne[j+1]);
            if dist < distanceMaxCons:
                largeurLigne[-1] = largeurLigne[-1] + dist;#On ajoute la distance entre les points à la longueur de la ligne.
            else:
                break;

    if min(largeurLigne) == 0:#Si on a trouvé aucune longueur, pas possible de créer une zone 2D
        return(0);
    largeur = min(largeurLigne);

    zoneLimLarg = [lat, lon, largeur, hauteur];

###--------------faire la hauteur limitante

    ##-------------------------------------------------##
    ##----------- Hauteur limitante--------------------##
    ##-------------------------------------------------##
    ##-------------------------------------------------##
    #On cherche la longueur max d'une ligne à droite du point référent avant la terre. Sur ces lignes, on devra prendre la plus petite distance en bas avant la terre pour faire la hauteur.
    #Les points d'une ligne ont tous la même latitude.

    c.execute('''SELECT lat, lon FROM Points WHERE (x BETWEEN ? AND ?) AND (y BETWEEN ? AND ?) AND lon > ? AND lat = ?;''', (xMin, xMax, yMin, yMax, lon, lat));
    res = c.fetchall();
    if len(res) > 1:#Si on a plus d'un point en dessous du point référent (on peut construite une zone)
        largeur = 0;
        ligne = [];
        for i in range(len(res)-1):
            [dist, X, Y] = distanceGPSAxes(res[i], res[i+1]);
            if dist < distanceMaxCons:
                largeur = largeur + dist;#On ajoute la distance entre les points à la hauteur de la zone
                ligne.append(res[i]);
            else:
                break;
        if largeur == 0:#Si on a pas de hauteur, alors pas possible d'avoir une zone 2D. On peut arrêter la recherche
            return(0);
    else:
        return(0);#Si on a aucun point en dessous de la référence, impossible d'avoir une zone 2D. On arrête la recherche.

    #On a à présent la largeur de la zone, reste à trouver la hauteur. On part des longitude de la ligne, et on cherche la distance en bas avant la terre. On devra prendre la plus petite valeur comme hauteur de la zone.
    hauteurColonne = [];
    for i in range(len(res)):
        [latLig, lonLig] = res[i];
        c.execute('''SELECT lat, lon FROM Points WHERE (x BETWEEN ? AND ?) AND (y BETWEEN ? AND ?) AND lon = ? AND lat < ?;''', (xMin, xMax, yMin, yMax, lonCol, latCol));
        ligne = c.fetchall();
        
        hauteurColonne.append(0);
        for j in range(len(ligne)-1):
            [dist, X, Y] = distanceGPSAxes(ligne[j], ligne[j+1]);
            if dist < distanceMaxCons:
                hauteurColonne[-1] = hauteurColonne[-1] + dist;#On ajoute la distance entre les points à la longueur de la ligne.
            else:
                break;

    if min(hauteurColonne) == 0:#Si on a trouvé aucune longueur, pas possible de créer une zone 2D
        return(0);
    hauteur = min(hauteurColonne);

    zoneLimHaut = [lat, lon, largeur, hauteur];

    ##############################################
    ###----------------------------------------###
    ##############################################
    
    conn.commit();
    conn.close;
    zones = [zoneLimLarg, zoneLimHaut];
    return(zones);

def ajoutZone(zone):
    conn = sqlite3.connect(nom_BDD_zone);
    c = conn.cursor();

    [lat, lon, largeur, hauteur] = zone;
    id_lieu = 0;
    c.execute('''INSERT INTO Zones(id_lieu, latNO, lonNO, largeur, hauteur) VALUES (?, ?, ?, ?, ?);''', (id_lieu, lat, lon, largeur, hauteur));
    conn.commit();
    conn.close;

def loopCreaZone():
    zones = [];
    conn = sqlite3.connect(nom_BDD_zone);
    c = conn.cursor();
    iMax = 100;
    for i in range(0, iMax):
        c.execute('''SELECT * FROM Points WHERE id_point = ? ;''', (str(i),));
        point = c.fetchall()[0];
        print( str(i+1) + '/' + str(iMax) + ' : ' + str(zones) + '\n');
        nouvZones = creaZone(point);
        if nouvZones != 0:
            zones = zones + nouvZones;
            for k in range(len(nouvZones)):
                ajoutZone(nouvZones[k]);

    markers = [];
    for i in range(len(zones)):
        markers.append( str(zones[i][0]) + ',' + str(zones[i][1]) );

    Maps.getImageMaps(markers);
    
    conn.commit();
    conn.close;
    return(0);

initPoints();

