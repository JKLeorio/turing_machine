from collections import namedtuple
from pprint import pprint
from abc import ABC, abstractclassmethod

import os
import json
import time
import csv

clear = lambda: os.system('cls')


LEFT = "left"
RIGHT = "right"
INPLACE = "inplace"

STOP = 'stop'


Command = namedtuple("Command", ["next_state", "new_value", "direction"])


class Machine:
    """
        Машина тюринга.

        Аргументы для инициализации:

        commands словарь в виде:
        commands = {
            "0": {
                'q1': ('q0', "1", RIGHT),
                'q0': STOP
            }, 
            "1": {
                'q1': ('q1', "1", RIGHT),
                'q0': ('q1', "0", LEFT)
            }
        }  

        При этом 'q1', 'q2' состояния, а ('q0', "1", RIGHT) уже команды

        tape: лента с первоначальными данными, если алфавит = [0, 1],
        то tape например: [1,1, 0, 1]

    """
    def __init__(self, commands, tape: list[int], position: int, delay: float = 1):
        self.commands = commands
        self.tape = tape
        self.position = position
        self.delay = delay

    def start(self):
        command = self.get_command('q1')

        while True:
            
            self.print(command)
            time.sleep(self.delay)
            

            if command == STOP:
                break

            self.tape[self.position] = command.new_value

            if command.direction == RIGHT: 
                self.position += 1
            elif command.direction == LEFT: 
                self.position -= 1

            self.extend_if_overflow()
            command = self.get_command(command.next_state)

        print("Закончен!")

    def get_command(self, state):
        command = self.commands[self.tape[self.position]][state]

        if isinstance(command, tuple) or isinstance(command, list):
            command = Command(*command)

        return command

    def extend_if_overflow(self):
        if self.position >= len(self.tape):
            self.tape.append(0)

        if self.position == -1:
            self.tape.insert(0,0)


    def print(self, command):
        space_number = self.position*5+2
        clear()
        print(f"{self.position=}, {command=}")
        print(space_number * " " + '⌄')
        print(self.tape)


class Console:

    def start(self): 
        print("""
        Выберите откуда загрузить данные\n
        1)Из консоли
        2)Из JSON
        3)Из CSV
        """)
        choice = input("Номер вашего выбора: ")
        if choice == "1":
            self.from_console()

        elif choice == "2":

            self.commands = self.from_json(self.get_filename())
            self.get_tape()
            self.get_position()
            machine = Machine(self.commands, self.tape, self.position)
            machine.start()


        elif choice == "3":
            self.commands = self.from_csv(self.get_filename())
            self.get_tape()
            self.get_position()
            print(self.commands)
            machine = Machine(self.commands, self.tape, self.position)
            machine.start()


    def get_tape(self):
        clear()
        print("Введите начальное состояние пленки")
        tape = list(input(": "))
        print(f"лента: {tape}")
        self.wait_next()
        self.tape = tape
        

    def wait_next(self):
        input("Нажмите Enter чтобы продолжить...")


    def from_console(self):
        console = FromConsole()
        console.get_alphabet()
        console.get_commands()
        console.get_tape()
        console.get_position()
        machine = console.get_machine()
        machine.start()

    def get_filename(self):
        print("Введите имя файла(с расширением)")
        while True:
            file_name = input()
            if os.path.exists(file_name):
                return file_name
            print("Такого файла не существует")
            
    
    def get_position(self):
        clear()
        position = input("Введите укажите ячейку (начиная слева): ")
        self.position = int(position) - 1
            

    def from_csv(self, filename):
        csv_ob = FromCsv(filename)
        return csv_ob.get_commands()


    def from_json(self, filename):
        json_ob = FromJSON(filename)
        return json_ob.get_commands()

    
    def get_machine(self):
        return Machine(
            self.commands,
            self.tape,
            self.position
        )
        


class FromConsole:
    
    def __init__(self) -> None:
        self.alphabet = None
        self.commands = None
        self.tape = None
        self.position = None


    def get_commands(self):
        commands = {}

        clear()

        for letter in self.alphabet:
            print("Теперь для каждого значения создайте команды")
            print("чтобы закончить на имя команды напишите 'end'")
            print("чтобы сделать команды конечным, напишите в следующую команду 'stop'")
            print("---------------------------------------------------")
            print(f"Комманды для {letter}")
            print()
            commands[letter] = {}

            while True:
                command_name = input("имя состояния: ")
                if command_name == "end":
                    break

                next_command = input("следующая состояние: ")

                if next_command == "stop":
                    commands[letter][command_name] = STOP
                    continue

                command_value = input("новое значение: ")
                command_dir = input("направление (right, left): ")

                if command_dir not in ['right', 'left']:
                    print("Направление должно быть right или left !")
                    continue

                print("-----------------------------------------")

                commands[letter][command_name] = (
                    next_command,
                    command_value,
                    command_dir
                )

            print("------------------------")
            print(f"Вы создали команды для : {letter}")
            pprint(commands[letter])
            print("------------------------")
            self.wait_next()
            clear()

        print("-----------------")
        print("Все команды")
        pprint(commands)

        print("-----------------")
        save = input("сохранить (yes/no): ")
        if save == "yes":
            with open("./commands.json", "w") as file:
                file.write(json.dumps(commands))

        self.wait_next()
        self.commands = commands

    def get_alphabet(self):
        clear()
        print("""
            С начала вы должны ввести алфавит разделенные
            запятой, а потом команды для каждого из них.
            Введите данные точно как в таблице, иначе программа даст ошибку
        """)

        alphabet = input("введите алфавит: ")
        alphabet = [i.strip() for i in alphabet.split(",")]

        print(f"Вы создали алфавит: {alphabet}")
        self.wait_next()

        self.alphabet = alphabet


    def get_tape(self):
        clear()
        print("Введите начальное состояние пленки разделенная запятой")
        tape = input(": ")
        tape = [i.strip() for i in tape.split(",")]
        print(f"лента: {tape}")

        self.wait_next()
        self.tape = tape

    def get_position(self):
        clear()
        position = input("Введите укажите ячейку (начиная слева): ")
        self.position = int(position) - 1

    def wait_next(self):
        input("Нажмите Enter чтобы продолжить...")

    
    def get_machine(self):
        return Machine(
            self.commands,
            self.tape,
            self.position
        )



class FromFile(ABC):
    def __init__(self, commands_file_name):
        self.commands_file_name = commands_file_name
        self.serialize()


    @abstractclassmethod
    def serialize(self, commands):
        self.commands = commands

    def get_commands(self):
        return self.commands



class FromCsv(FromFile):
    
    def serialize(self):
        with open(self.commands_file_name, "r") as file:
            data = csv.reader(file, delimiter=" ")
            data = [row[0].split("\t") for row in data]
            commands = dict()
            columns = data.pop(0)
            columns.pop(0)
            for row in data:
                commands[row[0]] = {columns[i-1] : row[i].split(",") if row[i] != "stop" else "stop" for i in range(1,len(row))}

            super().serialize(commands)


class FromJSON(FromFile):

    def serialize(self):
        with open(self.commands_file_name, "r") as file:
            file = self.get_file()
            file_data = file.read()
            data = file_data.replace("\n", "")
            commands = json.loads(data)
            super().serialize(commands)



commands = {
    "0": {
        'q1': ('q0', "1", RIGHT),
        'q0': STOP
    }, 
    "1": {
        'q1': ('q1', "1", RIGHT),
        'q0': ('q1', "0", LEFT)
    }
}   


console = Console()
console.start()

# machine = Machine(commands, ["1", "0", "1", "1", "0", "0", "1", "1"], 3)
# machine = console.get_machine()
# machine.start()
