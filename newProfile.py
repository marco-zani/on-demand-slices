import json

def uploadData(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def saveData(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def newProfile(file_path):
    # Carica i dati dal file
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


# Nome del file JSON
file_path = 'profiles.json'
newProfile(file_path)
