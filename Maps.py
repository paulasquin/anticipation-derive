def getImageMaps():
    tileSize = 256;
    scale = 1;
    initialResolution = 2 * np.pi * 6378137 / tileSize;

    
##    [xExtent,yExtent] = latLonToMeters(curAxis(3:4), curAxis(1:2) );
##    width = size(M,2);
##    height = size(M,1);
    width = resX;
    heigth = resY;
    minResX = diff(xExtent) / width;
    minResY = diff(yExtent) / height;
    minRes = max([minResX minResY]);
    
    zoomlevel = int(np.log2(initialResolution/minRes));

    if zoomlevel < 0 
        zoomlevel = 0;
    if zoomlevel > 19 
        zoomlevel = 19;
    
    curResolution = initialResolution / 2^zoomlevel/scale; # meters/pixel (EPSG:900913)
    
    # Calculate center coordinate in WGS1984
    lat = (curAxis(3)+curAxis(4))/2;
    lon = (curAxis(1)+curAxis(2))/2;

    # Construct query URL
    preamble = 'http://maps.googleapis.com/maps/api/staticmap';
    location = ['?center=' num2str(lat,10) ',' num2str(lon,10)];
    zoomStr = ['&zoom=' num2str(zoomlevel)];
    sizeStr = ['&scale=' num2str(scale) '&size=' num2str(width) 'x' num2str(height)];
    maptypeStr = ['&maptype=' maptype ];
    if ~isempty(apiKey)
        keyStr = ['&key=' apiKey];
    else
        keyStr = '';
    end
    markers = '&markers=';
    for idx = 1:length(markerlist)
        if idx < length(markerlist)
            markers = [markers markerlist{idx} '%7C'];
        else
            markers = [markers markerlist{idx}];
        end
    end
    if showLabels == 0
        labelsStr = '&style=feature:all|element:labels|visibility:off';
    else
        labelsStr = '';
    end
    if ~isempty(language)
        languageStr = ['&language=' language];
    else
        languageStr = '';
    end
        
    if ismember(maptype,{'satellite','hybrid'})
        filename = 'tmp.jpg';
        format = '&format=jpg';
        convertNeeded = 0;
    else
        filename = 'tmp.png';
        format = '&format=png';
        convertNeeded = 1;
    end
    sensor = '&sensor=false';
    url = [preamble location zoomStr sizeStr maptypeStr format markers labelsStr languageStr sensor keyStr];

    urlwrite(url,filename);
    [M, Mcolor] = imread(filename);
    M = cast(M,'double');
    delete(filename); % delete temp file
    
    


