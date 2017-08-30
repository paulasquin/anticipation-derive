import math
import webbrowser

maptype = 'hybrid';
apiKey = '';
showLabels = 0;
language = '';

def getImageMaps(markerlist):

    scale = 2;
    width = 640
    height = 640;
    
    # Construct query URL
    preamble = 'http://maps.googleapis.com/maps/api/staticmap';
    #location = '?center=' + str(lat) + ',' + str(lon);
    location = '';
    #zoomStr = '&zoom=' + str(zoomlevel);
    zoomStr = '';
    sizeStr = '?scale=' + str(scale) + '&size=' + str(width) + 'x' + str(height);
    maptypeStr = '&maptype=' + maptype;
    if len(apiKey)!=0:
        keyStr = '&key=' + apiKey;
    else:
        keyStr = '';
        
    markers = '&markers=';
    for idx in range(len(markerlist)):
        if len(markers) < 1900:#Limite d'affichage des caractéres
            if idx < len(markerlist):
                markers = markers + markerlist[idx] + '%7C';
            else:
                markers = markers + markerlist[idx];
        else:
            print('Limitation affichage carte : trop de point pour url');
            break;
    if showLabels == 0:
        labelsStr = '&style=feature:all|element:labels|visibility:off';
    else:
        labelsStr = '';
        
    if len(language)!=0:
        languageStr = '&language=' + language;
    else:
        languageStr = '';
        
    if maptype in ['satellite','hybrid']:
        filename = 'tmp.jpg';
        form = '&format=jpg';
        convertNeeded = 0;
    else:
        filename = 'tmp.png';
        form = '&format=png';
        convertNeeded = 1;
        
    sensor = '&sensor=false';
    url = preamble + location + zoomStr + sizeStr + maptypeStr + form + markers + labelsStr + languageStr + sensor + keyStr;
    webbrowser.open(url);
    return(0);

