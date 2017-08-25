# coding: utf-8
import urllib
import urllib.request
import re
import gestionBDD
import datetime
import math
import numpy as np

#/!\ Le site des vents parle en "provenance du vent". Etant donné que l'on travaille sur des vecteurs vents, on inverse le signe

#Format des données
#[[Lieu, Date, Heure, Sens (deg), Vitesse (m/s)], ...]

#Ou
#[[Lieu, Date, VecteurX, VeteurY], ...]

#Fonction trouver lieu. 
def trouvLieu(Titre):
    return(Titre[Titre.find('"nofollow"')+11:Titre.find('</a>')]);

#Fonction trouver Date
def trouvDate(Tab):
    lesDates = []
    for m in re.finditer('heading-date', Tab):
        date = Tab[m.end()+2:m.end()+Tab[m.end():m.end()+50].find('/th')-1];    
        lesDates.append(date);
    return(lesDates);

#Fonction conversion dates : mardi, juil. 04 --> 2017-07-04. On est face à un problème de gestion de date : \
#l'année n'est pas indiquée sur le site des vents. Que faire si on est à cheval entre 2017 et 2018 ? \
#Solution  : utiliser l'incrémentation datetime et la date du jour, en faisant attention à la correspondance dateDuJour/1erJourPrévision.
def conversionDate(dates):
    datesConv = [];
    correctionJour = 0;
    today = datetime.date.today();
    if int(dates[0][-2] + dates[0][-1]) != today.day:#Si décallage entre jour actuel et premier jour prévision météo (retard de la météo)
        correctionJour = -1;#le jour météo est la veille du jour actuelle
    for i in range(len(dates)):
        datesConv.append(today + datetime.timedelta(days=i+correctionJour));
    return(datesConv);
    

#Fonction Générer heures
def genHeures():
    lesHeures = [2, 5, 8, 11, 14, 17, 20, 23];
    return lesHeures;

#Fonction trouver sens avec résultat en degrés
def trouvSens(Tab, degre = True):
    lesSens = [];
    for m in re.finditer('i-wd-xs-', Tab):
        lesSens.append(Tab[m.end():m.end()+Tab[m.end():m.end()+10].find(' ')]);

    if(degre):
        lesNom = ['n', 'nne', 'ne', 'ene', 'e', 'ese', 'se', 'sse', 's', 'ssw', 'sw', 'wsw', 'w', 'wnw', 'nw', 'nnw'];
        lesDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5];
        for i in range(len(lesSens)):
            for j in range(len(lesNom)):
                if (lesSens[i] == lesNom[j]):
                    lesSens[i] = lesDeg[j];
    return(lesSens);

#Fonction trouver sens avec résultat en vecteur coordonnées cartésiennes unitaire. Repère Est(x)-Nord(y)
def vecteurVent(Tab, cart = True):
    lesSens = [];
    lesVecteurX = [];
    lesVecteurY = [];
    lesVitesses = trouvVitesse(Tab);#Récupération de la vitesse des vents sur le tableau
    
    for m in re.finditer('i-wd-xs-', Tab):
        lesSens.append(Tab[m.end():m.end()+Tab[m.end():m.end()+10].find(' ')]);#Récupération du nom du vent
    if(cart):
        lesNom = ['n', 'nne', 'ne', 'ene', 'e', 'ese', 'se', 'sse', 's', 'ssw', 'sw', 'wsw', 'w', 'wnw', 'nw', 'nnw'];
        lesDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5];#Correspondance noms vents et degrés
        lesRad = [ i*math.pi/180 for i in lesDeg ];#Conversion des degrés en radian
        lesCartX = -np.sin(lesRad);#Conversion des radians en coordonnées cartésiennes unitaires. Inversion "-" pour passer de provenance à direction
        lesCartY = -np.cos(lesRad);
        for i in range(len(lesSens)):
            for j in range(len(lesNom)):
                if (lesSens[i] == lesNom[j]):
                    lesVecteurX.append(float(lesCartX[j])*float(lesVitesses[i]));#On établi la correspondance entre sens et \
                    lesVecteurY.append(float(lesCartY[j])*float(lesVitesses[i]));#vecteur cartésien unitaire, ensuite pondéré par la vitesse du vent
    return(lesVecteurX, lesVecteurY);

#Fonction trouver vitesses (m/s)
def trouvVitesse(Tab):
    tabVit = Tab[Tab.find('Vitesse du vent'):Tab.find('Couverture nuageuse')];
    lesVitesses = [];
    for m in re.finditer('<td>', tabVit):#On utilise '<td>' comme discriminant
        lesVitesses.append(tabVit[m.end():m.end()+tabVit[m.end():m.end()+10].find('\\')]);
    return(lesVitesses);

#Fonction chargement de la page
def chargementPage(nom_windfinder):
    url = 'https://fr.windfinder.com/widget/forecast/'+nom_windfinder+'?show_pressure=1&unit_temperature=c&show_day=0&show_rain=1&unit_rain=mm&days=4&unit_wind=ms&show_clouds=1&show_wind=1&show_temperature=1&show_waves=1&columns=3&unit_wave=m'
    page=urllib.request.urlopen(url);
    corps=str(page.read());
    return(corps);

#Fonction décomposition de la page en tableaux. Les tableaux vallent 3 jours
def decompositionTab(corps):
    titre = corps[corps.find('<h1'):corps.find('/h1>')];
    debutTab1 = corps.find('class="weathertable"');
    debutTab2 = corps.find(' class="weathertable last-weathertable"');
    finTab2 = corps.find('www.google-analytics.com/analytics.js');
    tab1 = corps[debutTab1:debutTab2];
    tab2 = corps[debutTab2:finTab2];
    return(titre, tab1, tab2);
    
#Alimentation BDD
def recuperationDonneesVent(lieuxVent):
    print('\n\nTéléchargement des données des vents depuis windfinder.com\n');
    type_vecteur = 'air';
    dateActuelle = datetime.datetime.today()

    for i in range(len(lieuxVent)):
        id_lieu = i;
        nom_lieu = lieuxVent[i][0];
        nom_windfinder = lieuxVent[i][1];
        
        #---Section appel des fonctions pour recueil depuis site---
        print('\nRécupération des prévisions vents de ' + nom_lieu);
        donnees = [];
        corps = chargementPage(nom_windfinder);
        titre, tab1, tab2 = decompositionTab(corps);

        dates = conversionDate(trouvDate(tab1) + trouvDate(tab2));#Tableau de 4 (jours)
        heures = genHeures();#Génération heures ( 2, 5, 8, 11...) Tableau de 8
        lesVecteurX1, lesVecteurY1 = vecteurVent(tab1);
        lesVecteurX2, lesVecteurY2 = vecteurVent(tab2);
        lesVecteurX = lesVecteurX1 + lesVecteurX2; #Tableau de 8*4 
        lesVecteurY = lesVecteurY1 + lesVecteurY2; #Tableau de 8*4 

        #---Section commande ajout données---
        k = 0;
        for jour in dates:#défillement des jours
            for heure in heures:#défillement des heures
                date_vecteur = datetime.datetime(jour.year, jour.month, jour.day, heure);
                gestionBDD.gestionDoublonVecteur(id_lieu, date_vecteur, type_vecteur);
                gestionBDD.ajoutVecteur(id_lieu, date_vecteur, lesVecteurX[k], lesVecteurY[k], type_vecteur, dateActuelle);
                k = k+1;
        print('OK');
    return(0);
