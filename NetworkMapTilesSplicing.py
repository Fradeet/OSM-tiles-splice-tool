# testServer:OpenStreetMap-Docker:2.0.0

from PIL import Image,ImageEnhance,ImageOps
import requests
import colorsys
print("Hallo Earth!")

# Initialize global variables

def CalcAreaLong(xList,yList):
    areaList= []
    
    xLong= xList[1]- xList[0]+ 1 # Area length
    yLong= yList[1]- yList[0]+ 1 # Both include the tile of the last one 
    
    areaTilesLong= (xLong-1,yLong-1)# Count start from 1
    areaPixelLong= (xLong*256,yLong*256)# A big combined tile size 
    areaList.append(areaPixelLong)
    areaList.append(areaTilesLong)
    return areaList
    
def GetNetworkPictures(infoDict):
    tilesUrl= "http://192.168.31.182:8080/tile/{z}/{x}/{y}.png" # target tiles server address
    tilesUrl= tilesUrl.format(**infoDict)
    tilePic = requests.get(tilesUrl)
    return tilePic

def DarkTile(tile):
    #Like CSS render

    tile= ImageEnhance.Brightness(tile)
    tile= tile.enhance(0.6)

    try:
        invertedTile = ImageOps.invert(tile)
        tile= invertedTile
    except:#Can't direct convert PNG
        r,g,b,a = tile.split()
        rgbTile = Image.merge('RGB', (r,g,b))
        invertedTile = ImageOps.invert(rgbTile)
        r,g,b = invertedTile.split()
        rgbaTile = Image.merge('RGBA', (r,g,b,a))
        tile= rgbaTile

    tile= ImageEnhance.Contrast(tile)
    tile= tile.enhance(3)
    tile= ImageEnhance.Color(tile)
    tile= tile.enhance(0.3)

    colorDict= dict()
    pixelArray = tile.load()
    width, height = tile.size
    for x in range(0,width):
        for y in range(0,height):
            rgb = pixelArray[x,y]
            try:
                pixelArray[x,y]= colorDict[str(rgb)] #Boost by before color pixel
            except:
                hls1= colorsys.rgb_to_hls(rgb[0]/255,rgb[1]/255,rgb[2]/255) #colorsys is 0~1
                hls1H= (hls1[0]*360+200)/360 #add 200 degrees
                if hls1H > 1:
                    hls1H= hls1H- 1
                rgb1= colorsys.hls_to_rgb(hls1H,hls1[1],hls1[2])
                rgbGroup= (int(rgb1[0]*255),int(rgb1[1]*255),int(rgb1[2]*255)) # has deviation
                pixelArray[x,y]= colorDict[str(rgb)]= rgbGroup

    tile= ImageEnhance.Brightness(tile)
    tile= tile.enhance(0.7)
    return tile

def SpliceTiles(targetPic,zoomRate,x1,x2,y1,y2,areaTilesLong):
    #Paste the tile to big tile
    picX= picY= 0

    for nowX in range(x1,x2+1):
        picY= 0 
        print("Processing({}, {}), Total{}".format(picX,picY,areaTilesLong))
        for nowY in range(y1,y2+1):
            tryCount= 0
            while True and tryCount < 10: #trying again because sometime network error.
                try:
                    locateDict= dict({"z":zoomRate,"x":nowX,"y":nowY}) 
                    currentNetworkFile= GetNetworkPictures(locateDict) 
                    
                    currentFile= open(".\\~temp.png","wb") # Windows path,and you need create a folder'~temp'.
                    for chunk in currentNetworkFile.iter_content(100000): #must
                        currentFile.write(chunk)
                    currentFile.close()

                    currentPic= Image.open(".\\~temp.png")
                    currentCopyPic= currentPic.copy()
                    currentPic.close()
                    picLocation= (picX*256,picY*256) #Every tile size is 256*256
                    targetPic.paste(currentCopyPic,picLocation)
                    picY+= 1
                except:
                    tryCount+= 1
                    print("Error y= {}, retry {}.".format(picY,tryCount))
                    continue
                break
        picX+= 1
    return targetPic



def main():
    xList= yList= []
    userConfig= dict({"DarkMode":0}) #Initialize, it's better to don't edit
    
    zoomRate= input("Zoom Level (Z): ")
    location1X,location1Y= map(int,input("Location1 (x,y): ").split(","))
    location2X,location2Y= map(int,input("Location2 (x,y): ").split(","))
    userConfig["DarkMode"]= int(input("Need dark tiles? (1 is yes, 0/None is no.):"))

    #Sort, start from small location
    xList= [location1X,location2X]
    xList.sort()
    yList= [location1Y,location2Y]
    yList.sort()

    #TODO:Split Pages

    location1X, location2X= xList
    location1Y, location2Y= yList

    areaList= CalcAreaLong(xList,yList) 
    areaPixelLong= areaList[0]
    areaTilesLong= areaList[1]
    targetPic= Image.new('RGBA',areaPixelLong)
    targetPic= SpliceTiles(targetPic,zoomRate,location1X,location2X,location1Y,location2Y,areaTilesLong)

    if userConfig["DarkMode"]== True:
        print("Convert to dark...")
        targetPic= DarkTile(targetPic)

    targetPic.save(".\\tile-Z"+ str(zoomRate)+ "-Size"+ str(areaTilesLong)+ "-L("+ str(location1X)+ ","+ str(location1Y)+ ")to("+ str(location2X)+ ","+ str(location2Y)+ ").png")
    print("Finish.")

if __name__== "__main__":
    main()
