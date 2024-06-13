# On Demand Slices
This is an academic project for the Softwarized and Virtualized Mobile Networks / Netowrking Module II course at the University of Trento.

## Project Goal
The main goal of the project is to implement a network slicing approach to enable dynamic activation/de-activation of network slices via CLI/GUI commands

## Setup the environment
The project relies on ComNetsEmu, a testbed and network emulator that already provides all the dependencies we need to start the Ryu application and the MiniNET topology. More information about it can be found [here](https://git.comnets.net/public-repo/comnetsemu). We personally installed it by cloning the repository and using Vagrant. 

The only necessary library to install before executing this demo is `dill`, which can be installed by running the command:
```
pip install dill
```


If installed in this way, the project can be easily started by following these steps:

1. Start the Virtual Machine and get access to a shell
2. Start the Vagrant Machine of comnetsemu
3. Clone the repository: 
    ```
    git clone https://github.com/marco-zani/on-demand-slices.git
    ```
4. Move inside the repo directory: 
    ```
    cd on-demand-slices
    ```
5. Start the mininet network by executing
    ```
    sudo python3 network.py
    ```
6. Open another terminal to run the Ryu controller
    ```
    ryu-manager controller.py
    ```
7. Open the third terminal, outside Vagrant machine, and run
    ```
    python3 net-slice.py
    ```
This will run the GUI of the application.

## UI functionalities
Through the UI realised using the GTK module, it is possible to navigate through the different sections:
- Network View: represents the network with devices and connections
- Active Slice View: show the active profile and enable the selection of the profile through a dropdown menu. In the descriptor is shown the devices and the connections of the different slices included in that profile.
- Profiles View: show all the possible profiles with the list of slices included. In the bottom there is the button "Create new profile"
- Create new profile: enable to create a custom profile with custom slices and setting the QoS.

## Report
For all the technical details please refer to the full report inside the docs directory of this repo.
