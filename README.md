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
- [ ] Pagina profilo (`profile.html`)
    - [ ] Form modifica dati personali
    - [ ] Form aggiunta indirizzi
    - [ ] Link a pagina recensioni fatte (ricevute se venditore)
    - [ ] Statistiche venditore (se venditore)
- [ ] Pagina profilo altrui (`user.html`)
- [ ] Pagina vendita (`sell.html`)
- [ ] Zoom in (`zoom_in.html`)
    - [ ] Fixare nuovo layout (è ancora bruttino)
- [ ] Pagina home (`home.html`)
    - [x] Cambiare css
- [ ] Template navbar (`nav.html`)
    - [ ] Indicare pagina selezionata
- [x] Passare a template jinja per bene (extends, block, ecc.)


### Back-end
- [ ] Migliorare controlli sugli attributi tabelle
- [x] Fare generazione id prodotti (ora è randomica)
- [ ] Aggiungere controllo sulla route `'/sell'` per utenti NON venditori
- [x] Fare pagina `'/home'`
- [x] Fixare registrazione
- [ ] Applicare cambiamenti alla struttura della tabella addresses (non capisco come farlo)
##### Cart
- [ ] Fixare aggiunta di un prodotto al carrello quando questo è già presente (sommiamo le quantità)
