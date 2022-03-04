import nltk
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
import requests
import random
from pywsd.similarity import max_similarity
from pywsd.lesk import adapted_lesk
from nltk.corpus import wordnet as wn

print("Enter the question :")
question = input()
print("Enter the Answer :")
answer = input()
answer = answer.lower()

# to handle boolean

def dis_boolean():
    if answer == "true" or answer == "false" or answer == "partially true" or answer == "partially false":
        y = ["true", "false", "partially true", "partially false"]
        random.shuffle(y)
        option_choices = ['a', 'b', 'c', 'd']
        print(question)
        for idx, choice in enumerate(y):
            print(option_choices[idx] + ") " + str(choice))


# to handle number
def dis_num(answer):
    if answer.isnumeric():
        answer = int(answer)

    if answer in range(0, 99):
        start = answer - 5
    elif answer in range(100, 999):
        start = answer - 20
    elif answer in range(1000, 9999):
        start = answer - 50
    else:
        start = answer - 100
    if answer in range(0, 99):
        end = answer + 5
    elif answer in range(100, 999):
        end = answer + 25
    elif answer in range(1000, 9999):
        end = answer + 100
    else:
        end = answer + 1000
    num = 4

    def Rand(start1, end1, num):
        res = []
        res.append(answer)

        for j in range(num):

            x = random.randint(start, end)
            if x not in res:
                res.append(x)

        return res
        # shuffle the options

        # Driver Code

    y = Rand(start, end, num)
    random.shuffle(y)
    option_choices = ['a', 'b', 'c', 'd']
    print(question)
    for idx, choice in enumerate(y):
        print(option_choices[idx] + ") " + str(choice))


def wordsense(answer):
    text = question
    text = text.lower()
    answer = answer

    def tokenize_sentences(text):
        sentences = [word_tokenize(text)]
        sentences = [y for x in sentences for y in x]
        # initializing char list
        char_list = ['who', 'when', 'What', 'which', 'where', 'why', 'how', 'whose' '?']
        res = [ele for ele in sentences if all(ch not in ele for ch in char_list)]
        res.insert(0, answer)
        w = ' '.join(res)
        return w

    sentence = tokenize_sentences(text)
    keyword_sentences = {answer: sentence}
# distractors from Wordnet
    def get_distractors_wordnet(syn, word):
        distractors = []
        word = word.lower()
        orig_word = word
        if len(word.split()) > 0:
            word = word.replace(" ", "_")
            hypernym = syn.hypernyms()
        if len(hypernym) == 0:
            return distractors
        for item in hypernym[0].hyponyms():
            name = item.lemmas()[0].name()
            # print ("name ",name, " word",orig_word)
            if name == orig_word:
                continue
            name = name.replace("_", " ")
            name = " ".join(w.capitalize() for w in name.split())
            if name is not None and name not in distractors:
                distractors.append(name)
        return distractors

    def get_wordsense(sent, word):
        word = answer.lower()

        if len(word.split()) > 0:
            word = word.replace(" ", "_")

        synsets = wn.synsets(word, 'n')
        if synsets:
            wup = max_similarity(question, answer, 'wup', pos='n')
            adapted_lesk_output = adapted_lesk(question, word, pos='n')
            lowest_index = min(synsets.index(wup), synsets.index(adapted_lesk_output))
            return synsets[lowest_index]
        else:
            return None

    # Distractors from http://conceptnet.io/
    def get_distractors_conceptnet(word):
        word = word.lower()
        original_word = word
        if (len(word.split()) > 0):
            word = word.replace(" ", "_")
        distractor_list = []
        url = "http://api.conceptnet.io/query?node=/c/en/%s/n&rel=/r/PartOf&start=/c/en/%s&limit=5" % (word, word)
        obj = requests.get(url).json()

        for edge in obj['edges']:
            link = edge['end']['term']

            url2 = "http://api.conceptnet.io/query?node=%s&rel=/r/PartOf&end=%s&limit=10" % (link, link)
            obj2 = requests.get(url2).json()
            for edge in obj2['edges']:
                word2 = edge['start']['label']
                if word2 not in distractor_list and original_word.lower() not in word2.lower():
                    distractor_list.append(word2)

        return distractor_list

    key_distractor_list = {}

    for keyword in keyword_sentences:
        wordsense = get_wordsense(keyword_sentences[keyword][0], keyword)
        if wordsense:
            distractors = get_distractors_wordnet(wordsense, keyword)
            if len(distractors) == 0:
                distractors = get_distractors_conceptnet(keyword)
            if len(distractors) != 0:
                key_distractor_list[keyword] = distractors
        else:

            distractors = get_distractors_conceptnet(keyword)
            if len(distractors) != 0:
                key_distractor_list[keyword] = distractors

        sentence = question
        print(sentence)
        # pattern = re.compile(each, re.IGNORECASE)
        choices = key_distractor_list[answer]

        top4choices = choices[0:3]
        top4choices.append(answer)
        random.shuffle(top4choices)
        option_choices = ['a', 'b', 'c', 'd']
        for idx, choice in enumerate(top4choices):
            print("\t", option_choices[idx], ")", " ", choice)


def main():
    if answer == "true" or answer == "false" or answer == "partially true" or answer == "partially false":
        dis_boolean()
    elif answer.isnumeric():
        dis_num(answer)
    else:
        wordsense(answer)


main()
