import urllib
import urllib.request

def getInfoLac(nom_lac):#Fonction qui récupère des infos GPS sur un lieu nommé
    base = 'https://maps.googleapis.com/maps/api/geocode/json?address=';
    nom_lac = nom_lac.replace(' ', '%20');
    url = base + nom_lac;
    page = urllib.request.urlopen(url);
    page = page;
    corps = str(page.read().decode('utf-8'));
    
    adresse = corps[corps.find('"formatted_address" : "')+23:corps.find('"geometry" : {')-12]; #Adresse formelle
    print('Récupération infos de ' + str(adresse));
    
    corps0 = corps.split('"northeast"')[1];
    latNE = corps[corps.find('"lat"')+7:corps.find('"lat"')+18]; 
    lonNE = corps[corps.find('"lng"')+7:corps.find('"lng"')+18];
    
    corps1 = corps.split('"southwest"')[1];
    latSO = corps1[corps1.find('lat')+7:corps1.find('"lat"')+18];
    lonSO = corps1[corps1.find('"lng"')+7:corps1.find('"lng"')+18];
    
    corps2 = corps.split('"location"')[1];
    latCe = corps2[corps2.find('"lat"')+7:corps2.find('"lat"')+18];
    lonCe = corps2[corps2.find('"lng"')+7:corps2.find('"lng"')+18];

    return(adresse, latCe, lonCe, latNE, lonNE, latSO, lonSO);

#print(getInfoLac('lac a la truite, Orford'));
