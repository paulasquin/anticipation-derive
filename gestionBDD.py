# coding: utf-8
###Programme de cohésion du code d'optimisation pour le drone SUWAVE de l'université de Sherbrooke
###Par Paul Asquin, créé le 4 Juillet 2017

import sqlite3
import os
import Calculs
import BotLac
import BotZone
import Maps
import datetime
import BotVent

nom_BDD = 'environnement.db';
nom_station = 'station.txt';
nom_lacs = 'nom_lac.txt';
nom_points = 'points_lacs.txt';
affichageCartes = True;
affichageChargement = True;

#Fonction qui permet de créer la BDD de gestion des vecteurs et lieux
def initialisationBDD():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''CREATE TABLE IF NOT EXISTS Lac (id_lac integer NOT NULL PRIMARY KEY, nom_lac varchar(100), id_station integer, adresse varchar(100), latCe float, lonCe float, latNE float, lonNE float, latSO float, lonSO float, FOREIGN KEY (id_station) References Station(id_station));''');
    c.execute('''CREATE TABLE IF NOT EXISTS Vecteur (id_station integer, date_vecteur datetime, vecteurX float, vecteurY float, type_vecteur varchar(3), date_enregistrement datetime, FOREIGN KEY (id_station) References Station(id_station));''');
    c.execute('''CREATE TABLE IF NOT EXISTS Zone (id_lac integer, id_zone integer, latNO float, lonNO float, largeur integer, hauteur integer, FOREIGN KEY (id_lac) References Lac(id_lac), PRIMARY KEY(id_lac, id_zone));''');
    c.execute('''CREATE TABLE IF NOT EXISTS Point (id_point integer NOT NULL PRIMARY KEY, lat float, lon float );''');
    c.execute('''CREATE TABLE IF NOT EXISTS Station (id_station integer NOT NULL PRIMARY KEY, nom_windfinder varchar(50), lat float, lon float );''');
    conn.commit();
    conn.close();
    return(0);

def miseAJour():
    os.remove(nom_BDD);
    initialisationBDD();
    ajoutDesStations();
    ajoutDesLacs();
    ajoutDesVents();
    ajoutDesPoints();
    ajoutDesZones();
    return(0);

def affichageLac():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT * FROM Lac''');
    res = c.fetchall();
    for i in range(len(res)):
        chaine = '';
        for c in res[i]:
            chaine = chaine + str(c) + ' ';
    conn.close;
    return(0);

def affichageStation():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT * FROM Station''');
    res = c.fetchall();
    for i in range(len(res)):
        chaine = '';
        for c in res[i]:
            chaine = chaine + str(c) + ' ';
        print(chaine);
    conn.commit();
    conn.close;
    return(0);

def affichageZone():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    print('\n\nAffichage Zone : \n\n');
    c.execute('''SELECT * FROM Zone''');
    res = c.fetchall();
    for i in range(len(res)):
        chaine = '';
        for c in res[i]:
            chaine = chaine + str(c) + ' ';
        print(chaine);
    conn.commit();
    conn.close;
    return(0);

def affichageVecteur():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT * FROM Vecteur''');
    conn.commit();
    conn.close;
    return(0);

#Fonction qui commande un appel SQL pour l'ajout d'un vecteur    
def ajoutVecteur(id_station, date_vecteur, vecteurX, vecteurY, type_vecteur, date_enregistrement):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();    
    c.execute('''INSERT INTO Vecteur(id_station, date_vecteur, vecteurX, vecteurY, type_vecteur, date_enregistrement) VALUES (?, ?, ?, ?, ?, ?);''', (id_station, date_vecteur, vecteurX, vecteurY, type_vecteur, date_enregistrement));
    conn.commit();
    conn.close();
    return(0);

def ajoutLac(id_lac, nom_lac, id_station, adresse, latCe, lonCe, latNE, lonNE, latSO, lonSO):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''INSERT INTO Lac(id_lac, nom_lac, id_station, adresse, latCe, lonCe, latNE, lonNE, latSO, lonSO) VALUES(?,?,?,?,?,?,?,?,?,?);''', (id_lac, nom_lac, id_station, adresse, latCe, lonCe, latNE, lonNE, latSO, lonSO));
    conn.commit();
    conn.close();
    return(0);

def ajoutStation(id_station, nom_windfinder, lat, lon):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''INSERT INTO Station(id_station, nom_windfinder, lat, lon) VALUES (?,?,?,?);''', (id_station, nom_windfinder, lat, lon));
    conn.commit();
    conn.close();
    return(0);

def ajoutZone(id_lac, id_zone, latNO, lonNO, largeur, hauteur):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''INSERT INTO Zone(id_lac, id_zone, latNO, lonNO, largeur, hauteur) VALUES (?,?,?,?,?,?);''', (id_lac, id_zone, latNO, lonNO, largeur, hauteur));
    conn.commit();
    conn.close();
    return(0);
         
def ajoutDesZones():#Ajoute les zones à partir des données des lacs

    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();

    c.execute('''SELECT MAX(id_lac) FROM Lac;''');
    maxLac = int(c.fetchall()[0][0]);

    for id_lac in range(maxLac+1):
        id_zone = 0;
        print('\n\nAjout des Zones pour id_lac = ' + str(id_lac + 1) + '/' + str(maxLac + 1) );
        c.execute('''SELECT latCe, lonCe, latNE, lonNE, latSO, lonSO FROM Lac WHERE id_lac = ?;''', (str(id_lac)) );
        [latCe, lonCe, latNE, lonNE, latSO, lonSO] = c.fetchall()[0];
        #latNE = latMax ; latSO = latMin ; lonNE = lonMax ; lonSO = lonMin
                  
        c.execute('''SELECT id_point, lat, lon FROM Point WHERE (lat BETWEEN ? AND ?) AND (lon BETWEEN ? AND ?) ;''', (latSO,latNE,lonSO,lonNE));
        tabPoints = c.fetchall();
        markers = [];
        print('On a ' + str(len(tabPoints)) + ' points');
        
        for i in range(len(tabPoints)):

            if affichageChargement:
                print('id_lac ' + str(id_lac) + '/' + str(maxLac) + ', Point ' + str(i) + '/' + str(len(tabPoints)-1));
            
            point = tabPoints[i];
            #print('\nUtilisation du point ' + str(point[0]) + ': '+ str(point[1]) + ',' + str(point[2]) );
            markers.append( str(point[1]) + ',' + str(point[2]) );
            nouvZones = BotZone.creaZone(point, tabPoints);
            if nouvZones != 0:
                #print(nouvZones);
                for k in range(len(nouvZones)):
                    [lat, lon, largeur, hauteur] = nouvZones[k];
                    ajoutZone(id_lac, id_zone, lat, lon, largeur, hauteur);
                    id_zone = id_zone + 1;
        if affichageCartes:
            Maps.getImageMaps(markers);
    conn.commit();
    conn.close;
    return(0);

def trouveWindFinder(latCe, lonCe):#indique l' id_station de la station WindFinder la plus proche des coordonnées indiquées
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT * FROM Station;''');
    tabStation = c.fetchall();
    conn.commit();
    conn.close;
    
    distance = [];
    for i in range(len(tabStation)):
        latStation = tabStation[i][2];
        lonStation = tabStation[i][3];
        distance.append(Calculs.distanceGPS([latCe, lonCe],[latStation, lonStation]));
    id_station = distance.index(min(distance));
    return(id_station);

def id_lac2id_station(id_lac):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT latCe, lonCe FROM Lac WHERE id_lac = ?;''', (id_lac,));
    res = c.fetchall();
    [latCe, lonCe] = res[0];
    id_station = trouveWindFinder(latCe, lonCe);
    return(id_station);

def ajoutDesLacs():#ajout des lacs indiqués dans le fichier nom_lacs
    donnees = open(nom_lacs, 'r');
    tabLacs = donnees.read().split('\n');
    donnees.close();
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    for i in range(len(tabLacs)):
        id_lac = i;
        nom_lac = tabLacs[i];
        [adresse, latCe, lonCe, latNE, lonNE, latSO, lonSO] = BotLac.getInfoLac(nom_lac);
        id_station = trouveWindFinder(latCe, lonCe);
        ajoutLac(id_lac, nom_lac, id_station, adresse, latCe, lonCe, latNE, lonNE, latSO, lonSO);
    return(0);


def ajoutDesStations():#Ajout des stations indiqué dans le fichier nom_station

    donnees = open(nom_station, 'r');
    don = donnees.read().split('\n');
    donnees.close();

    tabStation = [l.split(' ; ') for l in don[1:len(don)]];
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    for i in range(len(tabStation)):
        id_station = i;
        nom_windfinder = tabStation[i][0];
        lat = tabStation[i][1];
        lon = tabStation[i][2];
        ajoutStation(id_station, nom_windfinder, lat, lon);
    return(0);

def ajoutDesPoints():    
    donnees = open(nom_points, 'r');
    tab = donnees.read().split('\n');
    donnees.close();
    
    for i in range(len(tab)):
        tab[i] = tab[i].split('\t');

    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    for i in range(len(tab)):
        lat = float(tab[i][1]);
        lon = float(tab[i][0]);
        c.execute('''INSERT INTO Point(id_point, lat, lon) VALUES (?, ?, ?);''', (i, lat, lon) );
    conn.commit();
    conn.close();
    return(0);

def ajoutDesVents():
    print('\n\nTéléchargement des données des vents depuis windfinder.com\n');
    type_vecteur = 'air';
    dateActuelle = datetime.datetime.today()

    lieuxVent = getStations();
    
    for id_station in range(len(lieuxVent)):
        nom_windfinder = lieuxVent[id_station];
        
        #---Section appel des fonctions pour recueil depuis site---
        print('\nRécupération des prévisions vents de ' + nom_windfinder);
        donnees = [];
        corps = BotVent.chargementPage(nom_windfinder);
        titre, tab1, tab2 = BotVent.decompositionTab(corps);

        dates = BotVent.conversionDate(BotVent.trouvDate(tab1) + BotVent.trouvDate(tab2));#Tableau de 4 (jours)
        heures = BotVent.genHeures();#Génération heures ( 2, 5, 8, 11...) Tableau de 8
        lesVecteurX1, lesVecteurY1 = BotVent.vecteurVent(tab1);
        lesVecteurX2, lesVecteurY2 = BotVent.vecteurVent(tab2);
        lesVecteurX = lesVecteurX1 + lesVecteurX2; #Tableau de 8*4 
        lesVecteurY = lesVecteurY1 + lesVecteurY2; #Tableau de 8*4 

        #---Section commande ajout données---
        k = 0;
        for jour in dates:#défillement des jours
            for heure in heures:#défillement des heures
                date_vecteur = datetime.datetime(jour.year, jour.month, jour.day, heure);
                ajoutVecteur(id_station, date_vecteur, lesVecteurX[k], lesVecteurY[k], type_vecteur, dateActuelle);
                k = k+1;
        print('OK');
    return(0);

def getVent(id_station, deb, fin):
    vecteurs = [];
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT VecteurX, VecteurY FROM Vecteur WHERE type_vecteur = 'air' AND id_station = ? AND date_vecteur BETWEEN ? AND ?''', (id_station, deb, fin));
    res = c.fetchall();
    
    for i in range(len(res)):
        vecteurs.append([res[i][0], res[i][1]]);
    conn.commit();
    conn.close;
    return(vecteurs);

    
def getZones(id_lac, zoneU = [0,0]):#Récupération des zones compatibles. Si zoneU = [0,0], on donne toutes les zones.
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    if zoneU == [0,0]:#On récupère toutes les zones du lieux
        c.execute('''SELECT id_zone, latNO, lonNO, largeur, hauteur FROM Zone WHERE id_lac = ?''', str(id_lac));
        res = c.fetchall();
    else:
        [zoneUX, zoneUY] = [str(c) for c in zoneU];
        t = [str(id_lac), str(zoneUX), str(zoneUY)];
        c.execute('''SELECT id_zone, latNO, lonNO, largeur, hauteur FROM Zone WHERE id_lac = ? AND largeur > ? AND hauteur > ?''', t);
        res = c.fetchall();
    zones = []
    for l in res:
        zones.append([c for c in l])
    conn.commit();
    conn.close;
    return(zones);

def getLacs():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT nom_lac FROM Lac ORDER BY id_lac ASC''');
    res = c.fetchall();

    noms_lac = [];
    for i in range(len(res)):
        noms_lac.append(res[i][0]);
    
    return(noms_lac);

def getStations():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT nom_windfinder FROM Station ORDER BY id_station ASC''');
    res = c.fetchall();

    noms_station = [];
    for i in range(len(res)):
        noms_station.append(res[i][0]);
    
    return(noms_station);

initialisationBDD();
#affichageZone();
#affichageStation();
#affichageLac();
#affichageVecteur();
