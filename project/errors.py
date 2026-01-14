class GameError(Exception):
    """Si è verificato un errore nel flusso di gioco."""
    pass

class InvalidEquipError(GameError):
    """Non è stato possibile equipaggiare l'oggetto"""
    pass