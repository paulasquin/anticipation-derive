###Le Grand ordonateur
###Programme de cohésion du code d'optimisation pour le drone SUWAVE de l'université de Sherbrooke
###Par Paul Asquin, créé le 4 Juillet 2017

import sqlite3

nom_BDD = 'environnement.db';
nom_donnees = 'donnees.txt';

#Fonction qui permet de créer la BDD de gestion des vecteurs et lieux
def initialisationBDD():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''CREATE TABLE IF NOT EXISTS Lieu (id_lieu integer NOT NULL PRIMARY KEY, nom_lieu varchar(50), nom_windfinder varchar(50));''');
    c.execute('''CREATE TABLE IF NOT EXISTS Vecteur (id_lieu integer, date_vecteur datetime, vecteurX float, vecteurY float, type_vecteur varchar(3), date_enregistrement datetime, FOREIGN KEY (id_lieu) References Lieu(id_lieu));''');
    c.execute('''CREATE TABLE IF NOT EXISTS Zone (id_lieu integer, id_zone integer, latNO float, lonNO float, largeur integer, hauteur integer, FOREIGN KEY (id_lieu) References Lieu(id_lieu), PRIMARY KEY(id_lieu, id_zone));''');
    conn.commit();
    conn.close();
    ecritureDonnees(lectureDonnees());
    return(0);

#Fonction qui commande un appel SQL pour l'ajout d'un vecteur    
def ajoutVecteur(id_lieu, date_vecteur, vecteurX, vecteurY, type_vecteur, date_enregistrement):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    vecteur = [id_lieu, date_vecteur, vecteurX, vecteurY, type_vecteur, date_enregistrement];
    c.executemany('''INSERT INTO Vecteur(id_lieu, date_vecteur, vecteurX, vecteurY, type_vecteur, date_enregistrement) VALUES (?, ?, ?, ?, ?, ?);''', [vecteur]);
    conn.commit();
    conn.close();
    return(0);

def ajoutLieu(id_lieu, nom_lieu, nom_windfinder):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    t = [id_lieu, nom_lieu, nom_windfinder];
    c.executemany('''INSERT INTO Lieu(id_lieu, nom_lieu, nom_windfinder) VALUES (?,?,?);''', [t]);
    conn.commit();
    conn.close();
    return(0);

def ajoutZone(id_lieu, zone):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    [id_zone, latNO, lonNO, largeur, hauteur] = zone;
    latNO = convGPSDec(latNO);
    lonNO = convGPSDec(lonNO);
    t = [id_lieu, id_zone, latNO, lonNO, largeur, hauteur];
    c.executemany('''INSERT INTO Zone(id_lieu, id_zone, latNO, lonNO, largeur, hauteur) VALUES (?,?,?,?,?,?);''', [t]);
    conn.commit();
    conn.close();
    return(0);
         
def ajoutDesZones(id_lieu, tabZones):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''DELETE FROM Zone WHERE id_lieu=?''', str(id_lieu));
    c.execute('''SELECT MAX(id_zone) FROM Zone WHERE id_lieu = ?''', str(id_lieu));
    last = c.fetchone()[0];
    conn.commit();
    conn.close();
    if last == None:#Si pas de zone pour ce lieu
        last = -1;
    for i in range(int(last) + 1, len(tabZones)):#Dans la zone non encore écrite
        id_zone = i;
        ajoutZone(id_lieu, [id_zone]+tabZones[i]);
    return(0);

def ajoutDesLieux(tabLieux):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT MAX(id_lieu) FROM Lieu''');
    last = c.fetchone()[0];
    conn.commit();
    conn.close();
    if last == None:#Si la table est vide de lieux
        last = -1;
    for i in range(int(last) + 1, len(tabLieux)):
        id_lieu = i;
        nom_lieu = tabLieux[i][0];
        nom_windfinder = tabLieux[i][1];
        ajoutLieu(id_lieu, nom_lieu, nom_windfinder);
    return(0);

def gestionDoublonVecteur(id_lieu, date_vecteur, type_vecteur):
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    t = [id_lieu, date_vecteur, type_vecteur];
    c.executemany('''DELETE FROM Vecteur WHERE id_lieu = ? AND date_vecteur = ? AND type_vecteur = ?''', [t]);
    conn.commit();
    conn.close();
    return(0);
    
def affichageLieu():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT * FROM Lieu''');
    res = c.fetchall();
    for i in range(len(res)):
        print(str(res[i][0]) + ' ' + str(res[i][1]));
    conn.commit();
    conn.close;
    return(0);

def affichageZone():
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
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

def getVent(id_lieu, deb, fin):
    vecteurs = [];
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    c.execute('''SELECT VecteurX, VecteurY FROM Vecteur WHERE type_vecteur = 'air' AND id_lieu = ? AND date_vecteur BETWEEN ? AND ?''', (id_lieu, deb, fin));
    res = c.fetchall();
    
    for i in range(len(res)):
        vecteurs.append([res[i][0], res[i][1]]);
    conn.commit();
    conn.close;
    return(vecteurs);

def convGPSDec(sexa):#Conversion des coordonnées GPS sexagésimaux vers décimal
    #Format 72° 2'30.65"O ou encore 45°19'1.53"N
    deg = sexa[0:sexa.find('°')];
    minu = sexa[sexa.find('°')+1:sexa.find("'")];
    sec = sexa[sexa.find("'")+1:sexa.find('"')];
    deci = float(deg) + (float(minu) / 60) + (float(sec) / 3600);
    deci = int(deci*10**6)/10**6; #On arrondi à 6 chiffres après la virgules.
    if 'O' in sexa or 'S' in sexa:
        deci = -deci;
    return(deci);
    
def getZones(id_lieu, zoneU = [0,0]):#Récupération des zones compatibles. Si zoneU = [0,0], on donne toutes les zones.
    conn = sqlite3.connect(nom_BDD);
    c = conn.cursor();
    if zoneU == [0,0]:#On récupère toutes les zones du lieux
        c.execute('''SELECT id_zone, latNO, lonNO, largeur, hauteur FROM Zone WHERE id_lieu = ?''', str(id_lieu));
        res = c.fetchall();
    else:
        [zoneUX, zoneUY] = [str(c) for c in zoneU];
        t = [str(id_lieu), str(zoneUX), str(zoneUY)];
        c.execute('''SELECT id_zone, latNO, lonNO, largeur, hauteur FROM Zone WHERE id_lieu = ? AND largeur > ? AND hauteur > ?''', t);
        res = c.fetchall();
    zones = []
    for l in res:
        zones.append([c for c in l])
    conn.commit();
    conn.close;
    return(zones);

def lectureDonnees():
    donnees = open(nom_donnees, 'r');
    tabDonnees = [];
    
    don = donnees.read().split('\n');
    donnees.close();  
    don = [l.split(' ; ') for l in don[1:len(don)]];
    for l in don:
        ligne = [];
        for c in l:
            el = c.split(', ');
            if len(el) == 1:
                ligne.append(el[0]);
            else:
                ligne.append(el);
        tabDonnees.append(ligne);
    return(tabDonnees);

def ecritureDonnees(tabDonnees):
    #--Ajout des Lieux & des Zones--
    tabLieux = [];
    for i in range(len(tabDonnees)):
        tabLieux.append([tabDonnees[i][0], tabDonnees[i][1]]);
        if len(tabDonnees[i][0]) >= 3:
            tabZone = tabDonnees[i][2:len(tabDonnees[i])];
            ajoutDesZones(i, tabZone); 
    ajoutDesLieux(tabLieux);

    #affichageLieu();
    #affichageZone();
    return(0);
        

initialisationBDD();
#affichageZone();

