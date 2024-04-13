from SimpleGame.simplegame import *
from random import choice
import sys

BEAT_DIRECTIONS = ['up', 'down', 'left', 'right']
WASD_DIRECTIONS = {'w': 'up', 's': 'down', 'a': 'left', 'd': 'right'}
VISIBLE = 'visible'
SPEED = 5   # DO NOT CHANGE

generation_speed = 0.6
frame_counter = 0
score = 0
timeLeft = 20
topScores = []
highestScore = 0

# hit box coordinates
hitBoxTop = 550
hitBoxBottom = 650

# checks if enough arguments are provided
if len(sys.argv) < 4:
        print("Please print structure like so: python BeatSaber2DStarter <player_name> '<song_choice>' <difficulty_level>")
        sys.exit(1)
    


# the command arguments 
playerName = sys.argv[1]
gameDifficulty = sys.argv[3]
songName = sys.argv[2]
currentBeatIndex = 0

# reads and parse the files
with open (f"{sys.argv[2]}/{sys.argv[3]}.beat") as input_file:
    beatmap = input_file.read()
    parsedBeatmap = beatmap.split()
    stringFrames = parsedBeatmap[4:len(parsedBeatmap):4]
    genFrames = []
    for n in stringFrames:
        genFrames.append(int(n))
    hand = parsedBeatmap[6:len(parsedBeatmap):4]
    direction = parsedBeatmap[7:len(parsedBeatmap):4]

game_ended = False
game_started = False
startScreenElements = {}
playScreenElements = {}
endScreenElements = {}

beatList = []


def start_screen_setup():
    startScreenElements['ready'] = create_element('text-ready', (WIDTH / 2, HEIGHT / 2 - 100))
    startScreenElements['space'] = create_element('space-bar', (WIDTH / 2, HEIGHT / 2 + 50))
    startScreenElements['tap'] = create_element('tap-active', (WIDTH / 2 + 70, HEIGHT / 2 + 50))
    startScreenElements['tap'][VISIBLE] = True
    schedule_callback_every(toggle_tap, .5)

def end_screen_setup():
    global game_ended
    game_ended = True
    endScreenElements['player_score'] = create_element('text-score', (WIDTH / 2, HEIGHT / 2 - 200))
    endScreenElements['player_score'][VISIBLE] = True
    
    
def game_screen_setup():
    global game_started
    game_started = True
    cancel_callback_schedule(toggle_tap)
    playScreenElements['score'] = create_element('star2', (30, 30))
    playScreenElements['keyboard'] = create_element('keyboard_arrows', (WIDTH / 2, HEIGHT - 60))
    playScreenElements['keyboard']['base'] = 'keyboard_arrows_'
    playScreenElements['go'] = create_element('text-go', (WIDTH / 2, HEIGHT / 2))
    playScreenElements['go'][VISIBLE] = True
    schedule_callback_after(hide_go, .5)
        


def hide_go():
    playScreenElements['go'][VISIBLE] = False

def toggle_tap():
    startScreenElements['tap'][VISIBLE] = not startScreenElements['tap'][VISIBLE]



def draw():
    """
    - Called automatically everytime there's a change in the screen
    - Do not include any operations other than drawing inside this function.
    - The only allowed statements/functions are the ones that have draw_ in the name like
    draw_background_image(), draw_element(), etc
    """
    global flag, score
    # You may set different background for each step!
    draw_background('background4')

    if not game_started:
        # What you want to show *before* the game starts goes here. eg 'Press Space to Start!'
        for gameElement in startScreenElements.values():
            if VISIBLE not in gameElement or gameElement[VISIBLE]:
                draw_element(gameElement)
    elif game_ended:
        # What you want to show *after* the game ends goes here. eg 'You Scored x Beats!'
        for gameElement in endScreenElements.values():
            if VISIBLE not in gameElement or gameElement[VISIBLE]:
                draw_element(gameElement)
        
        # Draw top scores
        top_scores = read_top_scores()
        y_position = 230  
        count = 1
        for name, highestScore in top_scores:
            draw_text_on_screen(f"{count}. {name}: {highestScore}", (WIDTH / 2, y_position))
            y_position += 30 
            count += 1
                
    else:
        # What you want to show *during* the game goes here. e.g. beats, timer, etc
        draw_text_on_screen(f'{score}', (70, 32), color='yellow', fontsize=40)
        
        for gameElement in playScreenElements.values():
            if VISIBLE not in gameElement or gameElement[VISIBLE]:
                draw_element(gameElement)

        for beat in beatList:
            draw_element(beat)



def update():
    """
    - Called automatically 60 times per second (every 1/60th of a second) to
    maintain a smooth frame rate of 60 fps.
    - Ideal for game logic e.g. moving objects, updating score, and checking game conditions.
    """
    # The frame counter keeps track of which frame we're on, this can be helpful for
    # operations that are time sensitive. You may also use the callback functions instead of
    # using the frame_counter.

    global frame_counter, game_ended, score, highestScore
    frame_counter += 1
    generate_beat()
    # Uncomment the following line and see what happens when you run the program
    # print(f'{frame_counter/60:.1f}')
    


    if not game_started:
        # Game logic if any *before* the game starts.
        pass

    elif game_ended:
        # Game logic if any *after* the game ends.
        pass
    else:
        # Game logic if any *during* the game.
        # move it 5 pixels down
        if manage_background_music(songName, 'is-playing') == False:
            end_game()
            return
        for beat in beatList:
            if beat['moving']:
                move_by_offset(beat, (0, SPEED))
                if get_position(beat, 'bottom') >= HEIGHT:
                    beat['moving'] = False
                    beat['scoreStatus'] = 'miss'
            elif beat['scoreStatus']:
                if beat['scoreStatus'] == 'hit':
                    score += 2
                    highestScore += 2
                if beat['scoreStatus'] == 'miss':
                    score -= 1
                score_beat(beat)
        # checks if the score reaches -1 and end the game
        if score == -1:
            end_game()
        

def on_key_down(key):
    """
    Called when a key is pressed on the keyboard.
    - Do not use this function for game logic.

    Parameters:
    - key: An integer representative of the key that was pressed.
    In order to get a str value of the key pressed, use get_key() instead.
    """

    key_pressed = get_key_pressed(key)
    if key_pressed == 'space' and not game_started:
        start_game()
        return



    lowest_beat = findRightLowestBeat()
    if not game_ended and lowest_beat and key_pressed in BEAT_DIRECTIONS and findRightLowestBeat()['side'] == 1:
        beat_bottom = get_position(lowest_beat, 'bottom')
        lowest_beat['moving'] = False
        change_image(playScreenElements['keyboard'], playScreenElements['keyboard']['base'] + lowest_beat['direction'])
        schedule_callback_after(keyboardArrowChangeBack, .1)
        if hitBoxTop <= beat_bottom <= hitBoxBottom and lowest_beat['direction'] == key_pressed:
            lowest_beat['scoreStatus'] = 'hit'
        else:
            lowest_beat['scoreStatus'] = 'miss'
    
    lowest_beat = findLeftLowestBeat()
    if not game_ended and lowest_beat and key_pressed in WASD_DIRECTIONS and findLeftLowestBeat()['side'] == -1:
        beat_bottom = get_position(lowest_beat, 'bottom')
        lowest_beat['moving'] = False
        direction = WASD_DIRECTIONS[key_pressed]
        change_image(playScreenElements['keyboard'], playScreenElements['keyboard']['base'] + lowest_beat['direction'])
        schedule_callback_after(keyboardArrowChangeBack, .1)
        if hitBoxTop <= beat_bottom <= hitBoxBottom and lowest_beat['direction'] == direction:
            lowest_beat['scoreStatus'] = 'hit' 
        else:
            lowest_beat['scoreStatus'] = 'miss'


def keyboardArrowChangeBack():
    change_image(playScreenElements['keyboard'], playScreenElements['keyboard']['base'][:-1])


def score_beat(beat):
    status = beat['scoreStatus']
    beat['scoreStatus'] = ''
    direction = beat['direction']
    change_image(beat, direction + '-' + status)
    schedule_callback_after(remove_lowest_beat, .2)


def remove_lowest_beat():
    if beatList:
        beatList.pop(0)


def findRightLowestBeat():
    for beat in beatList:
        if beat['moving'] and beat['side'] == 1:
            return beat
    return None

def findLeftLowestBeat():
    for beat in beatList:
        if beat['moving'] and beat['side'] == -1:
            return beat
    return None


def start_game():
    # user-defined function
    # only put logic that'll happen once when the game starts
    game_screen_setup()
    manage_background_music(songName, 'play-once')
    manage_background_music(songName, 'change-volume', volume=0.3)
    schedule_callback_every(generate_beat, generation_speed)


# Reads the top10 file and parsing the information
def read_top_scores():
    try:
        with open("top10.csv", "r") as file:
            topScores = [line.strip().split(",") for line in file]
            topScores = [(name, int(score)) for name, score in topScores]
            return topScores
    except FileNotFoundError:
        return []

# extracts the score 
def get_score(entry):
    return entry[1]

# determines score placement
def update_top_scores(player_name, highestScore):
    top_scores = read_top_scores()

    # Add the player's score to the list if it's among the top 10 or if there are less than 10 scores
    if len(top_scores) < 10:
        top_scores.append((player_name, highestScore))
    else:
        # Replace the lowest score if the player's score is higher
        min_score = min(top_scores, key=get_score)[1]
        if highestScore > min_score:
            # Check if the player's name and score are already in the list
            player_entry = (player_name, min_score)
            if player_entry in top_scores:
                min_index = top_scores.index(player_entry)
                top_scores[min_index] = (player_name, highestScore)
            else:
                # Add the player's score if it's not already in the list
                top_scores.append((player_name, highestScore))

    # Sort the list in descending order based on score
    top_scores.sort(key=get_score, reverse=True)

    # Write the updated top scores to the file
    write_top_scores(top_scores)
    return top_scores

# a function that writes the top scores
def write_top_scores(topScores):
     with open("top10.csv", "w") as file:
        for name, score in topScores:
            file.write(f"{name},{score}\n")

def end_game():
    # user-defined function
    global game_ended, score, highestScore
    game_ended = True
    # Update the highest score achieved during the game
    highestScore = max(score,highestScore) #found on this website https://www.geeksforgeeks.org/python-max-function/ 
    cancel_callback_schedule(generate_beat)
    end_screen_setup()
    beatList.clear()
    manage_background_music(songName, 'stop')
    # Update the top scores with the player's name and the highest score achieved
    update_top_scores(playerName, highestScore)


def generate_beat():
    # user-defined function
    global currentBeatIndex, frame_counter,game_started
    if game_started and not game_ended:
        if currentBeatIndex < len(genFrames):
            if frame_counter >= genFrames[currentBeatIndex]:
                beatHand = hand[currentBeatIndex].lower() # this tracks the "hands" part of the file 
                beatSide = -1 if beatHand == 'left' else 1 # makes sure to put the beats on the correct sides based on the hands!
                beatDifficultlyDirection = direction[currentBeatIndex].lower() # based on the difficulty the arrows will be put in certain directions given
                beat = create_element(beatDifficultlyDirection + '-beat', centerPos=(WIDTH / 2 + beatSide*150, 0))
                beat['side'] = beatSide
                beat['moving'] = True
                beat['scoreStatus'] = ''
                beat['direction'] = beatDifficultlyDirection
                beatList.append(beat)
                currentBeatIndex += 1



# # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # DO NOT REMOVE THIS LINE!! # # # # # # # #
start_screen_setup()
run_game()
# # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # #
