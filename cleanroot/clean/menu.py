from typing import Any, Dict,Generic, List, TypeVar

T = TypeVar('T')  # Tipo genérico


class Menu(Generic[T]):
    def __init__(self, items:List[T], prompt,objectStringDescriptor:str="name"):
        if(len(items)<1):
            raise BaseException("Empty List to show the menu options")
        self.items = items
        self.prompt = prompt
        self.objectStringDescriptor = objectStringDescriptor

    def display(self):
        print(self.prompt)

        for index, item in enumerate(self.items):
            #print(f"{item.id}.) {item.name}")
            print(f"{index+1}.) {getattr(item, self.objectStringDescriptor, None)}")

            
    def select(self)->T:
        self.display()

        selection = input("Enter your choice: ")
        if not selection.isdigit():
            raise ValueError("Selection must be a number.")
        
        selection = int(selection)
        if selection > 0 and selection <= len(self.items):
            return self.items[selection - 1]
        else:
            raise ValueError("Selection out of valid range.")
    

