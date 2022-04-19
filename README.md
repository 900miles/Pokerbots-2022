# MIT Pokerbots 2022 Engine
MIT Pokerbots engine for 2022 and skeleton bots in Python, Java, and C++. Also contains my own bots written in Python, with the following characteristics:

 - **Adamack**: Most advanced bot. Adapts to opponent's play. Will bluff more if opponent folds too often, call more if opponent bluffs too often, and fold more if opponent bluffs too infrequently.
 - **Exploitive**: An earlier version of Adamack, will attempt to adapt to opponent's tendencies but is far less effective at accurately reading opponents.
 - **Maniac**: Will bet large and often. It was an attempt to gain an edge over early bots in the competition that folded too often, but I had to abandon it once they became more sophisticated.

The command to run the engine is ```python3 engine.py```. The engine is configured via ```config.py```. If on Windows, the engine must be run using the Windows Subsystem for Linux (WSL).

## Dependencies
 - python>=3.5
 - cython (pip install cython)
 - eval7 (pip install eval7)
 - Java>=8 for java_skeleton
 - C++17 for cpp_skeleton
 - boost for cpp_skeleton (`sudo apt install libboost-all-dev`)
 - fmt for cpp_skeleton

## Linting
Use pylint.
