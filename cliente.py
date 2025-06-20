#############################################################
#                     CLASE CLIENTE                         #
#############################################################
class Cliente:
    def __init__(self, id, destino, posX=None, posY=None, estado=None):
        self.id = id
        self.destino = destino
        self.posX = posX
        self.posY = posY
        self.estado = estado
        self.color ="yellow"

    def getColor(self):
        return "yellow"
    
    def __str__(self):
        return f"Cliente={self.id}, destino={self.destino}, posX={self.posX}, posY={self.posY}, estado={self.estado}"
    
    def imprimirCliente(self):
        return f"{self.id}:{self.destino}:{self.posX}:{self.posY}:{self.estado}"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {
            "id": self.id,
            "destino": self.destino,
            "posX": self.posX,
            "posY": self.posY,
            "estado": self.estado,
            "color": self.color
        }

    