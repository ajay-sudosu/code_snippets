import random


def make_name():
    first_names = ('John', 'Andy', 'Joe', 'Frank', 'Kevin', 'Leo')
    last_names = ('Johnson', 'Smith', 'Williams', 'Cook', 'Parley')
    group = "".join(random.choice(first_names) + " " + random.choice(last_names))
    return group

def get_city():
    city = ['Mumbai', 'Maharashtra', 'Delhi', 'Bangalore', 'Karnataka']
    return random.choice(city)


def get_book_name():
    books = ['The 4th Road', 'Shining dark', 'Crossing busy road', 'Patience', 'Farud is the downtown']
    return random.choice(books)
