import json

def convert_slice_to_port(slice_data):
    slice_id = list(slice_data.keys())[0]
    links = slice_data[slice_id]['links']

    switch_ports = {}

    for link in links:
        source = link['source']
        target = link['target']

        # Estrai il numero dello switch dalla stringa
        source_switch = int(source[1:])
        target_switch = int(target[1:])

        # Configura le porte per i collegamenti tra switch
        if source[0] == 's' and target[0] == 's':
            if source_switch not in switch_ports:
                switch_ports[source_switch] = {}
            if target_switch not in switch_ports:
                switch_ports[target_switch] = {}

            source_port = links.index(link) + 1
            target_port = links.index(link) + 1

            switch_ports[source_switch][source_port] = target_port
            switch_ports[target_switch][target_port] = source_port

    return {slice_id: switch_ports}

# Esempio di utilizzo
slices_json = [
    {
        "slice1": {
            "id": 1,
            "links": [
                {"source": "h1", "target": "s1"},
                {"source": "h2", "target": "s1"},
                {"source": "s1", "target": "s2"},
                {"source": "s2", "target": "h3"},
                {"source": "s2", "target": "h4"}
            ]
        }
    },
    {
        "slice2": {
            "id": 2,
            "links": [
                {"source": "h1", "target": "s1"},
                {"source": "s1", "target": "s2"},
                {"source": "h4", "target": "s2"}
            ]
        }
    }
]

slice_to_port = {}

for slice_data in slices_json:
    slice_id = list(slice_data.keys())[0]
    slice_to_port.update(convert_slice_to_port(slice_data))

print(slice_to_port)
