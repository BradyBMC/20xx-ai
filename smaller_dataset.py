import melee
import pickle
import os
import numpy as np

#----------------------------------------------------------------------------

'''
Returns port of specific character and -1 if not found
Skip checking for specific port
'''
def has_character(
                    console: melee.Console,
                    character: melee.Character,
                    skip: int=-1
) -> int:

    gamestate = console.step()
    if gamestate is None:
        return False
    for i in range(1,3):
        if character == gamestate.players[i].character and i != skip:
            return i
    return -1

#----------------------------------------------------------------------------

'''
Copies ingame character data and returns as list
May need to restructure how data is saved
'''
def gamedata(player: melee.GameState.players) -> list:
    position = [player.position.x, player.position.y]
    return position

#----------------------------------------------------------------------------

def interpret_stick(pos) -> list():
    # Neutral, Up, Left, Down, Right
    x, y = pos
    if x == 0.5 and y == 0.5:
        return [0, 0, 0, 0]
    elif x >= 0.6:
        return [1, 0, 0, 0]
    elif x <= 0.4:
        return [0, 1, 0, 0]
    elif y >= 0.6:
        return [0, 0, 1, 0]
    elif y <= 0.4:
        return [0, 0, 0, 1]

#----------------------------------------------------------------------------

'''
Process game data and controller inputs from slp -> pkl
Returns 0 if it DOESN'T work and 1 if it does
'''
def convert_dataset(
                    agent: melee.Character=melee.Character.CPTFALCON,
                    adversary: melee.Character=melee.Character.FOX,
                    match: bool=True,
                    train_path: str='Game_20220727T191324.slp',
                    pkl_path: str='smaller_pdata',
                    count: int=None
) -> None:

    # assert train_path is not None
    # assert pkl_path is not None
    
    console = melee.Console(is_dolphin=False, path=train_path)
    console.connect()

    if match is True:
        agent_port = has_character(console, agent)
        adversary_port = has_character(console, adversary, agent_port)
        if agent_port == -1 or adversary_port == -1:
            print('ERROR character not found in slp file')
            return 0

    # Need to change how name will be generated
    f = open(pkl_path + '/data' + str(count) + '.pkl', 'wb')
    # f = open('data.pkl', 'wb')

    data = []
    while True:
        gamestate = console.step()
        # step() returns None when the file ends
        if gamestate is None:
            break

        # Each frame has game data and controller data
        frame = []

        # Visible game data for 1 frame
        agent_data = gamedata(gamestate.players[agent_port])
        adversary_data = gamedata(gamestate.players[adversary_port])
        frame.append([agent_data[0], agent_data[1],
                      adversary_data[0], adversary_data[1]])

        # All controller data for 1 frame
        controller = gamestate.players[agent_port].controller_state
        
        count = 0
        pressed = []
        for button in controller.button:
            count += 1
            if controller.button[button] is True:
                pressed.append(float(1))
            else:
                pressed.append(float(0))
            if count == 7:
                break
        # Missing L/R half press for light shield. Dpad missing bc Luigi and Samus = Cringe

        control_stick = [float(round(controller.main_stick[0], 1)), float(round(controller.main_stick[1], 1))]
        c_stick = [float(round(controller.c_stick[0], 1)), float(round(controller.c_stick[1], 1))]
        inputs = interpret_stick(control_stick) + interpret_stick(c_stick) + pressed

        frame.append(inputs)

        data.append(frame)

    pickle.dump(data, f)
    f.close()
    
    return 1

#----------------------------------------------------------------------------

if __name__ == '__main__':
    # convert_dataset()
    
    directory = os.fsencode('training_set0001')
    pkl_path = 'smaller_pdata'
    i = 0
    for file in os.listdir(directory):
        filename = 'training_set0001/' + os.fsdecode(file)
        assert filename.endswith('.slp'), 'Contains non .slp files: ' + filename
        res = convert_dataset(train_path=filename, pkl_path=pkl_path, count=i)
        i += res