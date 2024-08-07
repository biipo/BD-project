# BD-project

> Rif. per i controlli sugli attributi: https://docs.sqlalchemy.org/en/20/orm/mapped_attributes.html \
> Materiale prof SQLAlchemy Core: https://colab.research.google.com/drive/1D59IbeExQL4AQihpcKMQ4yBQZabfwZO9?usp=sharing#scrollTo=6QYybaiNSD0m \
> Materiale prof SQLAlchemy ORM: https://colab.research.google.com/drive/1nHd7iFKzTvvNsnYCbPHcWQVSrcgU_36T?usp=sharing \
> Documentazione matcha.css: https://matcha.mizu.sh/

### Dubbi 

- In teoria gli utenti venditori, leggendo dal pdf, possono solamente vendere; quindi togliamo la possiblità che possano fare ordini??
- Se un prodotto termina la sua disponibilità lo eliminamo dal DB o lo impostiamo tipo a -1 e lo mostriamo come 'Esaurito'?\
    Ee magari, non so, possiamo fare che il venditore può riaumentare le quantità e rimetterlo disponibile\
    Per ora i prodotti ho messo che vengono eliminati dal DB
- Possibilità di modificare le recensioni??

## Todo

### Front-end
- [ ] Notifiche per stato ordini
    - [x] Creare sezione notifiche
- [ ] Se stato ordine completato, rendere possibile inserimento recensione
- [x] Pagina profilo (`profile.html`)
    - [x] Form modifica dati personali
    - [x] Form aggiunta indirizzi
    - [ ] Link a pagina recensioni fatte (ricevute se venditore)
        - [ ] Per utenti venditori aggiungere ref alla pagina profilo utente che ha fatto la recensione
    - [ ] Statistiche venditore (se venditore)
- [ ] Pagina profilo altrui (`user.html`)
- [x] Zoom in (`zoom_in.html`)
    - [ ] Fixare nuovo layout (è ancora bruttino)
    - [ ] Migliorare visualizzazione tag
- [ ] Pagina home (`home.html`)
    - [x] Cambiare css
- [ ] Carrello
    - [x] Migliorare visualizzazione carrello
    - [ ] Modificare eliminazione prodotti dal carrello per una certa quantità (es. se un prodotto sono 5 elementi di poterne togliere 2)
- [ ] Migliorare pagina recensioni sul profilo, dove vedi le recensioni fatte/ricevute

### Back-end
- [ ] Migliorare controlli sugli attributi tabelle
- [ ] Ricerca prodotti dalla barra di ricerca

## Fatti

### Front-end
- [x] Aggiungere filtri
- [x] Pagina vendita (`sell.html`)
- [x] Template navbar (`nav.html`)
    - [x] Indicare pagina selezionata
- [x] Passare a template jinja per bene (extends, block, ecc.)
- [x] Aggiungere form con metodo di pagamento all'ordine
- [x] Aggiungere form recensioni visibile se ordinato e confermato ricevuto

### Back-end
- [x] Aggiungere controllo sulla route `'/sell'` per utenti NON venditori
- [x] Fare pagina `'/home'`
- [x] Fixare registrazione
- [x] Fixare aggiunta di un prodotto al carrello quando questo è già presente (sommiamo le quantità e non deve superare disponibilità prodotto)
        (controllo disponibilità al momento della creazione dell'ordine o all'aggiunta al carrello?? Caso in cui abbiamo più utenti che fanno l'acquisto)
- [x] Il carello quando aggiungi qualcosa mostra l'ultimo oggetto 2 volte, ma se aggiorni la pagina lo mostra correttamente (Da sistemare :/)
- [x] Applicare cambiamenti alla struttura della tabella addresses (non capisco come farlo)
- [x] Implementare parte avvio ordine
- [x] Aggiungere booleano `confirmed` alla tabella ordini per confermare ordine quando `state` settato a ricevuto da venditore