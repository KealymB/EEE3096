# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game
guess = 0
ALED = None
BUZZER = None
value = 0


# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
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
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        print(value)
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
    # print out the scores in the required format
    pass


# Setup Pins
def setup():
    global ALED, BUZZER
    GPIO.setmode(GPIO.BOARD)# Setup board mode

    # SETUP Buttons
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

    # Setup regular GPIO
    GPIO.setup(buzzer, GPIO.OUT)

    #create PWM instance with frequency
    if BUZZER is None:
        BUZZER = GPIO.PWM(buzzer, 1000)		

    ALED = PWMLED(12)	## sets GPIO12 V 32 as PWM LED

    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=500)  # add rising edge detection on a button increase
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=500)  # add rising edge detection on a button submit

    for LEDPIN in LED_value :   #sets LED as output
        GPIO.setup(LEDPIN, GPIO.OUT)
        GPIO.output(LEDPIN, GPIO.LOW)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = None
    # Get the scores
    
    # convert the codes back to ascii
    
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    global guess
    # Increase the value shown on the LEDs
    if guess>=7:
        guess=1
    else:
        guess+=1
    print(guess)
    GPIO.output(LED_value[0], guess & 0x01)
    GPIO.output(LED_value[1], guess & 0x02)
    GPIO.output(LED_value[2], guess & 0x04)
    pass


# Guess button
def btn_guess_pressed(channel):
    global guess, value
    start = time.time()
    backed = False

    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    while GPIO.input(btn_submit) == GPIO.LOW:
        time.sleep(0.01)
        length = time.time() - start

        if length > 1:
            print("BACK")
            GPIO.cleanup()
            setup() # fix no debounce thing...
            menu()
            backed = True
            break
            
    # Compare the actual value with the user value displayed on the LEDs
    print(guess)
    print(value)
    if guess != value and not backed:
        # if it's close enough, adjust the buzzer
        # Change the PWM LED
        accuracy_leds()
        trigger_buzzer()
    elif guess == value and not backed:
        # if it's an exact guess:
        # - Disable LEDs and Buzzer
        # - tell the user and prompt them for a name
        # - fetch all the scores
        # - add the new score
        # - sort the scores
        # - Store the scores back to the EEPROM, being sure to update the score count
        GPIO.cleanup() 
        name = input("YOURE AMAZING, enter your name:\n")
        name = name.upper()
        if len(name) > 3:
            name = name[0:3]
        print(name)
    pass


# LED Brightness
def accuracy_leds():
    global guess, ALED, value
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    print((value - guess))
    if (value - guess) < 0 :
        ALED.value = guess/value*100
    else:
        ALED.value = 100-value/guess*100+100
    pass

# Sound Buzzer
def trigger_buzzer():
    global guess, BUZZER, value
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%

    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second

    if abs(guess-value) == 3:
        BUZZER.ChangeFrequency(1)
        BUZZER.start(50)
        #elif abs(guess-value) == 2:
        #elif abs(guess-value) == 1:
    pass


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
    finally:
        GPIO.cleanup()
