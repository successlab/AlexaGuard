import os
import nltk
import queue
import re
from nltk.parse.corenlp import CoreNLPServer
from nltk.parse.corenlp  import CoreNLPParser
import random

#specifications for random seed and java path
from datetime import datetime
random.seed(datetime.now())

java_path = "C:/Program Files/Java/jre1.8.0_281/bin/java.exe"
os.environ['JAVAHOME'] = java_path

# Yes/No question: RNG Yes or No

# Instruction questions:

def answer_YN_question():
    answers = ["Yes", "No"]
    return random.choice(answers)


def answer_instruction_question(question):

    #THOUGHTS: assume question is pre-parsed might speed things up

    #step one: find "ask and say"

    #flatten sentence to end nodes(doing this in determine_question_type might be faster)

    question = re.sub(r'[^\w\s]', '', question.lower())

    wh_word = ['who', 'what', 'when', 'where', 'why', 'which', 'how']
    other_word = ['like', 'about', 'that','for', 'to']
    ask_say = ['ask','say','asking','saying']

    #WH is a easy scenario
    if any([word in question for word in wh_word]):
        wh_idx = None
        for i in range(len(wh_word)):
            if wh_word[i] in question:
                wh_idx = i
                break
        #regex match all words after the wh_word we found
        #instruct_un_trim = re.search(rf"(?<={wh_word[wh_idx]}).*",question).group()
        instruct_un_regex = r"(?<=" + re.escape(wh_word[wh_idx]) + r").*"
        instruct_un_trim = re.search(instruct_un_regex,question).group()
        return wh_word[wh_idx] + instruct_un_trim

    #trim all words before ask_say word
    ask_say_idx = None
    for i in range(len(ask_say)):
        if ask_say[i] in question:
            ask_say_idx = i
            break
    ask_say_word = ask_say[ask_say_idx]
    #instruct_un_trim = re.search(rf"(?<={ask_say_word}).*",question).group()
    instruct_un_regex = r"(?<=" + re.escape(ask_say_word) + r").*"
    instruct_un_trim = re.search(instruct_un_regex,question).group()

    instruct_un_trim_f_3 = instruct_un_trim.split()[:3] #first 2 word in untrimmed instruction
    if any([word in instruct_un_trim_f_3 for word in other_word]):
        #we found other_word in first 2 word slot
        other_word_idx = None
        for i in range(len(other_word)):
            if other_word[i] in instruct_un_trim_f_3:
                other_word_idx = i
                break
        #instruct_un_trim = re.search(rf"(?<={other_word[other_word_idx]}).*",question).group()
        instruct_un_regex = r"(?<=" + re.escape(other_word[other_word_idx]) + r").*"
        instruct_un_trim = re.search(instruct_un_regex,question).group()
        return instruct_un_trim
    else:
        return instruct_un_trim

    # refer to table!!!
    # good enough for now

def answer_selection_SC(question):
    #find array
    Q_striped = re.sub(r'[^\w\s]', '', question.lower()).split()
    Q_striped_chars = list(filter(lambda x:len(x) == 1,Q_striped))
    #random choice
    return random.choice(Q_striped_chars)

def answer_selection_CC(question,parser):
    question_parsed = next(parser.raw_parse(question))
    #following three line of code
    #will help find the position of the CC word(and/or)
    tags = [ t for w, t in question_parsed.pos() ]
    position = tags.index("CC")
    treeposition = question_parsed.leaf_treeposition(position)
    CC_word = question_parsed[ treeposition[:-1] ].leaves()[0]
    #question_parsed[ treeposition[:-2] ] contain all the parrell option and probably the ',' 
    parrell_structures = question_parsed[ treeposition[:-2] ] #<-btw this is a nltk.tree
    parrell_structures_list = parrell_structures.leaves()
    parrell_structures_list.remove(CC_word)
    return random.choice(' '.join(parrell_structures_list).split(','))

#code for testing
STANFORD = "models"
jars = (
    os.path.join(STANFORD, "stanford-corenlp-4.2.2.jar"),
    os.path.join(STANFORD, "stanford-corenlp-4.2.2-models.jar")
)
if __name__ == "__main__":
    from determine_question_type import determine_qeustion_type
    with CoreNLPServer(*jars):
        parser = CoreNLPParser()


        question = 'You can say what is the current sibor rates'
        #question = 'You can say something like repeat my name.'    
        #question = 'You can ask me things like do dedo deded do'
        #question = 'Ok, Here’s myTuner Radio. I’ve found: A: CHOIFM Radio X 98.1 from Canada, B: Ibiza X Radio from the United Kingdom, C: Radio X London from the United Kingdom. Choose a station.'
        #print(answer_instruction_question(question))
        #question = 'Tell me what you like: studying of music,persute of art, the power of mind, or understanding of science.'
        #question = "Sorry I didn't get that. Please tell me which of the following products you'd like to get a quote for? Car, home, or travel."
        q_t = determine_qeustion_type(question,parser)
        print("q_t is ", q_t)
        #question = 'Tell me what you like: music, art, or understanding of science.'
        if q_t == 'selection_CC':
            print(answer_selection_CC(question,parser))
        elif q_t == 'selection_SC':
            print(answer_selection_SC(question))
        elif q_t == 'Y/N':
            print(answer_YN_question())
        elif q_t == 'instruction':
            print(answer_instruction_question(question))
        elif q_t == 'WH':
            print("WH still in working process")
            import asyncio
            from api_helper import async_chat
            print(asyncio.run(async_chat(question)))
        else:
            print("wait man what happened? q_t = ",q_t)
            import asyncio
            from api_helper import async_chat
            print(asyncio.run(async_chat(question)))
    #https://www.usenix.org/system/files/sec20-guo.pdf

    """
    You can say what is the current sibor rates
    (ROOT
    (S
        (NP (PRP You))
        (VP
        (MD can)
        (VP
            (VB say)
            (SBAR
            (WHNP (WP what))
            (S
                (VP
                (VBZ is)
                (NP (DT the) (JJ current) (NN sibor) (NNS rates)))))))))
    You can say something like repeat my name
    (ROOT
    (S
        (NP (PRP You))
        (VP
        (MD can)
        (VP
            (VB say)
            (NP (NN something))
            (PP (IN like) (NP (NP (NN repeat)) (NP (PRP$ my) (NN name))))))))
    “Ok, Here’s myTuner Radio. I’ve found: 1: CHOIFM Radio X 98.1 from Canada, 2: Ibiza X Radio from the United Kingdom, 3: Radio X London from the United Kingdom. Choose a station.
    (ROOT
    (S
        (`` “)
        (INTJ (UH Ok))
        (, ,)
        (NP (NP (NP (RB Here)) (POS ’s)) (NN myTuner))
        (ADVP (NN Radio))
        (. .)
        (NP (PRP I))
        (VP
        (VBP ’ve)
        (S
            (S (VP (VBN found)))
            (: :)
            (S
            (FRAG
                (NP
                (NP
                    (NP
                    (NML (CD 1) (SYM :))
                    (NNP CHOIFM)
                    (NNP Radio)
                    (NNP X)
                    (CD 98.1))
                    (PP (IN from) (NP (NNP Canada)))
                    (, ,)
                    (NP
                    (NP (CD 2))
                    (: :)
                    (NP
                        (NP (NNP Ibiza) (NNP X) (NNP Radio))
                        (PP
                        (IN from)
                        (NP (DT the) (NNP United) (NNP Kingdom)))))
                    (, ,)
                    (NP-TMP (CD 3)))
                (: :)
                (NP
                    (NP (NNP Radio) (NNP X) (NNP London))
                    (PP
                    (IN from)
                    (NP (DT the) (NNP United) (NNP Kingdom))))
                (. .)))
            (VP (VB Choose) (NP (DT a) (NN station))))))
        (. .)))
    """