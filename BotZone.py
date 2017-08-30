# coding: utf-8
#Stratégie :
# - On établi plein de zone de pose possible à partir des données de carte de Cote. On créé les plus gros rectangle possible.
# - On défini pour chaque zone la station météo référence (la plus proche, par calcul distance entre centre zone et coord station météo)

import math
import sqlite3
import os
import Maps
import Calculs

distanceMaxCons = 250;#Distance maximale entre deux points consécutifs en mètres (maillage max).
nom_BDD_temp = 'BDD_zone_temp.bd';

def creaZone(point, tabPoints):#Définir le plus grand rectangle possible partant du point "point" comme référence Nord Ouest

    [id_point, lat, lon] = point;
    id_point = int(id_point);
    lat = float(lat);
    lon = float(lon);
    
    if os.path.exists(nom_BDD_temp):
        os.remove(nom_BDD_temp);
        
    conn = sqlite3.connect(nom_BDD_temp);
    c = conn.cursor();
    c.execute('''CREATE TABLE Point (id_point integer NOT NULL PRIMARY KEY, lat float, lon float );''');

    for i in range(len(tabPoints)):#On créé un table temporaire qui nous permet de simplifier les opérations sur les points. On aurait pu utiliser les classes, avec un peu moins de clareté
        c.execute('''INSERT INTO Point(id_point, lat, lon) VALUES(?,?,?);''', (int(tabPoints[i][0]), float(tabPoints[i][1]), float(tabPoints[i][2])));
            
    ###On défini 2 types de rectangles : ceux où la largeur est limitante, et ceux où la hauteur est limitante

    ##-------------------------------------------------##
    ##----------- Largeur limitante--------------------##
    ##-------------------------------------------------##
    ##-------------------------------------------------##
    #On cherche la longueur max d'une colonne en dessous du point référent avant la terre. Sur ces colonnes, on devra prendre la plus petite distance à droite avant la terre pour faire la largeur.
    #Les points d'une colonne ont tous la même longitude.

    c.execute('''SELECT lat, lon FROM Point WHERE lon = ? AND lat <= ? ORDER BY lat DESC;''', (lon, lat));#Récupération des points en dessous par lat Desc (on les classe du plus haut au plus bas
    pointsDessous = c.fetchall();
    
    if len(pointsDessous) > 1:#Si on a plus d'un point en dessous du point référent (on peut construite une zone)
        lesHauteurs = [];
        colonne = [pointsDessous[0]];
        for i in range(len(pointsDessous)-1):
            dist = Calculs.distanceGPS(pointsDessous[i], pointsDessous[i+1]);
            if dist < distanceMaxCons:    
                lesHauteurs.append(dist);
                colonne.append(pointsDessous[i+1]);
            else:
                break;
        if len(lesHauteurs) == 0:#Si on a pas de hauteur, alors pas possible d'avoir une zone 2D. On peut arrêter la recherche
            conn.commit();
            conn.close;
            return(0);
    else:
        conn.commit();
        conn.close;
        return(0);#Si on a aucun point en dessous de la référence, impossible d'avoir une zone 2D. On arrête la recherche.
    
    #On a à présent la hauteur (possible) de la zone, reste à trouver la largeur. On part des latitudes de la colonne, et on cherche la distance à droite avant la terre. On devra prendre la plus petite valeur comme largeur de la zone.
    largeurLigne = [];
    for i in range(len(colonne)):
        [latCol, lonCol] = colonne[i];
        c.execute('''SELECT lat, lon FROM Point WHERE lon >= ? AND lat = ? ORDER BY lon ASC;''', (lonCol, latCol));#Récupération des points de la ligne, classé par longitutde ascendante (de gauche à droite)
        pointsDroite = c.fetchall();
        largeurLigne.append(0);
        for j in range(len(pointsDroite)-1):
            dist = Calculs.distanceGPS(pointsDroite[j], pointsDroite[j+1]);
            if dist < distanceMaxCons:
                largeurLigne[-1] = largeurLigne[-1] + dist;#On ajoute la distance entre les points à la longueur de la ligne.
            else:
                del largeurLigne[-1];
                break;

    while(len(largeurLigne) > 0 and len(colonne) > 1 and min(largeurLigne) == 0):#Si on la largeur minimum nulle, cette zone ne peut pas être 2D, on doit donc retrancher une ligne et vérifier à nouveau
        del largeurLigne[-1];
        del colonne[-1];#On supprime l'élément le plus bas de la colonne
        del lesHauteurs[-1];#On retranche la hauteur de la colonne

    if len(largeurLigne) == 0 or min(largeurLigne) == 0:#Si pas de solution de largeur trouvée, on ne peut pas construire de zone
        conn.commit();
        conn.close;
        return(0);
    
    largeur = min(largeurLigne);
    hauteur = sum(lesHauteurs);
    if hauteur == 0:
        conn.commit();
        conn.close;
        return(0);
    
    zoneLimLarg = [lat, lon, largeur, hauteur];


    ##-------------------------------------------------##
    ##----------- Hauteur limitante--------------------##
    ##-------------------------------------------------##
    ##-------------------------------------------------##

    c.execute('''SELECT lat, lon FROM Point WHERE lat = ? AND lon >= ? ORDER BY lon ASC;''', (lat, lon));#Récupération des points à droite par lon Asc (on les classe du plus à gauche au plus à droite
    pointsDroite = c.fetchall();
    
    if len(pointsDroite) > 1:#Si on a plus d'un point à droite du point référent (on peut construite une zone)
        lesLargeurs = [];
        ligne = [pointsDroite[0]];
        for i in range(len(pointsDroite)-1):
            dist = Calculs.distanceGPS(pointsDroite[i], pointsDroite[i+1]);
            if dist < distanceMaxCons:    
                lesLargeurs.append(dist);
                ligne.append(pointsDroite[i+1]);
            else:
                break;
        if len(lesLargeurs) == 0:#Si on a pas de largeur, alors pas possible d'avoir une zone 2D. On peut arrêter la recherche
            conn.commit();
            conn.close;
            return(0);
    else:
        conn.commit();
        conn.close;
        return(0);#Si on a aucun point à droite de la référence, impossible d'avoir une zone 2D. On arrête la recherche.
    
    #On a à présent la largeur (possible) de la zone, reste à trouver la hauteur. On part des longitudes de la ligne, et on cherche la distance en bas avant la terre. On devra prendre la plus petite valeur comme hauteur de la zone.
    hauteurColonne = [];
    for i in range(len(ligne)):
        [latLig, lonLig] = ligne[i];
        c.execute('''SELECT lat, lon FROM Point WHERE lon = ? AND lat <= ? ORDER BY lat DESC;''', (lonLig, latLig));#Récupération des points de la colonne, classé par latitude descendante (de haut en bas)
        pointsDessous = c.fetchall();
        hauteurColonne.append(0);
        for j in range(len(pointsDessous)-1):
            dist = Calculs.distanceGPS(pointsDessous[j], pointsDessous[j+1]);
            if dist < distanceMaxCons:
                hauteurColonne[-1] = hauteurColonne[-1] + dist;#On ajoute la distance entre les points à la longueur de la ligne.
            else:
                del hauteurColonne[-1];
                break;
    
    while(len(hauteurColonne) > 0 and len(ligne) > 1 and min(hauteurColonne) == 0):#Si on la hauteur minimum nulle, cette zone ne peut pas être 2D, on doit donc retrancher une colonne et vérifier à nouveau
        del hauteurColonne[-1];
        del ligne[-1];#On supprime l'élément le plus à droite de la ligne
        del lesLargeurs[-1];#On retranche la largeur de la ligne

    if len(hauteurColonne) == 0 or min(hauteurColonne) == 0:#Si pas de solution de largeur trouvée, on ne peut pas construire de zone
        conn.commit();
        conn.close;
        return(0);
    
    hauteur = min(hauteurColonne);
    largeur = sum(lesLargeurs);

    if largeur == 0:
        conn.commit();
        conn.close;
        return(0);
    
    zoneLimHaut = [lat, lon, largeur, hauteur];

    ##############################################
    ###----------------------------------------###
    ##############################################
    
    
    conn.commit();
    conn.close;
    
    zones = [zoneLimLarg, zoneLimHaut];
    return(zones);

