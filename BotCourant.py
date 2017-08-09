import urllib
import urllib.request
import re


###https://www.cehq.gouv.qc.ca/suivihydro/fichier_donnees.asp?NoStation=030208
###Fichier test ???
####Code de test dans l'avion
def fopen():
    file = open("suivi_hydro_st_francois.html", "r");
    texte = file.read();
    return texte;

#Format des données
#[[Lieu, Date, Heure, Sens (deg), Vitesse (m/s)], ]

#Fonction trouver lieu
def trouvLieu(Titre):
    return(Titre[Titre.find('"nofollow"')+11:Titre.find('</a>')]);

#Fonction trouver Date
def trouvDate(Tab):
    lesDates = []
    for m in re.finditer('heading-date', Tab):
        lesDates.append(Tab[m.end()+2:m.end()+Tab[m.end():m.end()+50].find('/th')-1])
    return(lesDates);

#Fonction Générer heures
def genHeures():
    lesHeures = [2, 5, 8, 11, 14, 17, 20, 23]
    return lesHeures;

#Fonction trouver sens
def trouvSens(Tab, degre = True):
    lesSens = []
    for m in re.finditer('i-wd-xs-', Tab):
        lesSens.append(Tab[m.end():m.end()+Tab[m.end():m.end()+10].find(' ')])

    if(degre):
        lesNom = ['n', 'nne', 'ne', 'ene', 'e', 'ese', 'se', 'sse', 's', 'ssw', 'sw', 'wsw', 'w', 'wnw', 'nw', 'nnw']
        lesDeg = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5]
        
        for i in range(len(lesSens)):
            for j in range(len(lesNom)):
                if (lesSens[i] == lesNom[j]):
                    lesSens[i] = lesDeg[j]
    return(lesSens);

#Fonction trouver vitesses (m/s)
def trouvVitesse(Tab):
    tabVit = Tab[Tab.find('Vitesse du vent'):Tab.find('Couverture nuageuse')]
    lesVitesses = []
    for m in re.finditer('<td>', tabVit):#On utilise '<td>' comme discriminant
        lesVitesses.append(tabVit[m.end():m.end()+tabVit[m.end():m.end()+10].find('\\')])
    return(lesVitesses)

#Fonction chargement de la page
def chargementPage():
    page=urllib.request.urlopen('https://www.cehq.gouv.qc.ca/suivihydro/tableau.asp?NoStation=030208&Zone=&Secteur=nulle') 
    corps=str(page.read())
    return(corps);

#Fonction décomposition de la page en tableaux. Les tableaux vallent 3 jours
def decompositionTab(corps):
    debutTab = corps.find('//		document.title = "Tableau des débits";')
    finTab = corps.find('www.google-analytics.com/analytics.js')
    tab1 = corps[debutTab1:debutTab2]
    tab2 = corps[debutTab2:finTab2]
    return(titre, tab1, tab2);

#Main


#Assemblage résultats
def assemblage():
    donnees = []
    #corps = chargementPage()
    
    titre, tab1, tab2 = decompositionTab(corps)

    lieu = trouvLieu(titre)
    dates = trouvDate(tab1) + trouvDate(tab2)
    heures = genHeures()
    sens = trouvSens(tab1) + trouvSens(tab2)
    vitesses = trouvVitesse(tab1) + trouvVitesse(tab1)

    for i in range(len(dates)):
        lieuJour = [lieu]*len(heures)
        dateJour = [dates[i]]*len(heures)
        sensJour = sens[8*i:8*i+8]
        vitessesJour = vitesses[8*i:8*i+8]
        donnees+= [lieuJour] + [dateJour] + [sensJour] + [vitessesJour]
        
    return(donnees);
#print(assemblage())

print(fopen());
