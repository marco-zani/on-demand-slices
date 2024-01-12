# on-demand-slices
This project is in it's embrio phase. The objective is to create a way enable and disable network slicing in the most autonomous way possible


# To do
## Marco
- [ ] multi-processing
  - [ ] funzione send() per inviare la configurazione dallo slicer al controller
- [X] creazione file contenente i links

## Francesco
- [ ] funzione listNetElements(): elenca tutti i dispositivi e link sulla rete
- [ ] listSlicingProfiles(): elenca tutti i profili salvati, e quali dispositivi ne fanno parte
- [ ] listActiveProfiles(): mostra la configurazione attuale della rete, con la divisione delle diverse slices
- [ ] toggleProfile(): modifica la configurazione attiva rispettando il profilo assegnato (o disattivato)
## Alessio
- [ ] createNewProfile(): --> OK
  - [ ] convert profile into controller configuration
