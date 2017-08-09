###Ce proramme a pour but d'utiliser les données des vents et des courants
#recueilli apr des programmes tiers afin de calculer le vecteur dérive
#totale du drone. Les données arrivent en format [lieu, date, vecteur]
#Les vecteurs sont exprimé en coordonnées cartésiennes, et leur norme
#correspond à la vitesse du flux (eau ou air)

coefAir = 1; #1 m/s de vent donne 1 m/s de déplacement (faux, valeur numérique à expérimenter)
coefEau = 1; #1 m/s de courant donne 1 m/s de déplacement (peut-être vrai... voir avec les vagues)

import datetime

#print(datetime.datetime.today())


def dateActuelle():
    #return(datetime.datetime.today())
    return(datetime.datetime(2017, 7, 28, 17, 00, 00, 00));

print(dateActuelle());
    


