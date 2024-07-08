
"""
Eccezione usata per controllare le credenziali alla CREAZIONE
di un nuovo utente
"""
class InvalidCredential(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    
    def __repr__():
        return message