# BD-project

> Rif. per i controlli sugli attributi: https://docs.sqlalchemy.org/en/20/orm/mapped_attributes.html \
> Materiale prof SQLAlchemy Core: https://colab.research.google.com/drive/1D59IbeExQL4AQihpcKMQ4yBQZabfwZO9?usp=sharing#scrollTo=6QYybaiNSD0m \
> Materiale prof SQLAlchemy ORM: https://colab.research.google.com/drive/1nHd7iFKzTvvNsnYCbPHcWQVSrcgU_36T?usp=sharing \
> Documentazione matcha.css: https://matcha.mizu.sh/
## Todo

### Front-end
- [ ] Notifiche per stato ordini
    - [x] Creare sezione notifiche
- [ ] Se stato ordine completato, rendere possibile inserimento recensione
- [x] Pagina profilo (`profile.html`)
    - [x] Form modifica dati personali
    - [x] Form aggiunta indirizzi
    - [ ] Link a pagina recensioni fatte (ricevute se venditore)
    - [ ] Statistiche venditore (se venditore)
- [ ] Pagina profilo altrui (`user.html`)
- [x] Pagina vendita (`sell.html`)
- [ ] Zoom in (`zoom_in.html`)
    - [ ] Fixare nuovo layout (è ancora bruttino)
- [ ] Pagina home (`home.html`)
    - [x] Cambiare css
    - [ ] Aggiungere filtri
- [x] Template navbar (`nav.html`)
    - [x] Indicare pagina selezionata
- [x] Passare a template jinja per bene (extends, block, ecc.)
- [x] Migliorare visualizzazione carrello
- [ ] Aggiungere form con metodo di pagamento all'ordine
- [ ] Aggiungere form recensioni visibile se ordinato e confermato ricevuto

### Back-end
- [ ] Migliorare controlli sugli attributi tabelle
- [ ] Aggiungere controllo sulla route `'/sell'` per utenti NON venditori
- [x] Fare pagina `'/home'`
- [x] Fixare registrazione
- [ ] Applicare cambiamenti alla struttura della tabella addresses (non capisco come farlo)
- [x] Fixare aggiunta di un prodotto al carrello quando questo è già presente (sommiamo le quantità e non deve superare disponibilità prodotto)
        (controllo disponibilità al momento della creazione dell'ordine o all'aggiunta al carrello?? Caso in cui abbiamo più utenti che fanno l'acquisto)
- [x] Il carello quando aggiungi qualcosa mostra l'ultimo oggetto 2 volte, ma se aggiorni la pagina lo mostra correttamente (Da sistemare :/)
- [x] Applicare cambiamenti alla struttura della tabella addresses (non capisco come farlo)
- [x] Implementare parte avvio ordine
- [ ] Aggiungere booleano `confirmed` alla tabella ordini per confermare ordine quando `state` settato a ricevuto da venditore
