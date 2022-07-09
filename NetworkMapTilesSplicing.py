# testServer:OpenStreetMap-Docker:2.0.0

from PIL import Image
import requests
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
    return(areaList)
    
def GetNetworkPictures(infoDict):
    tilesUrl= "http://localhost:8080/tile/{z}/{x}/{y}.png" # target tiles server address
    tilesUrl= tilesUrl.format(**infoDict)
    tilePic = requests.get(tilesUrl)
    return tilePic



def main():
    xList= yList= []
    
    zoomRate= input("Zoom Level (Z): ")
    p1X, p1Y= map(int,input("Location1 (x,y): ").split(","))
    p2X, p2Y= map(int,input("Location2 (x,y): ").split(","))

    #Sort, start from small location
    xList= [p1X,p2X]
    xList.sort()
    yList= [p1Y,p2Y]
    yList.sort()

    #TODO:Config Dictionary
    #TODO:Split Pages
    #TODO:Dark Mode
    
    p1X, p2X= map(int,xList)
    p1Y, p2Y= map(int,yList)

    areaList= CalcAreaLong(xList,yList) 
    areaPixelLong= areaList[0]
    areaTilesLong= areaList[1]
    
    targetPic = Image.new('RGBA',areaPixelLong)
    
    #Paste the tile to big tile
    picX= picY= 0
    for nowX in range(p1X,p2X+1):
        picY= 0 
        for nowY in range(p1Y,p2Y+1):
            tryCount= 0
            print("Processing({}, {}), Total{}".format(picX,picY,areaTilesLong))
            while True and tryCount < 10: #trying again because some network error.
                try:
                    tryCount+= 1
                    locateDict= dict({"z":zoomRate,"x":nowX,"y":nowY}) 
                    currentNetworkFile= GetNetworkPictures(locateDict) 
                    
                    currentFile= open(".\\~temp\\~temp.png","wb") # Windows path,and you need create a folder'~temp'.
                    currentFile.write(currentNetworkFile)
                    currentFile.close()

                    currentPic= Image.open(".\\~temp\\~temp.png")
                    currentCopyPic= currentPic.copy()
                    currentPic.close()
                    picLocation= (picX*256,picY*256) #Every tile size is 256*256
                    targetPic.paste(currentCopyPic,picLocation)
                    picY+= 1
                except:
                    print("Error y= {}, retry {}.".format(picY,tryCount))
                    continue
                break
        picX+= 1
    targetPic.save(".\\~temp\\test-Z"+ str(zoomRate)+ "-Size"+ str(areaTilesLong)+ "-L("+ str(p1X)+ ","+ str(p1Y)+ ")to("+ str(p2X)+ ","+ str(p2Y)+ ").png")
    print("Finish.")

if __name__== "__main__":
    main()
