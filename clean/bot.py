class Bot:
    """
    Clase base para cualquier tipo de bot.
    """

    def __init__(self, name):
        self.name = name
        self.status = 'stopped'

    def start(self):
        self.status = 'running'
        print(f"{self.name} bot started.")
    
    def stop(self):
        self.status = 0
        print(f"{self.name} bot stopped.")

    def get_status(self):
        return self.status