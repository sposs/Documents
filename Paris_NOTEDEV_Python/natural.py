if my_value in my_list:
    print(my_value)
elif 1 < my_value < 3:
    my_value *= 34
elif my_value and (my_other_value or something):
    do_something()
else:
    raise Exception("Bad!")
