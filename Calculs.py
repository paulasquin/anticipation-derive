import math

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

def distanceGPS(a, b):#Donne la distance en mètres entre 2 points GPS, à partir de coord décimales.
    latA = float(a[0])*math.pi/180;#B2
    lonA = float(a[1])*math.pi/180;#C2
    latB = float(b[0])*math.pi/180;#B3
    lonB = float(b[1])*math.pi/180;#C3
    dist=math.acos(math.sin(latA)*math.sin(latB)+math.cos(latA)*math.cos(latB)*math.cos(lonA-lonB))*6371000
    return(int(abs(dist)));

def angleGPS(x,y):#Donne l'angle en ° relatif GPS d'un déplacement [x, y]
    #Latitude : longitude = 0.
    lat=arrondir(y/6371000*180/math.pi, 6);
    lon=arrondir(x/6371000*180/math.pi, 6);
    return([lat, lon]);

def arrondir(x, n):#Arrondir x à n chiffre après la virgule
    x = int(x*10**n)/10**n;
    return(x);

def latLonToMeters(lat, lon ):
    # Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913"
    originShift = 2 * np.pi * 6378137 / 2.0; # 20037508.342789244
    x = lon * originShift / 180;
    y = log(tan((90 + lat) * np.pi / 360 )) / (np.pi / 180);
    y = y * originShift / 180;
    return([x, y]);

    
