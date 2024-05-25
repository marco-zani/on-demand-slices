# Back end
The back-end is composed by the class `Slicer` who manages, creates and shares the slices configurations. In detail, the slicer object contains the Udp socket used for exchanging data with the controller, the list of profiles, and index to keep track of the active profile and a datastructure representing the network topology

## Slicer
The slicer offers 2 main functions: The initialization and the ability to toggle a specific profile

### Initialization
The inizialization requires the slicer to load all the data from the `profiles.json` file and convert it to usable `Profile` objects. The JSON file is organized to store `id` and `name` of a profile, plus an array of `slices`, each element containing the list of `devices` and a `maxBandwidth` value
Afterwards the slicer creates an empty `Topology` object and loads the different links in the network topology from mininet. Lastly it takes the association between hostname, and its IP and MAC addresses and sends it to the controller using the `sendDevices()` function.

### Enabling a profile
The other function, `toggleProfile()`, uses the index passed as argument, and requests to the `Topology` to convert the profile using that index into an usable controller configuration. It then converts the configuration into a stream of bytes and sends it to the controller using the `sendUDP()` function.
The convertion into a `bytestream` using the `dill` library is important because it automatically manages the convertion from `bytestream` into a dictionary instead of needing to manually parse a `str` into the dictionary

## Topology
The `Topology` class is responable with managing the information regarding the network topology, keeping a copy of the current active configuration and converting a given profile into a controller configuration

### Storing devices data
Each end point is saved as a dictionary using the name as key, and using as value a list of tuples containing the other connection device and the port used. 
Because the data passed from mininet lists only links, the topology is populated using the `addLink` function, who tries to source and destination devices, if not already present, to the topology, and then appends the link data to each device connections list, always if not already present.

### Converting profiles into a configuration
The `convertProfileInConfiguration()` function accepts a profile as argument, then for each slice extracts all the contained devices list,their amount and how much bandwidth must be reserved. Then for each device extract all the data from the topology regarding that element. 
With all this informations, uses the functions provided by the `floydWarshall.py` file to build up the configuration. In order:
 1. Initializes an empty table the size of all devices in the slice
 2. Uses the Floyd-Warshall algorithm to create the next hop matrix
 3. Removes all cells where there is no connection
 4. Converts the matrix in a dictionary
 5. Inserts the port necessary for the next hop
 6. Removes all the records that do not regard switches
After performing this actions on all slices, it lastly compares all the reserved bandwidth requiremes, so that on every link can be detected the most efficient bandwidth separation.

## Floyd-Warshall 
The `floydWarshall.py` file is an utility file providing a list of function used to calculate the shortest path between all couples of nodes and converting this table in a configuration usable by the controller

### initMatrix()
It generates an adjacency matrix n x n where n is the number of devices in the slice

### compute_next_hop()
Applies the Floyd-Warshall algorithm, which uses a Dynamic Programming approach to check every possible path going via every possible node in order to calculate shortest distance between every pair of nodes.
### shrinkTable()
It converts the matrix into a list of lists, where at each index corresponds a device, and inside the list are contained tuples indicating which devices are reachable forwarding which device

This convertion removes all the empty cells of the matrix, compacting the data
### convertToDict()
It converts the list of lists into a dictionary, using the device associated with the index as key, and storing the sublist as value
### convertPorts()
Exchanges the device name used inside the tuples in the dictionary values for the port to use to reach them
### extractSwitches()
Removes all keys regarding devices that are not switches, since the controller has no use for them
### add_max_bandwidth()
It compares all links which are common between slices, if any are found, it enforces the each link to split bandwidth according to the required value


# UI components
Found inside the `slicer_UI.py` file, the class `Visualizer` is responsable for presenting the application window after calling the class `SlicerWindow` which is responsable to build the UI, while also initializing the `Slicer`, importing the topology from `mininet` and sending the list of devices in the net to the `controller`.It also manages the event `updateProfiles`

## Applications views
The user interface offers three views: network, profiles and active slices, interchangeable like a carousel using the related buttons. This allowes the application to maintain a coherent look and behavior. Each view is loaded individually and incapsulated inside a wrapper using `SlicerWindow.buildWrapper()` which accepts the function used to build the spicific view. This wrapper has been implemented allways with look coherency as the objective.

### Network view
This view has been created with the purpouse of presenting in a minimal and clear way, which devices are contained in the network and which port do they use to connect with each other. This is done by formatting the data contained in the slicer topology.

The data is separeted in two columns balanced to occupy less space possible using the `splitArray()` function

### Active slice view
Used for selecting the slice to apply on the network, the active slice view presents a dropdown menu listing all the profiles that have been loaded from the `Slicer`. This component is custom made using object inheritance to simplify the component usage. Indeed the normal usage of the GTK dropdown requires the creation of a data model and factory, plus the specification of setups and binding of each dropdown element. 

The `SimpleDropDown` widget instead only takes the list of elements and the index of the selected element as constructor's arguments, while automatically managing all the previous requirements. This widget also manages the signal `dropDownElementSelected` used to update the active configuration through the `updateActiveSlice()` function

Upon selecting a slice, two functions are called, one to update the dropdown widget with the selected item (`updateDropDown()`) and another to display the network configuration (`updateActiveSlice()`) using a similar formatting as `formatDevices()`

### Profiles view
This last view provides the list of available profiles with the different slices, capacity limits and all devices contained inside each slice, all formatted using the `formatProfiles()` fucntion.

At the bottom of the panel is available a button used to launch a new window used for creating a new profile using the `NewProfileWindow` class. This is more explored in the next chapter. 
With the creation of a new window, the primary application transfers full focus to it, thereby directing user attention to the new widget while preventing interference with the main program. This is all done in the `spawnNewProfileWidget()` function, who also connects the `newProfileWindowClosed` event to the `newProfileWindowsClosed()` function, responable of inserting the newly created profile inside the slicer list and emitting the `updateProfiles` signal

## New Profile window
The window presents itself only with the textfield used to capture the profile name, plus two buttons for adding slices and saving the profile. In case the profile is saved without any slices inside, all the changes are ignored and no profile is created in the main application.

When clicking the "add slice" button, a small widget is added to the window using the `NewSliceBox` class. This class builds a `SpinButton` used for keeping track of the minimum bandwidth reserved for the slice, plus a selection of check buttons listing the different devices who can be contained inside the slice
Each time a new slice is created, the program removes previously selected hosts and reduces the maximum value for reserved bandwidth. This behavior blocks the possibility of having the same host on multiple slices, or slices who compete for the same bandwidth. If the maximum amount of reserved bandwidth is reached, or all hosts have been selected, the "add slice" button doesn't perform any action

Upon confirming the customizations using the apropriate button, the window extracts the data from the form, creates a new profile storing it internally, and emits the `newProfileWindowClosed` signal, warning the main window that the new profile is ready to be extracted and the new profile window to be subsequently destroyed