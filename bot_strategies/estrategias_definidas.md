estrategia A:
    llamando cada linea un stop, 
    si el precio alcanzo un stop a favor,
        1.)repetir operacion limit open, ? close.
        2.)abrir nueva operacion a precio mercado,y colocar orden profit de cerrado con x offset
    
    si el precio alcanzo el primer stop en contra:
        1.)asignar -1 el contador de stops en contra alcanzados
    
    si el precio alcanzo el segundo stop en contra:
        1.)abrir operacion opuesta
        2.)asignar +1 al contador