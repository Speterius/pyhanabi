colors = ['blue', 'red', 'green', 'yellow', 'white']
card_stack = dict.fromkeys(colors, [])

card = {"color": "green", "number": 1}
# card_stack[card["color"]].append(card)

print(card_stack)

for key, lst in card_stack.items():
    if key == card["color"]:
        card_stack[key] = [*lst, card]

print(card_stack)
