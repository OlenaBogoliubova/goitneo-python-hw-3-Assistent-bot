from datetime import datetime, timedelta
from collections import defaultdict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value.isalpha():
            raise ValueError(
                "Invalid name format. Name should contain only alphabetic characters.")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Invalid phone number format.")
        super().__init__(value)


class Birthday(Field):
    DATE_FORMAT = '%d.%m.%Y'

    def __init__(self, value):
        try:
            datetime.strptime(value, self.DATE_FORMAT)
        except ValueError:
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY.")
        super().__init__(value)


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        new_phone = Phone(phone)
        self.phones.append(new_phone)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p

    def add_birthday(self, birthday):
        if not self.birthday:
            self.birthday = Birthday(birthday)
        else:
            print("Birthday already exists.")

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"


class AddressBook:
    def __init__(self):
        self.data = defaultdict(list)

    def add_record(self, record):
        self.data[record.name.value].append(record)

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        today = datetime.today().date()
        birthdays_this_week = defaultdict(list)

        for records in self.data.values():
            for record in records:
                if record.birthday:
                    name = record.name.value
                    birthday = datetime.strptime(
                        record.birthday.value, Birthday.DATE_FORMAT).date()
                    birthday_this_year = birthday.replace(year=today.year)

                    if birthday_this_year < today:
                        birthday_this_year = birthday_this_year.replace(
                            year=today.year + 1)

                    delta_days = (birthday_this_year - today).days

                    if delta_days < 7:
                        next_birthday_day = (
                            today + timedelta(days=delta_days)).strftime('%A')
                        if next_birthday_day == 'Saturday' or next_birthday_day == 'Sunday':
                            # Birthday falls on the weekend, greet on Monday
                            next_birthday_day = 'Monday'
                        birthdays_this_week[next_birthday_day].append(name)

        current_day = today.strftime('%A')
        for i in range(7):
            day = (today + timedelta(days=i)).strftime('%A')
            if day in birthdays_this_week:
                print(f"{day}: {', '.join(birthdays_this_week[day])}")
            elif day == current_day and current_day not in birthdays_this_week:
                print(f"No birthdays this week.")
            else:
                print(f"{day}: No birthdays.")


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command. Usage: [command] [arguments]"

    return inner


@input_error
def add_contact(args, book):
    if len(args) == 2:
        name, phone = args
        record = Record(name, None)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    else:
        raise IndexError


@input_error
def change_contact(args, book):
    if len(args) == 2:
        name, new_phone = args
        records = book.find(name)
        if records:
            for record in records:
                record.edit_phone(record.phones[0].value, new_phone)
            return "Contact updated."
        else:
            raise KeyError
    else:
        raise IndexError


@input_error
def show_phone(args, book):
    if len(args) == 1:
        name = args[0]
        records = book.find(name)
        if records:
            return records[0].phones[0].value
        else:
            raise KeyError
    else:
        raise IndexError


@input_error
def show_all(book):
    if book.data:
        for records in book.data.values():
            for record in records:
                print(record)
    else:
        raise ValueError("No contacts.")


@input_error
def add_birthday(args, book):
    if len(args) == 2:
        name, birthday_input = args
        records = book.find(name)
        if records:
            for record in records:
                record.add_birthday(birthday_input)
            return "Birthday added."
        else:
            raise KeyError
    else:
        raise IndexError


@input_error
def show_birthday(args, book):
    if len(args) == 1:
        name = args[0]
        records = book.find(name)
        if records and records[0].birthday:
            return records[0].birthday.value
        else:
            raise KeyError
    else:
        raise IndexError


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            show_all(book)
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            book.get_birthdays_per_week()
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
