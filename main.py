import BotVent
import gestionBDD
import Anticipation
import msvcrt
#import deCote
from tkinter import *
import turtle

#À développer : Mise en page (affiché nord)
#Etudier l'intégration des scripts dans px4 : dilemne python et C. Convertir ou rendre compatible
#Dans px4: intégration aux capteurs. Détecter trop proche de la berge, calcul nouveau point et commande redécollage.
#Décallage de la zoneU quand zoneD trop petite

tabDonnees = gestionBDD.lectureDonnees();
nom_lieux = [ligne[0] for ligne in tabDonnees];
nom_windfinder = [ligne[1] for ligne in tabDonnees];

def miseAJour(lieuxVent):
    gestionBDD.ajoutDesLieux(lieuxVent);
    BotVent.recuperationDonneesVent(tabDonnees);
    return(0);

def anticipationGraphique(id_lieu, minutesDer):
    print('\n\n -------------------- \n');
    if minutesDer == 0:
        print('Valeur entrée laissée à 0. On prend 15 minutes par défaut');
        minutesDer = 15;
    print('\nDérive de ' + str(minutesDer) + ' minutes');
    dep = Anticipation.getDepRepos(id_lieu, minutesDer);
    zoneU, start, zoneD, startD, GPSOptm = Anticipation.calculAnticipation(id_lieu, dep);
    Anticipation.affichageAnticipation(zoneU, start, zoneD, startD, dep, nom_lieux[id_lieu], GPSOptm);
    return(0);

def interfaceGraphique():
    fenetre = Tk();
    fenetre.title('Interface Anticipation');
    FrameOutils= LabelFrame(fenetre, text='Outils',borderwidth=1);
    FrameOutils.grid(row=1, sticky=W, padx = 5, pady = 5);
    FrameTemps= LabelFrame(fenetre, text='Temps de dérive',borderwidth=1);
    FrameTemps.grid(row=1, column=2, sticky=W, padx = 5, pady = 5);

    bouttonMAJBDD = Button(FrameOutils, text = 'Mise à jour BDD', command = lambda: miseAJour(nom_windfinder));
    bouttonMAJBDD.grid(row=1, sticky=W, padx = 5, pady = 5);

    bouttonQuitter = Button(FrameOutils, text = 'Quitter', command = lambda: fenetre.destroy() );
    bouttonQuitter.grid(row=2, sticky=W, padx = 5, pady = 5);

    labelHeure = Label(FrameTemps, text="Heures : ");
    labelHeure.grid(row=1, column = 1, sticky=W, padx = 5, pady = 5);
    selectHeure = Spinbox(FrameTemps, from_=0, to=50)
    selectHeure.selection('from', 4);
    selectHeure.grid(row=1, column = 2, sticky=W, padx = 5, pady = 5);

    labelMinute = Label(FrameTemps, text="Minutes : ");
    labelMinute.grid(row=2, column = 1, sticky=W, padx = 5, pady = 5);
    selectMinute = Spinbox(FrameTemps, from_=0, to=50)
    selectMinute.selection('from', 4);
    selectMinute.grid(row=2, column = 2, sticky=W, padx = 5, pady = 5);
    
    FrameLac= LabelFrame(fenetre, text='Lac à étudier',borderwidth=1);
    FrameLac.grid(row=2, sticky=W, padx = 5, pady = 5);
    boutonLac = [];
    
    for i in range(len(nom_lieux)):
        boutonLac.append(Button(FrameLac, text = str(nom_lieux[i]), command = lambda i=i: anticipationGraphique( i, int(selectHeure.get())*60 + int(selectMinute.get()) ) ));#le étrange lambda i=i: permet 
        boutonLac[i].grid(row = i, sticky=W, padx = 5, pady = 5);#d'avoir une variable i indépendante pour chaque bouton, sinon tous les boutons sont réaffecté au dernier i.
    
    
    fenetre.mainloop();
    return(0);

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

