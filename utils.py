def fuzzy(string):
    words = []
    for i in range(len(string)):
        words.append(string[0:i] + "_" + string[i + 1 :])
    return words

