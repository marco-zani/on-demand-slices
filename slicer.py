import json

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
        createNewProfile()
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

def uploadData(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def saveData(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def createNewProfile():
    # Carica i dati dal file
    file_path = 'profiles.json'
    dati_originali = uploadData(file_path)

    # Get id attuale massimo
    max_id = max(entry[next(iter(entry))]['id'] for entry in dati_originali)
    next_id = max_id + 1

    # Aggiungi una nuova slice
    nuova_slice_name = input("Inserisci il nome della nuova slice: ")

    # Crea la nuova slice
    nuova_slice = {
        nuova_slice_name: {
            "id": next_id,
            "links": []
        }
    }

    # Inserimento links
    while True:
        source_host = input("Inserisci l'host sorgente: ")
        target_host = input("Inserisci l'host di destinazione: ")

        nuova_slice[nuova_slice_name]['links'].append({
            "source": source_host,
            "target": target_host
        })
        risposta = input("Vuoi inserire un altro collegamento? (s per si, n per uscire): ")
        if risposta.lower() == 'n':
            break

    dati_originali.append(nuova_slice)

    # Salva i dati aggiornati nel file
    saveData(dati_originali, file_path)

    print("Aggiunta nuova slice con id -> " + str(next_id))



def toggleProfile(profileId):
    print("Activating profile n." + str(profileId))

while(acceptCommand()):
    a = 0
