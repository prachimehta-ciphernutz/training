import string

def count_freq(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = text.split()

    freq = {}
    for word in words:
        if word in freq:
            freq[word] += 1
        else:
            freq[word] = 1
    
    return freq

def get_count(item):
    return item[1]

def sort_frequency(freq):
    return sorted(freq.items(), key=get_count, reverse=True)

print(sort_frequency(count_freq("Prachi Prachi hello Hello prachi!! hello hello")))
