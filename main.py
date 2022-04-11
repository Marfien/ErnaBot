import json
import os

import dotenv

from interactions import Client, CommandContext, Intents, Option, OptionType
from typing import Dict, List


class Character:

    def __init__(self, owner: int, name: str, full_name: str = None, inventory: Dict[str, float] = None, backstory: str = None, stats=None):
        if stats is None: stats = dict()
        if inventory is None: inventory = dict()
        if backstory is None: backstory = f'Blob! A wild {name} has appeared.'
        if full_name is None: full_name = name

        self.owner = owner
        self.name = name
        self.full_name = full_name
        self.inventory: [str, float] = inventory
        self.stats = stats
        self.backstory = backstory

    def add_item_to_inventory(self, item: str, amount: float = 1.0):
        new_amount: float
        if item in self.inventory:
            current_amount = self.inventory[item]
            new_amount = current_amount + amount
        else:
            new_amount = amount

        if new_amount > 0.0:
            self.inventory[item] = new_amount
        else:
            self.inventory.pop(item)

    def cleanup_inventory(self):
        for item, amount in self.inventory.items():
            if amount > 0.0: continue
            self.inventory.pop(item)

    def cleanup_item(self, item: str, amount: float = None):
        if amount is None: amount = self.inventory[item]

        if amount <= 0.0: self.inventory.pop(item)

    def remove_item_from_inventory(self, item: str):
        self.inventory.pop(item)

    def set_item_amount(self, item: str, amount: float):
        self.inventory[item] = amount


def load_characters(file: str) -> List[Character]:
    characters: List[Character] = list()
    with open(file, 'r') as f:
        character_list = f.read()
        character_list = json.loads(character_list)['characters']

        for character in character_list:
            characters.append(Character(
                owner=character['owner'],
                name=character['name'],
                full_name=character['full_name'],
                inventory=character['inventory'],
                backstory=character['backstory'],
                stats=character['stats']
            ))

    return characters


# load environment variables
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# characters
CHARACTERS_BY_NAME: Dict[str, Character] = dict()
CHARACTERS_BY_OWNER: Dict[int, Character] = dict()

for character in load_characters('./game.json'):
    CHARACTERS_BY_OWNER[character.owner] = character
    CHARACTERS_BY_NAME[character.name] = character

# client
intents = Intents.DEFAULT | Intents.GUILD_MEMBERS | Intents.GUILD_MESSAGE_CONTENT | Intents.DIRECT_MESSAGES

bot = Client(token=TOKEN, intents=intents)


# commands
@bot.command(
    name='stop',
    description='Stops erna!',
    scope=833376462803173427,
    options=[
        Option(
            name='message',
            description='One last message',
            type=OptionType.STRING,
            required=False
        )
    ]
)
async def stop_command(ctx: CommandContext, message: str = 'Have a nice day.'):
    await ctx.send(f'Erna has fallen! {message}')
    quit()


@bot.command(
    name='info',
    description='Displays information about a character',
    scope=833376462803173427,
    options=[
        Option(
            name='name',
            description='The name of the character. If not given, your character will be used.',
            type=OptionType.STRING,
            required=False
        )
    ]
)
async def info_command(ctx: CommandContext, name: str = None):
    character: Character
    if name is None:
        character = CHARACTERS_BY_OWNER[ctx.target.id]
    else:
        character = CHARACTERS_BY_NAME[name]

    if character is None:
        await ctx.send('Cannot find any character with this name or belonging to you.')
        pass

    await ctx.send(
        f'''
        Name: {character.name}
        Full Name: {character.full_name}
        Backstory: {character.backstory}
        '''
    )


if __name__ == '__main__':
    bot.start()
