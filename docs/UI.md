# Back end


# UI components
Found inside the `slicer_UI.py` file, the class `Visualizer` is responsable for presenting the application window after calling the class `SlicerWindow` which is responsable to build the UI, while also initializing the `Slicer`, importing the topology from `mininet` and sending the list of devices in the net to the `controller`.It also manages the event `updateProfiles`

The user interface offers three views: network, profiles and active slices, interchangeable like a carousel using the related buttons. This allowes the application to maintain a coherent look and behavior. Each view is loaded individually and incapsulated inside a wrapper using `SlicerWindow.buildWrapper()` which accepts the function used to build the spicific view. This wrapper has been implemented allways with look coherency as the objective.
## Applications views
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
The widnow presents itself only with the textfield used to capture the profile name, plus two buttons for adding slices and saving the profile. In case the profile is saved without any slices inside, all the changes are ignored and no profile is created in the main application.

When clicking the "add slice" button, a small widget is added to the window using the `NewSliceBox` class. This class builds a `SpinButton` used for keeping track of the minimum bandwidth reserved for the slice, plus a selection of check buttons listing the different devices who can be contained inside the slice
Each time a new slice is created, the program removes previously selected hosts and reduces the maximum value for reserved bandwidth. This behavior blocks the possibility of having the same host on multiple slices, or slices who compete for the same bandwidth. If the maximum amount of reserved bandwidth is reached, or all hosts have been selected, the "add slice" button doesn't perform any action

Upon confirming the customizations using the apropriate button, the window extracts the data from the form, creates a new profile storing it internally, and emits the `newProfileWindowClosed` signal, warning the main window that the new profile is ready to be extracted and the new profile window to be subsequently destroyed