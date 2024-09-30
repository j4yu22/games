class Action:
    def __init__(self, entity):
        self.entity = entity  # The entity taking the action

    def attack(self, target):
        """
        The entity makes a melee or ranged attack against the target.
        """
        print(f"{self.entity.name} attacks {target.name}.")
        # Implement the attack logic here

    def cast_spell(self, spell, target):
        """
        The entity casts a spell on the target. 
        Each spell has its own casting time and effects.
        """
        print(f"{self.entity.name} casts {spell['name']} on {target.name}.")
        # Implement the spell casting logic here

    def dash(self):
        """
        The entity gains extra movement for the current turn, doubling their speed.
        """
        print(f"{self.entity.name} takes the Dash action and moves twice their speed.")
        # Double the movement of the entity
        self.entity.speed *= 2

    def disengage(self):
        """
        The entity moves without provoking opportunity attacks.
        """
        print(f"{self.entity.name} disengages and avoids opportunity attacks.")
        # Implement the disengage logic here

    def dodge(self):
        """
        The entity focuses on dodging incoming attacks, gaining disadvantage on incoming attack rolls.
        """
        print(f"{self.entity.name} takes the Dodge action and gains disadvantage on attacks.")
        # Implement the dodge logic here (likely involving setting a flag or status)

    def help(self, ally, target=None):
        """
        The entity helps an ally, granting advantage to the ally's next ability check or attack roll.
        """
        print(f"{self.entity.name} helps {ally.name}, giving them advantage.")
        # Implement the help action logic here

    def hide(self):
        """
        The entity attempts to hide and rolls for Dexterity (Stealth).
        """
        print(f"{self.entity.name} tries to hide.")
        # Implement the hide logic, which might involve a stealth roll

    def ready(self, condition, action):
        """
        The entity prepares an action in response to a specific condition.
        """
        print(f"{self.entity.name} readies an action: '{action}' when '{condition}' occurs.")
        # Implement the ready action

    def search(self):
        """
        The entity searches for something, using Wisdom (Perception) or Intelligence (Investigation).
        """
        print(f"{self.entity.name} takes the Search action.")
        # Implement the search logic here

    def use_object(self, obj):
        """
        The entity uses an object. Could be healing potions, magical items, etc.
        """
        print(f"{self.entity.name} uses {obj}.")
        # Implement the logic for interacting with an object
