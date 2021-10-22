# Import libraries
import random
from ES2EEPROMUtils import ES2EEPROM
import os
from gpiozero import PWMLED, Button, LED, Buzzer
from time import sleep

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
ALED = None
BTNGUESS = None
BTNINC = None
was_held = False
value = 0
guess = 0
LED1 = None
LED2 = None
LED3 = None
BUZZER = None
EEPROM = None
scores = []
currScore = 0
name = ""

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzerPin = 33

# Print the game banner
def welcome():
    os.system('clear')
    print(" _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game, value
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        end_of_game = False
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    index = 1
    for score in raw_data:
        print("{} - {} took {} guesses".format(index, score[0], score[1]))
        index += 1
    # print out the scores in the required format
    pass


# Setup Pins
def setup():
    global ALED, BTNGUESS, NUMLED, BTNINC, LED1, LED2, LED3, BUZZER, EEPROM, currScore, name

    #set pin types
    if ALED is None:
        ALED = PWMLED("BOARD" +str(LED_accuracy)) # PWM LED on pin 12 v 32
        BTNGUESS = Button("BOARD"+str(btn_submit), hold_time=1, bounce_time=0.1)
        BTNINC = Button("BOARD"+str(btn_increase), bounce_time=0.1)
        LED1 = LED("BOARD"+str(LED_value[0]))
        LED2 = LED("BOARD"+str(LED_value[1]))
        LED3 = LED("BOARD"+str(LED_value[2]))
        BUZZER = Buzzer("BOARD" + str(buzzerPin))
        EEPROM = ES2EEPROM() #create ref object

    BTNINC.when_pressed = increaseNum
    BTNGUESS.when_held = guessHeld
    BTNGUESS.when_released = guessPressed

    currScore = 0 #reset score
    name = "" #reset name

    pass

def guessHeld():
    global was_held, playing
    was_held = True
    end()
    setup()
    menu()

def guessPressed():
    global was_held, playing
    if not was_held:
        guessNum()
    was_held = False

# Load high scores
def fetch_scores():
    global EEPROM
    temp_scores = []

    scores = ES2EEPROM.read_block(EEPROM,0,13) # Get the scores
    score_count = scores[0]
    temp_name = ""

    # convert the codes back to ascii   
    for index in range(1,len(scores)):
        if index%4 == 0:
            temp_scores.append([temp_name, scores[index]])
            temp_name = ""
        else:
            temp_name += chr(scores[index])

    scores = temp_scores

    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    global currScore, EEPROM, name
    s_count, ss = fetch_scores()
    s_count += 1 # add one to score count

    # include new score
    # sort
    # update total amount of scores
    # write new scores

    ss.append([name, currScore])
    ss.sort(key=lambda x: x[1])

    data_to_write = []
    data_to_write.append(s_count)

    for score in ss[0:3]:
        # get the string
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
    ES2EEPROM.write_block(EEPROM, 0, data_to_write)
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def increaseNum():
    global guess, LED1, LED2, LED3
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    if guess>=7:
        guess=0
    else:
        guess+=1

    if guess & 0x01:
        LED1.on()
    else:
        LED1.off()
    
    if guess & 0x02:
        LED2.on()
    else:
        LED2.off()
    
    if guess & 0x04:
        LED3.on()
    else:
        LED3.off()
    pass


# Guess button
def guessNum():
    global guess, value, end_of_game, name, currScore

    if guess != value:
        # if it's close enough, adjust the buzzer
        # Change the PWM LED
        accuracy_leds()
        trigger_buzzer()
        currScore+=1
    else:
        # if it's an exact guess:
        # - Disable LEDs and Buzzer
        # - tell the user and prompt them for a name
        # - fetch all the scores
        # - add the new score
        # - sort the scores
        # - Store the scores back to the EEPROM, being sure to update the score count
        end()
        name = input("Well done you took {} guesses to get it right!\n Enter your name to save your score:\n".format(currScore))
        name = name.upper()

        while not end_of_game:
            if len(name) < 3:
                name = input("Please enter a name 3 characters long:\n")
                name = name.upper()
            else:
                name = name[0:3]
                end_of_game = True
                save_scores()
    pass


# LED Brightness
def accuracy_leds():
    global guess, ALED, value
    tvalue = value
    tguess = guess
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%

    if tvalue == 0:
        tvalue = 1
        tguess = guess + 1

    if tvalue > tguess :
        ALED.value = guess/value
    else:
        per = (tvalue-(tguess - tvalue))/tvalue 
        if per > 1 or per < 0:
            per = 0
        ALED.value = per
    pass

# Sound Buzzer
def trigger_buzzer():
    global BUZZER
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%

    if abs(guess-value) == 3:
        BUZZER.beep(on_time=0.1, off_time=1)
    elif abs(guess-value) == 2:
        BUZZER.beep(on_time=0.1, off_time=0.5)
    elif abs(guess-value) == 1:
        BUZZER.beep(on_time=0.1, off_time=0.25)
    else:
        BUZZER.off()

    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass

def end():
    global BUZZER, LED1, LED2, LED3, ALED
    BUZZER.off()
    LED1.off()
    LED2.off()
    LED3.off()
    ALED.off()

if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
