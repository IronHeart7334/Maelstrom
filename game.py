from output import Op
from file import File, PlayerSaveFile
from teams import PlayerTeam, AbstractTeam
from character import AbstractCharacter
from utilities import choose, ELEMENTS
import json

class Game:
    """
    The Game class is used to store data on the game the user is currently playing,
    so this way, there don't have to be any globals.
    """
    def __init__(self):
        self.player = None
        self.exit = False
        #gameType (Maelstrom, or other rpg)
    
    def run(self):
        """
        Begins the program
        """
        while not self.exit:
            if self.player == None:
                self.main_menu()
            else:
                print("Player login works. My work here is done.")
                self.exit = True
    
    def main_menu(self):
        """
        Displayes the main menu
        """
        Op.add("MAELSTROM")
        Op.display()
        action = choose("Choose an option: ", ["Play", "About", "Quit"])
        if action == "Play":
            self.login_menu()
        elif action == "Quit":
            self.exit = True
    
    def login_menu(self):
        """
        Asks the user to log in
        """
        users = File("users/users.txt").get_lines()
        
        options = users.copy()
        options.append("None of these")
        
        user_name = " "
        
        action = choose("Do you wish to load a game, or start a new one?", ["Create game", "Load game"])
        if action == "Load game":
            user_name = choose("Which user are you?", options)
            if user_name == 'None of these':
                self.new_user_menu()
                self.login_menu()
            else:
                self.login_user(user_name)
        else:
            self.new_user_menu()
            self.login_menu()
        
    
    def login_user(self, user_name):
        """
        Play a game as the given user
        """
        data = PlayerSaveFile("users/" + user_name.replace(" ", "_").lower() + ".txt")
        
        self.player = AbstractTeam.load_team('users/' + user_name.replace(" ", "_").lower() + '.json')
        self.player.initialize()
        self.player.display_data()
            
    
    def new_user_menu(self):
        """
        Creates the menu for creating a new user
        """
        name = input('What do you want your character\'s name to be? ')
        element = choose('Each character has elemental powers, what element do you want yours to control?', ELEMENTS)
        print(self.create_user(name, element))
        self.login_user(name)
        
                
    def create_user(self, user_name: str, element: str) -> str:
        """
        Adds a user.
        Returns a message based on if the profile creation was successful
        """
        ret = 'User added successfully!'
        success = True
        
        with open('users/users.txt', 'rt') as file:
            if user_name in file.read():
                ret = 'The name ' + user_name + ' is already taken.'
                success = False
                
        
        if success:
            character = AbstractCharacter.create_default_player()
            character.name = user_name
            character.set_element(element)
            PlayerTeam(user_name, character).save()
            
            with open('users/users.txt', 'a') as file:
                file.write(user_name + '\n')
            
        return ret