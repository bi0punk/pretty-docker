from textual.app import App
from textual.widgets import Card, Container, Static

class ThreeCardsApp(App):
    async def on_mount(self):
        # Crear tarjetas con contenido
        card1 = Card("Tarjeta 1", body=Static("Contenido de la tarjeta 1"))
        card2 = Card("Tarjeta 2", body=Static("Contenido de la tarjeta 2"))
        card3 = Card("Tarjeta 3", body=Static("Contenido de la tarjeta 3"))

        # Crear un contenedor para las tarjetas
        container = Container(card1, card2, card3)
        await self.view.dock(container)

if __name__ == "__main__":
    ThreeCardsApp.run()
