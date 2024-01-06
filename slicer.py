import json

#Variabile globale per slice attiva, valore default
sliceActive = 1

def acceptCommand():
    choice = input("\nSelect function:\n1 - listNetElements\n2 - listSlicingProfiles\n3 - listActiveProfiles\n4 - createNewProfile\n5 - toggleProfile\n0 - exit\n")
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
        toggleProfile()
        return True

def listNetElements():
    print("\nListing defualt network")
    file_path = 'networkFile.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    #Ciclo while che stampa ogni elemento del file
    i = 0
    while i < len(data):
        print(json.dumps(data[i],indent=4))
        i+=1

def listSlicingProfiles():
    print("\nListing all profiles")
    file_path = 'profiles.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    #Ciclo while che stampa ogni elemento del file
    i = 0
    while i < len(data):
        print(json.dumps(data[i],indent=4))
        i+=1

def listActiveProfiles():
    print("\nListing active profiles")
    file_path = 'profiles.json'
    with open(file_path, 'r') as file:
        data = json.load(file)

    #Stampa dati relativi alla variabile globale selezionata
    print(json.dumps(data[sliceActive-1],indent=4))

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

def toggleProfile():
    profileId = input("\nQuale slice vuoi attivare?:")
    global sliceActive 
    sliceActive = int(profileId)
    print("\nActivating profile n." + str(sliceActive))

while(acceptCommand()):
    a = 0
