import math
import webbrowser

maptype = 'hybrid';
apiKey = 'AIzaSyCjrrMzllhGLtrCvcudwJuPchbkUHoqdSQ';
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
        if idx < len(markerlist):
            markers = markers + markerlist[idx] + '%7C';
        else:
            markers = markers + markerlist[idx];
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

    print(url);
    webbrowser.open(url);

##    urlwrite(url,filename);
##    [M, Mcolor] = imread(filename);
##    M = cast(M,'double');
##    delete(filename); # delete temp file
    
#getImageMaps();


