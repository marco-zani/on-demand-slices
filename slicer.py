from time import sleep

class Slicer:
    def __init__(self, send) -> None:
        self.send = send
        pass

    def listNetElements():
        print("Listing elements...")
    def listSlicingProfiles():
        print("Listing profiles...")
    def listActiveProfiles():
        print("Listing profiles...")
    def createNewProfile(params):
        print("Creating profile with paramas:" + str(params))
    def toggleProfile(profileId):
        print("Activating profile n." + str(profileId))

    def acceptCommand(self):
        choice = input("Select function:\n1 - listNetElements\n2 - listSlicingProfiles\n3 - listActiveProfiles\n4 - createNewProfile\n5 - toggleProfile\n0 - exit\n")
        if choice == "0":
            return False
        elif choice == "1":
            self.listNetElements()
            return True
        elif choice == "2":
            self.listSlicingProfiles()
            return True
        elif choice == "3":
            self.listActiveProfiles()
            return True
        elif choice == "4":
            self.createNewProfile("generic")
            return True
        elif choice == "5":
            profile = input("insert profile id:")
            self.send(profile)
            return True
        
    def start(self):
        while(self.acceptCommand()):
            sleep(0.5)
        

