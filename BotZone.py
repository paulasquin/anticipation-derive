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
    os.remove(nom_BDD_temp);
    conn = sqlite3.connect(nom_BDD_temp);
    c = conn.cursor();
    c.execute('''CREATE TABLE Point (id_point integer NOT NULL PRIMARY KEY, lat float, lon float );''');

    for i in range(len(tabPoints)):#On créé un table temporaire qui nous permet de simplifier les opérations sur les points. On aurait pu utiliser les classes, avec un peu moins de clareté
        if id_point != tabPoints[i][0]:
            c.execute('''INSERT INTO Point(id_point, lat, lon) VALUES(?,?,?);''', (int(tabPoints[i][0]), float(tabPoints[i][1]), float(tabPoints[i][2])));
            
    ###On défini 2 types de rectangles : ceux où la largeur est limitante, et ceux où la hauteur est limitante

    ##-------------------------------------------------##
    ##----------- Largeur limitante--------------------##
    ##-------------------------------------------------##
    ##-------------------------------------------------##
    #On cherche la longueur max d'une colonne en dessous du point référent avant la terre. Sur ces colonnes, on devra prendre la plus petite distance à droite avant la terre pour faire la largeur.
    #Les points d'une colonne ont tous la même longitude.

    c.execute('''SELECT lat, lon FROM Point WHERE lon = ? AND lat < ?;''', (lon, lat));
    res = c.fetchall();
    print('res hauteur = ' + str(res));
    if len(res) > 1:#Si on a plus d'un point en dessous du point référent (on peut construite une zone)
        hauteur = 0;
        lesDistances = [];
        colonne = [];
        for i in range(len(res)-1):
            dist = Calculs.distanceGPS(res[i], res[i+1]);
            if dist < distanceMaxCons:
                hauteur = hauteur + dist;#On ajoute la distance entre les points à la hauteur de la zone
                lesDistances.append(hauteur);
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
        c.execute('''SELECT lat, lon FROM Point WHERE lon > ? AND lat = ?;''', (lonCol, latCol));
        ligne = c.fetchall();
        
        largeurLigne.append(0);
        for j in range(len(ligne)-1):
            dist = Calculs.distanceGPS(ligne[j], ligne[j+1]);
            
            if dist < distanceMaxCons:
                largeurLigne[-1] = largeurLigne[-1] + dist;#On ajoute la distance entre les points à la longueur de la ligne.
            else:
                break;

    while(len(colonne) > 1 and min(largeurLigne) == 0):#Si on la largeur minimum est nulle, cette zone ne peut pas être 2D, on doit donc retrancher une ligne et vérifier à nouveau
        del largeurLigne[-1];
        del colonne[-1];#On supprime l'élément le plus bas de la colonne
        hauteur = hauteur - lesDistances[-1];#On retranche la hauteur de la colonne
        del lesDistances[-1];
        
    if min(largeurLigne) == 0:#Si pas de solution de largeur trouvée, on ne peut pas construire de zone
        return(0);
    largeur = min(largeurLigne);

    zoneLimLarg = [lat, lon, largeur, hauteur];


    ##-------------------------------------------------##
    ##----------- Hauteur limitante--------------------##
    ##-------------------------------------------------##
    ##-------------------------------------------------##
    #On cherche la longueur max d'une ligne à droite du point référent avant la terre. Sur ces lignes, on devra prendre la plus petite distance en bas avant la terre pour faire la hauteur.
    #Les points d'une ligne ont tous la même latitude.

    c.execute('''SELECT lat, lon FROM Point WHERE lon > ? AND lat = ?;''', (lon, lat));
    res = c.fetchall();
    if len(res) > 1:#Si on a plus d'un point en dessous du point référent (on peut construite une zone)
        largeur = 0;
        ligne = [];
        lesDistances = [];
        for i in range(len(res)-1):
            dist = Calculs.distanceGPS(res[i], res[i+1]);
            if dist < distanceMaxCons:
                largeur = largeur + dist;#On ajoute la distance entre les points à la hauteur de la zone
                lesDistances.append(dist);
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
        c.execute('''SELECT lat, lon FROM Point WHERE lon = ? AND lat < ?;''', (lonCol, latCol));
        ligne = c.fetchall();
        
        hauteurColonne.append(0);
        for j in range(len(ligne)-1):
            dist = Calculs.distanceGPS(ligne[j], ligne[j+1]);
            if dist < distanceMaxCons:
                hauteurColonne[-1] = hauteurColonne[-1] + dist;#On ajoute la distance entre les points à la longueur de la ligne.
            else:
                break;

    while(len(ligne) > 1 and min(hauteurColonne) == 0):#Si on la largeur minimum est nulle, cette zone ne peut pas être 2D, on doit donc retrancher une ligne et vérifier à nouveau
        del hauteurColonne[-1];
        del ligne[-1];#On supprime l'élément le plus bas de la colonne
        largeur = largeur - lesDistances[-1];#On retranche la hauteur de la colonne
        del lesDistances[-1];
        
    if min(hauteurColonne) == 0:#Si pas de solution de largeur trouvée, on ne peut pas construire de zone
        return(0);
    hauteur = min(hauteurColonne);

    zoneLimHaut = [lat, lon, largeur, hauteur];

    ##############################################
    ###----------------------------------------###
    ##############################################
    
    conn.commit();
    conn.close;
    os.remove(nom_BDD_temp);
    
    zones = [zoneLimLarg, zoneLimHaut];
    print(zones);
    return(zones);

