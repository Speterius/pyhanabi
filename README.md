# PyHanabi
An online game written in python to play the card game Hanabi over voice chat.

 -  **server.py** creates a server to take care of game logic and distribute the game state all clients. 
 The update to the game state is done whenever the server receives an event from one of the players.

- **client.py** creates TCP link between the server and forwards all game state updates to the game GUI. 
The client also sends the game events back to the server.

- **game_window.py** defines the game GUI class using the arcade library. 

- **game_logic.py** module defines the game logic of Hanabi, inside the GameState class.
The server updates the GameState using GameState.update(event).

### Dependencies:

- arcade: the game engine used
- dataclasses: for easy class definitions
- pickle: converting custom classes into pickle for server-client comms
- names: randomizing player names for testing)

### Author:
Peter Seres 

p.seres@student.tudelft.nl

peet.seres@gmail.com
