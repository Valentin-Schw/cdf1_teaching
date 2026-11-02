"""Loops"""

"""While loop"""

# A while-loop is a control flow statement for specifying iteration, which allows code to be executed repeatedly.

# TODO: Write a while loop that prints break_condition and increments it, until it reaches 5

break_condition = 0

while break_condition < 10:
    print(break_condition)
    break_condition += 1
else:
    print("Break condition reached 10.")

...

print("out of while loop")

# ----------------------------------------------

"""For loop"""

# For-loop is a control flow statement for specifying iteration, which allows code to be executed repeatedly.

# TODO: Iterate over pets, printing each one

pets = ["dog", "cat", "horse", "rabbit", "snake"]

for i in pets:
    print(i)

my_list = [34, 71]

for i in my_list:
    print(i - 23)

for i in range(4):
    print(i)