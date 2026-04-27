from src.game_broker import GameBroker

def main():
    print("[INFO] Starting Agro-Defender Engine...")
    
    # Initialize the main game engine
    game = GameBroker()
    
    # Start the blocking game loop
    game.run()

# ¡ESTA PARTE ES CRÍTICA! Sin esto, el juego no arranca.
if __name__ == "__main__":
    main()
