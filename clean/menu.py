from typing import Dict


class Menu:
    def __init__(self, items, prompt):
        self.items = items
        self.prompt = prompt

    def display(self):
        print(self.prompt)
        for item in self.items:
            print(f"{item.id}.) {item.name}")

    def select(self)->Dict[int,str]:
        self.display()
        try:
            selection = input("Enter your choice: ")
            if not selection.isdigit():
                raise ValueError("Selection must be a number.")
            
            selection = int(selection)
            if selection > 0 and selection <= len(self.items):
                return self.items[selection - 1]
            else:
                raise ValueError("Selection out of valid range.")
        
        except ValueError as e:
            print(f"Error: {e}")
            return None
