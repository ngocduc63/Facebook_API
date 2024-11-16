LIST_BLOCK_WORD = [
    'dm',
    'fuck',
]


def contains_word_ignore_case(string):
    string = string.lower()
    word_list = [word.lower() for word in LIST_BLOCK_WORD]
    return any(word in string for word in LIST_BLOCK_WORD)

