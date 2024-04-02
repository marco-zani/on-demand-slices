# on-demand-slices
This project is in it's embrio phase. The objective is to create a way enable and disable network slicing in the most autonomous way possible


# To do
## Marco
- [X] multi-processing
  - [X] funzione send() per inviare la configurazione dallo slicer al controller
- [X] creazione file contenente i links
- [X] function to load function
- [X] convert profile into controller configuration
- [ ] passare in conf la percentuale sulla porta

## Francesco
- [X] funzione listNetElements(): elenca tutti i dispositivi e link sulla rete
- [X] listSlicingProfiles(): elenca tutti i profili salvati, e quali dispositivi ne fanno parte
- [X] listActiveProfiles(): mostra la configurazione attuale della rete, con la divisione delle diverse slices
- [X] toggleProfile(): modifica la configurazione attiva rispettando il profilo assegnato (o disattivato)
- [X] function notifyAllSwitch (flush tables)
- [ ] QoS
## Alessio
- [X] createNewProfile(): --> OK
- [X] rendere il controller funzionante
- [ ] Correggi la funzione di getPort
- [ ] Report

  
