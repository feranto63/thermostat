#prima versione del termostato su pi
#flowchart
#ogni 5 minuti leggi la temperatura e lo stato della caldaia
#memorizza i dati sul DB
#grafica lo storico orario
#richiedi in input la temperatura desiderata
Tdes=raw_input("temperatura desiderata = ")
print "Tdes=",Tdes
#se Tdes > Tact then turnon caldaia
#loop
