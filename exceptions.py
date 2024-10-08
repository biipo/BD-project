
# Credenziali invalide durante la creazione di un utente
class InvalidCredential(Exception):
    def __init__(self, message: str):
        self.message = str(message)
        super().__init__(self.message)
    
    def __repr__(self):
        return message

# Dati mancanti passati ai costruttori
class MissingData(Exception):
    def __init__(self, message: str):
        self.message = str(message)
        super().__init__(self.message)
    
    def __repr__(self):
        return message

# Quantità dell'ordine invalide
class InvalidOrder(Exception):
    def __init__(self, message: str):
        self.message = str(message)
        super().__init__(self.message)
    
    def __repr__(self):
        return message