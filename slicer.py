def acceptCommand():
    choice = input("Select function:\n1 - listNetElements\n2 - listSlicingProfiles\n3 - listActiveProfiles\n4 - createNewProfile\n55555 - toggleProfile\n0 - exit\n")
    if choice == "0":
        return False
    elif choice == "1":
        listNetElements()
        return True
    elif choice == "2":
        listSlicingProfiles()
        return True
    elif choice == "3":
        listActiveProfiles()
        return True
    elif choice == "4":
        createNewProfile("generic")
        return True
    elif choice == "5":
        toggleProfile(2)
        return True
    
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

while(acceptCommand()):
    a = 0

