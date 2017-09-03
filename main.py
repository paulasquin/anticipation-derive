# coding: utf-8
import gestionBDD
import Anticipation
import msvcrt
from tkinter import *
import turtle
import os
import datetime

#À développer : Mise en page (affiché nord)
#Etudier l'intégration des scripts dans px4 : dilemne python et C. Convertir ou rendre compatible
#Dans px4: intégration aux capteurs. Détecter trop proche de la berge, calcul nouveau point et commande redécollage.
#Décallage de la zoneU quand zoneD trop petite

nom_lacs = gestionBDD.getLacs();

def anticipationGraphique(id_lac, minutesDer, minutesAvDeb):
    id_station = gestionBDD.id_lac2id_station(id_lac);
    
    print('\n\n -------------------- \n');
    if minutesDer == 0:
        print('Valeur entrée laissée à 0. On prend 15 minutes par défaut');
        minutesDer = 15;
    print('\nDérive de ' + str(minutesDer) + ' minutes');
    dep = Anticipation.getDepRepos(id_station, minutesDer, minutesAvDeb);
    zoneU, start, zoneD, startD, GPSOptm = Anticipation.calculAnticipation(id_lac, dep);
    Anticipation.affichageAnticipation(zoneU, start, zoneD, startD, dep, nom_lacs[id_lac], GPSOptm);
    return(0);

def interfaceGraphique():
    
    fenetre = Tk();
    fenetre.title('Interface Anticipation');
    FrameOutils= LabelFrame(fenetre, text='Outils',borderwidth=1);
    FrameOutils.grid(row=1, sticky=W, padx = 5, pady = 5);
    FrameDebut= LabelFrame(fenetre, text='Date début de dérive',borderwidth=1);
    FrameDebut.grid(row=1, column=2, sticky=W, padx = 5, pady = 5);
    FrameTemps= LabelFrame(fenetre, text='Temps de dérive',borderwidth=1);
    FrameTemps.grid(row=2, column=2, sticky=W, padx = 5, pady = 5);

    bouttonMAJBDD = Button(FrameOutils, text = 'Mise à jour BDD', command = lambda: gestionBDD.miseAJour());
    bouttonMAJBDD.grid(row=1, sticky=W, padx = 5, pady = 5);

    bouttonQuitter = Button(FrameOutils, text = 'Quitter', command = lambda: fenetre.destroy() );
    bouttonQuitter.grid(row=2, sticky=W, padx = 5, pady = 5);

    labelDebJour = Label(FrameDebut, text="");
    labelDebJour.grid(row=1, column = 1, sticky=W, padx = 5, pady = 5);
    selectDebJour = Listbox(FrameDebut);
    selectDebJour.insert(END, "Aujourd'hui");
    selectDebJour.insert(END, "Demain");
    selectDebJour.insert(END, "Dans 2 jours");
    selectDebJour.insert(END, "Dans 3 jours");
    selectDebJour.activate(0);
    selectDebJour.selection_set(0);
    selectDebJour.grid(row=1, column = 2, sticky=W, padx = 5, pady = 5);

    labelDebHeure = Label(FrameDebut, text="À");
    labelDebHeure.grid(row=2, column = 1, sticky=W, padx = 5, pady = 5);
    selectDebHeure = Spinbox(FrameDebut, from_=0, to=23, wrap=True);
    selectDebHeure.grid(row=2, column = 2, sticky=W, padx = 5, pady = 5);

    labelDebMinute = Label(FrameDebut, text="h");
    labelDebMinute.grid(row=2, column = 3, sticky=W, padx = 5, pady = 5);
    selectDebMinute = Spinbox(FrameDebut, from_=0, to=59, wrap=True);
    selectDebMinute.grid(row=2, column = 4, sticky=W, padx = 5, pady = 5);
    
    labelHeure = Label(FrameTemps, text="Heures : ");
    labelHeure.grid(row=1, column = 1, sticky=W, padx = 5, pady = 5);
    selectHeure = Spinbox(FrameTemps, from_=0, to=50, wrap=True);
    selectHeure.grid(row=1, column = 2, sticky=W, padx = 5, pady = 5);

    labelMinute = Label(FrameTemps, text="Minutes : ");
    labelMinute.grid(row=2, column = 1, sticky=W, padx = 5, pady = 5);
    selectMinute = Spinbox(FrameTemps, from_=0, to=50, wrap=True);
    selectMinute.grid(row=2, column = 2, sticky=W, padx = 5, pady = 5);
    
    FrameLac= LabelFrame(fenetre, text='Lac à étudier',borderwidth=1);
    FrameLac.grid(row=2, sticky=W, padx = 5, pady = 5);
    boutonLac = [];
    
    for i in range(len(nom_lacs)):
        boutonLac.append(Button(FrameLac, text = str(nom_lacs[i]), command = lambda i=i: anticipationGraphique( i, int(selectHeure.get())*60 + int(selectMinute.get()), calculTempsDebut( selectDebJour.curselection(), selectDebHeure.get(), selectDebMinute.get() ) ) ));#le étrange lambda i=i: permet 
        boutonLac[i].grid(row = i, sticky=W, padx = 5, pady = 5);#d'avoir une variable i indépendante pour chaque bouton, sinon tous les boutons sont réaffecté au dernier i.
    
    
    fenetre.mainloop();
    return(0);

def calculTempsDebut(idListJour, heure, minute):
    print(idListJour);
    print(heure);
    actuel = datetime.datetime.today();
    debut = actuel + datetime.timedelta(days = int(idListJour[0]), hours = -actuel.hour + int(heure[0]), minutes = -actuel.minute + int(minute[0]));
    if debut < actuel:
        return(0);
    diff = debut - actuel;
    minutesAvDeb = int(diff.total_seconds()/60);
    
    return(minutesAvDeb);

def interfaceShell():
    id_lieu = '0';
    cont = True;
    gestionBDD.affichageLieu();
    while(cont):
        ent = input('\nQuel lieu ? \nEntrez m pour mise à jour BDD\nou Entrer pour quitter) : ');
        if ent == '':
            cont = False;
        elif ent == 'm':
            miseAJour(lieuxVent);
        else:
            anticipationGraphique(int(ent));
    return(0);

interfaceGraphique();
#interfaceShell();

