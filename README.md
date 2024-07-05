# BD-project

> Rif. per i controlli sugli attributi: https://docs.sqlalchemy.org/en/20/orm/mapped_attributes.html\
> Materiale prof SQLAlchemy Core: https://colab.research.google.com/drive/1D59IbeExQL4AQihpcKMQ4yBQZabfwZO9?usp=sharing#scrollTo=6QYybaiNSD0m\
> Materiale prof SQLAlchemy ORM: https://colab.research.google.com/drive/1nHd7iFKzTvvNsnYCbPHcWQVSrcgU_36T?usp=sharing

## Todo

### Front-end
- [ ] Creare sezione venditore con ordini inviati e annunci creati (navigazione con tab)
- [ ] Notifiche per stato ordini
    - [ ] Creare sezione notifiche
    - [ ] Creare template per notifiche toast (?)
- [ ] Se stato ordine completato, rendere possibile inserimento recensione

### Back-end
- [ ] Fare autenticazione login, e migliorare registrazione (non ci sono controlli)
- [ ] Migliorare controlli sugli attributi tabelle
- [ ] Sessione per utente (per ora c'è solo dopo register e solamente perché dopo viene subito usata nella /sell)
- [ ] Fare generazione id prodotti (ora è randomica)
- [ ] Gestire utenti venditori e non venditori (mettere controlli alla registrazione)
- [x] Sistemare le relationship (non funzionano le join)
