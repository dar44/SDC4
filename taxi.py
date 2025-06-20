#############################################################
#                        CLASE TAXI                         #
#############################################################
class Taxi:
    def __init__(self, id, estado, posicionX, posicionY, destino,  destinoX, destinoY, ocupado, clienteX, clienteY,clienteId, base):
        self.id = id
        self.estado = estado
        self.posicionX = posicionX
        self.posicionY = posicionY
        self.destino = destino
        self.destinoX = destinoX
        self.destinoY = destinoY
        self.ocupado = ocupado
        self.clienteX = clienteX
        self.clienteY = clienteY
        self.clienteId = clienteId
        self.base = base
        
    def getId(self):
        return self.id
    
    def getEstado(self):
        return self.estado

    def getPos(self):
        return self.pos

    def getOcupado(self):
        return self.ocupado
    
    def imprimir(self):
        return f"{self.id}, {self.estado}"
    
    def actualizar_destino(self, nuevo_destino):
        self.destino = nuevo_destino
    
    def getColor(self):
        if self.estado == "ok":
            return "green"
        else:
            return "red"
    def __str__(self):
        return f"Taxi(id={self.id}, estado={self.estado}, posicionX={self.posicionX}, posicionY={self.posicionY}, destino={self.destino}, destinoX={self.destinoX}, destinoY={self.destinoY}, ocupado={self.ocupado}, clienteX={self.clienteX}, clienteY={self.clienteY}, clienteId={self.clienteId}, base={self.base})"        
    
    def imprimirTaxi(self):
        return f"{self.id}:{self.estado}:{self.posicionX}:{self.posicionY}:{self.destino}:{self.destinoX}:{self.destinoY}:{self.ocupado}:{self.clienteX}:{self.clienteY}:{self.clienteId}:{self.base}"        
    
    def to_dict(self):
        return {
            "id": self.id,
            "estado": self.estado,
            "posicionX": self.posicionX,
            "posicionY": self.posicionY,
            "destino": self.destino,
            "destinoX": self.destinoX,
            "destinoY": self.destinoY,
            "ocupado": self.ocupado,
            "clienteX": self.clienteX,
            "clienteY": self.clienteY,
            "clienteId": self.clienteId,
            "base":self.base
        }
    
    
    """KO siempre rojo,
    OK es verde si está en movimiento pero OK puede ser rojo si esta parado porque no tiene cliente(destino)"""