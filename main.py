# Import Libraries (AKA the epic import arch)
from dotenv import load_dotenv, dotenv_values
from configparser import ConfigParser
from picamera2 import Picamera2
import numpy as np
import subprocess
import datetime
import signal
import time
import glob
import cv2
import re
import os

# Load Picamera Instance
Camera = Picamera2()

# Load Directories
ProcessedImagesFolder = os.path.join(os.path.dirname(__file__), 'ProcessedImages')
RawImagesFolder = os.path.join(os.path.dirname(__file__), 'RawImages')
StaticImagesFolder = os.path.join(os.path.dirname(__file__), 'static')

# Load config.ini Values
ConfigFile = 'config.ini'
Config = ConfigParser()
Config.read(ConfigFile)

ImageInterval = Config['ImagingControl']['ImageInterval'] # Gets all of the settings from the config file
BlockSize = Config['ImageAnalysis']['BlockSize']
GitHubRepoName = Config['GitHubConfig']['RepoName']
Candidates = Config['ImageAnalysis']['Candidates']

# Load .env Values
load_dotenv()
GitHubUN = os.getenv("GitHubUN")
GitHubPAT = os.getenv("GitHubPAT")

# Repository
GitHubRepo = f"https://{GitHubUN}:{GitHubPAT}@github.com/{GitHubUN}/{GitHubRepoName}.git" # Variables in .env

# Functions
def CaptureImage():
    global Cv2ImageNameCache
    global CurrentDateTime
    Camera.start()
    CurrentDateTime = datetime.datetime.now().isoformat()
    Camera.capture_file(f"{RawImagesFolder}/IMG_{CurrentDateTime}.jpg")
    Cv2ImageNameCache = f"{RawImagesFolder}/IMG_{CurrentDateTime}.jpg"
    Camera.stop() # Prevents interpreter from getting angry, stops it from being accessed twice by the MissionSoftware Loop

Running = True

def HandleExit(signum, frame):
    global Running
    print("\nShutting down safely...")
    Running = False

signal.signal(signal.SIGINT, HandleExit)

def UpdateRepository():
    subprocess.run(["git", "add", "--ignore-removal", "."]) # --ignore-removal so that captured images remain on repo even after they are locally deleted.
    CommitMessage = "SuperSAT Bot - Automatic Upload"
    subprocess.run(["git", "commit", "-m", CommitMessage])
    subprocess.run(["git", "remote", "set-url", "origin", GitHubRepo])
    subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check = True) # --force to overide GitHub repo

def AnalyzeImage():
    FinalImage = cv2.imread(Cv2ImageNameCache)
    BlackAndWhiteImage = cv2.cvtColor(FinalImage, cv2.COLOR_BGR2GRAY) # Convert the starting image to black and white (removes color shading bias)

    Height, Width = BlackAndWhiteImage.shape # Gets the height and width of image
    IntBlockSize = int(BlockSize)
    Results = []

    for y in range(0, Height - IntBlockSize, IntBlockSize): # Scan through rows
        for x in range(0, Width - IntBlockSize, IntBlockSize): # Scan through columns
            RegionOfInterest = BlackAndWhiteImage[y:y+IntBlockSize, x:x+IntBlockSize]
            Variation = np.std(RegionOfInterest) # Get each block region standard deviation amount (roughness value)
            Results.append(((x, y), Variation)) # Add it to results list with coordinates

    Results.sort(key=lambda x: x[1])
    TopRegions = Results[:int(Candidates)] # Sort from least deviation to most and get the top candidates, specified in config.ini

    for (x, y), var in TopRegions: # Visualize each region via blocksize and write the standard deviation of each on screen
        cv2.rectangle(FinalImage, (x, y), (x + IntBlockSize, y + IntBlockSize), (0, 255, 0), 2)
        cv2.putText(FinalImage, f"{var:.2f}", (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 3)
        cv2.putText(FinalImage, f"{var:.2f}", (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

    cv2.putText(FinalImage, f"SuperSAT PRO_{CurrentDateTime}.jpg", (7,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
    cv2.putText(FinalImage, f"SuperSAT PRO_{CurrentDateTime}.jpg", (7,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1) # Image names in top left (Two to make it visible: One black, one white)

    cv2.imwrite(f"{ProcessedImagesFolder}/PRO_{CurrentDateTime}.jpg", FinalImage)
    cv2.imwrite(f"{StaticImagesFolder}/PRO_{CurrentDateTime}.jpg", FinalImage) # Save images to respective directories (Both 92 and 93)

def PrintLogoLine(): # Epic Ascii art :D
    print("""===============================================================================================
===============================================================================================""")
    print(""" .oooooo..o                                            .oooooo..o       .o.       ooooooooooooo 
d8P'    `Y8                                           d8P'    `Y8      .888.      8'   888   `8 
Y88bo.      oooo  oooo  oo.ooooo.   .ooooo.  oooo d8b Y88bo.          .8"888.          888      
 `"Y8888o.  `888  `888   888' `88b d88' `88b `888""8P  `"Y8888o.     .8' `888.         888      
     `"Y88b  888   888   888   888 888ooo888  888          `"Y88b   .88ooo8888.        888      
oo     .d8P  888   888   888   888 888    .o  888     oo     .d8P  .8'     `888.       888      
8""88888P'   `V88V"V8P'  888bod8P' `Y8bod8P' d888b    8""88888P'  o88o     o8888o     o888o     
                         888                                                                    
                        o888o                                                                   """)
    print("""===============================================================================================
===============================================================================================""")

def PrintLine():
    print("""===============================================================================================
===============================================================================================""")

def ClearTerminal():
    subprocess.run(["clear"])

def MainMenu():
    ClearTerminal()
    MainMenuChoiceLoop = True
    while MainMenuChoiceLoop == True: # The main choice loop, just in case the user puts in an invalid choice
        PrintLogoLine()
        print("What would you like to do?")
        print("[1] Execute Mission Software")
        print("[2] Execute Purge.py")
        print("[3] Display Tunnel URL")
        print("[4] Exit")
        
        MainMenuChoice = input("> ")
        try:
            MainMenuChoice = int(MainMenuChoice)
        except (ValueError, TypeError):
            pass

        if MainMenuChoice ==  1: # Mission Code
            ClearTerminal()
            print("Mission Code Working...") # Indicate choice 1 was selected while Pi-Camera loads
            while Running:
                CaptureImage()
                AnalyzeImage()
                time.sleep(int(ImageInterval)-0.5)
                UpdateRepository()
                time.sleep(0.5)
                subprocess.run(f"sudo rm -rf {ProcessedImagesFolder}/*", shell=True)
                subprocess.run(f"sudo rm -rf {RawImagesFolder}/*", shell=True)
                subprocess.run(f"sudo rm -rf {StaticImagesFolder}/*", shell=True)

        elif MainMenuChoice == 2: # Clears ALL image files, GitHub and SD card
            ClearTerminal()
            subprocess.run(["python3", "purge.py"])
            pass
            ClearTerminal()

        elif MainMenuChoice == 3: # Shows the webapp tunnel URL
            ClearTerminal()
            print(TunnelURL)
            print()
            WaitEnter = input("Press enter to return ")
            ClearTerminal()
        
        elif MainMenuChoice == 4: # Leaves
            ClearTerminal()
            exit()

        else:
            print("Invalid entry, please enter a valid option.") # If an unknown input is entered
            time.sleep(1.25)
            ClearTerminal()

            pass


# Main Program
if __name__ == "__main__":
    try:
        HostFlaskSubprocess = subprocess.Popen( # Locally host the webapp to then be tunneled with cloudflared
        ["python3", "hostapp.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
        time.sleep(1)

        ClearTerminal()

        time.sleep(1)
        CloudflaredProcess = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://127.0.0.1:8080"], # Sets up tunnel from localhost (8080)
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)

        print("Starting tunnel, please wait...") # Indicate that the tunnel is starting and the program hasn't broken

        TunnelURL = None
        try: # Save the tunnel to a text file so its easy to view (And updates on GitHub)
            for line in CloudflaredProcess.stderr:
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    TunnelURL = match.group(0)
                    print(f"Tunnel active: {TunnelURL}")
                        
                    with open("TunnelURL.txt", "w") as f:
                        f.write(TunnelURL)
                    break 
                    
        except Exception as e:
            print(f"Error: {e}")
            pass

        if not TunnelURL:
            print("Failed to retrieve tunnel URL.")
            pass

        print("Parameters (config.ini)") # Prints all of the currently set variables as they are in settings
        print(Config.read(ConfigFile))
        print(f"ImageInterval: {ImageInterval}")
        print(f"BlockSize: {BlockSize}")
        print(f"GitHubRepoName: {GitHubRepoName}")
        print(f"Candidates: {Candidates}")
        MainMenu()
    except KeyboardInterrupt: # To (hopefully) prevent the GitHub repository from corrupting upon ending the program
        subprocess.run(f"sudo rm -rf {ProcessedImagesFolder}/*", shell=True)
        subprocess.run(f"sudo rm -rf {RawImagesFolder}/*", shell=True)
        subprocess.run(f"sudo rm -rf {StaticImagesFolder}/*", shell=True)
        with open(f"TunnelURL.txt", "w") as f:
            f.write('')
        HostFlaskSubprocess.terminate()
        ClearTerminal()
        exit()