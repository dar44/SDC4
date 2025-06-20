#############################################################
#                     CLASE DESTINO                         #
#############################################################
class Destino:
    def __init__(self, id, posX, posY):
        self.id=id
        self.posX=posX
        self.posY=posY
        self.color = "light blue"

    def getColor(self):
        return self.color

    def __str__(self):
        return f"Destino(id={self.id}, posX={self.posX}, posY={self.posY}), color={self.color}"

    def to_dict(self):
        return {
            "id": self.id,
            "posX": self.posX,
            "posY": self.posY,
            "color": self.color
        }