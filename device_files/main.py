import time

while True:
    # Continuously run the game
    try:
        execfile("pacman/game.py")
    except SystemExit:
        pass	# Don't exit the main program if game.py exits early

    time.sleep(2)
