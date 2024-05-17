import sys
import time
from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE

class ConsoleManager:
    def __init__(self, messages):
        self.messages = messages
        self.processes = []

    def open_new_console(self):
        new_console_cmd = [
            sys.executable, "-c",
            """import sys
for line in sys.stdin:
    sys.stdout.write(line)
    sys.stdout.flush()"""
        ]

        return Popen(
            new_console_cmd,
            stdin=PIPE, bufsize=1, universal_newlines=True,
            creationflags=CREATE_NEW_CONSOLE
        )

    def start_consoles(self):
        for _ in self.messages:
            self.processes.append(self.open_new_console())

    def display_messages(self):
        for proc, msg in zip(self.processes, self.messages):
            proc.stdin.write(msg + "\n")
            proc.stdin.flush()

    def keep_consoles_open(self, duration=10):
        time.sleep(duration)

    def close_consoles(self):
        for proc in self.processes:
            proc.communicate("bye\n")

    def run(self):
        self.start_consoles()
        self.display_messages()
        self.keep_consoles_open()
        self.close_consoles()


if __name__ == "__main__":
    messages = ['This is Console1', 'This is Console2']
    console_manager = ConsoleManager(messages)
    console_manager.run()
