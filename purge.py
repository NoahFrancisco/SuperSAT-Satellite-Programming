# Import Libraries
import subprocess
import os

# Directories
ProcessedImagesFolder = os.path.join(os.path.dirname(__file__), 'ProcessedImages') # Just gets the directories for all of the local files
RawImagesFolder = os.path.join(os.path.dirname(__file__), 'RawImages')
StaticImagesFolder = os.path.join(os.path.dirname(__file__), 'static')

# Newline Function
def Newline():
    print('')

# Accident Protection / Main Script
Loop = True

while Loop == True:
    Newline()
    print("This action is NOT REVERSABLE. Are you sure you want to DELETE ALL IMAGES locally and in the GitHub repository? [Y/n]") # Make sure stuff doesn't get deleted by accident
    UserChoice = input("> ")

    if UserChoice == 'Y': # Send everything to the shadow realm
        Loop = False
        subprocess.run(f"sudo rm -rf {ProcessedImagesFolder}/*", shell=True)
        subprocess.run(f"sudo rm -rf {RawImagesFolder}/*", shell=True)
        subprocess.run(f"sudo rm -rf {StaticImagesFolder}/*", shell=True)
        subprocess.run(f"git add .", shell=True)
        CommitMessage = "SuperSAT Bot - Remove RawImages and ProcessedImages Directories"
        subprocess.run(f"git commit -m \"{CommitMessage}\"", shell=True)
        subprocess.run(f"git push origin main", shell=True)
        Newline()
        print("Purge Completed Successfully!")

    elif UserChoice == 'y': # Send everything to the shadow realm (but lowercase this time)
        Loop = False
        subprocess.run(f"sudo rm -rf {ProcessedImagesFolder}/*", shell=True)
        subprocess.run(f"sudo rm -rf {RawImagesFolder}/*", shell=True)
        subprocess.run(f"sudo rm -rf {StaticImagesFolder}/*", shell=True)
        subprocess.run(f"git add .", shell=True)
        CommitMessage = "Remove RawImages and ProcessedImages Directories"
        subprocess.run(f"git commit -m \"{CommitMessage}\"", shell=True)
        subprocess.run(f"git push origin main", shell=True)
        Newline()
        exit("Purge Completed Successfully!")

    elif UserChoice == 'N': # Nope
        Loop = False
        exit("Program Aborted")
        exit(0)

    elif UserChoice == 'n': # Nope (but lowercase this time)
        Loop = False
        exit("Program Aborted")
        exit(0)
    
    else:
        Newline()
        print("Invalid entry, please enter a valid option.") # User entered incorrect option