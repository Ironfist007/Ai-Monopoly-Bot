import property


class Player:
    def __init__(self, player_id: int, balance=1500, position=0, properties=None):
        self.balance = balance
        self.position = position
        self.properties: list[property.Property] = properties or []
        self.ID = player_id
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_free_cards = 0

    def __str__(self):
        return self.ID

    def move(self, num_spaces):
        self.position = (self.position + num_spaces) % len(self.properties)

    def pay_rent(self, amount, recipient):
        self.balance -= amount
        recipient.balance += amount

    def buy(self, property):
        self.balance -= property.value
        self.properties.append(property)
        property.owner = self.ID

    def sell(self, property):
        # try:
            for item in self.properties:
                if item.position == property.position:
                    self.properties.remove(item)
                    item.owner = None
                    self.balance += (item.value * .9)
        #
        # except:
        #     for i in self.properties:
        #         print(i.position)
        #     print("---------")
        #     print(property.position)
    
    def go_to_jail(self):
        """Send player to jail"""
        self.in_jail = True
        self.jail_turns = 0
        self.position = 10  # Jail is position 10
    
    def try_get_out_of_jail(self, dice_roll=None, pay_fine=False, use_card=False):
        """Attempt to get out of jail"""
        if not self.in_jail:
            return True
        
        # Use get out of jail free card
        if use_card and self.get_out_of_jail_free_cards > 0:
            self.get_out_of_jail_free_cards -= 1
            self.in_jail = False
            self.jail_turns = 0
            return True
        
        # Pay $50 fine
        if pay_fine and self.balance >= 50:
            self.balance -= 50
            self.in_jail = False
            self.jail_turns = 0
            return True
        
        # Roll doubles (not implemented in current dice system)
        # For now, automatic release after 3 turns
        self.jail_turns += 1
        if self.jail_turns >= 3:
            # Must pay fine after 3 turns
            if self.balance >= 50:
                self.balance -= 50
            self.in_jail = False
            self.jail_turns = 0
            return True
        
        return False
    
    def can_move(self):
        """Check if player can move (not in jail or got out)"""
        return not self.in_jail
