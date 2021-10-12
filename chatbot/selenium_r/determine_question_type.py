import nltk
import queue
import re
import os
from nltk.parse.corenlp import CoreNLPServer
from nltk.parse.corenlp  import CoreNLPParser

#import os
#from nltk.parse import stanford

#parser = stanford.StanfordParser(model_path="/location/of/the/englishPCFG.ser.gz")
#sentences = parser.raw_parse_sents("What is your name?")
#print(sentences)

# GUI
#for line in sentences:
#    for sentence in line:
#        sentence.draw()

java_path = "C:/Program Files/Java/jre1.8.0_281/bin/java.exe"
os.environ['JAVAHOME'] = java_path

# The server needs to know the location of the following files:
#   - stanford-corenlp-X.X.X.jar
#   - stanford-corenlp-X.X.X-models.jar
STANFORD = "models"

# Create the server

'''server = CoreNLPServer(
   os.path.join(STANFORD, "stanford-corenlp-4.2.2.jar"),
   os.path.join(STANFORD, "stanford-corenlp-4.2.2-models.jar"),    
)'''

#where to get -> https://search.maven.org/artifact/edu.stanford.nlp/stanford-corenlp/4.2.2/jar
# p.s. mordel.jar and .jar

# Start the server in the background
# server.start()

jars = (
    os.path.join(STANFORD, "stanford-corenlp-4.2.2.jar"),
    os.path.join(STANFORD, "stanford-corenlp-4.2.2-models.jar")
)

#support function
def is_leaf(tree):
    if type(tree) != nltk.tree.Tree:
        raise "is_leaf(tree) error: input is not type nltk.tree.Tree"
    if tree.height() <= 2:
        return True
    return False

def check_cont(s):
 
    # Get the length of the string
    l = len(s)
 
    # sort the given string
    s = ''.join(s)
 
    # Iterate for every index and
    # check for the condition
    for i in range(1, l):
 
        # If are not consecutive
        if ord(s[i]) - ord(s[i - 1]) != 1:
            return False
 
    return True

def determine_qeustion_type(question,parser):
    '''
    Yes/No question:
        1. contain SQ *
        2. does not contain SBARQ(wh- words) *
        3. does not contain CC(or of IAQ) *
    Instruction questions
        1. find VB,VBG,VBP *
        2. are they ask, say (or +ing) *
    Selection questions:
        1. contain CC tag(or) *
        2. extract number/single character *
            2.1 check are these number continuous 
    WH Question
        1. contiant 'WDT', 'WHADJP', 'WHADVP', *
            'WHNP', 'WHPP', 'WP', 'WP$', 'WP-S', 'WRB' *
    '''
    #print(question)
    leaf_queue = queue.Queue()
    question_parsed = next(parser.raw_parse(question))
    leaf_queue.put(question_parsed)
    have_SQ = False
    have_SBARQ = False
    have_CC = False
    have_VB_VBG_BVP = False
    have_ask_say = False
    ask_say = ['ask','say','asking','saying']
    have_WH = False 
    # including 'WDT', 'WHADJP', 'WHADVP',
    # 'WHNP', 'WHPP', 'WP', 'WP$', 'WP-S', 'WRB'
    have_cont_num = False
    #continuous number or character
    while not leaf_queue.empty():
        head = leaf_queue.get()
        lb = head.label()
        if not is_leaf(head):
            for x in head:
                leaf_queue.put(x)
        if lb == 'SBARQ':
            have_SBARQ = True
        if lb == 'SQ':
            have_SQ = True
        if lb == 'CC':
            have_CC = True
        if lb == 'VB' or lb == 'VBG' or lb == 'BVP':
            have_VB_VBG_BVP = True
        if lb == 'WDT' or lb == 'WHADJP' or lb == 'WHADVP' or \
            lb == 'WHNP' or  lb == 'WHPP' or lb ==  'WP' or \
            lb ==  'WP$' or lb == 'WP-S' or lb ==  'WRB':
            have_WH = True
    

        #print(head)
    Q_striped = re.sub(r'[^\w\s]', '', question.lower()).split()
    if have_VB_VBG_BVP:
        if any([word in Q_striped for word in ask_say]):
            have_ask_say = True
    Q_striped_chars = list(filter(lambda x:len(x) == 1,Q_striped))
    if len(Q_striped_chars) > 1: #have more then one choice
        if check_cont(Q_striped_chars): #check numbers
            have_cont_num = True

    if have_CC or have_cont_num:
        return 'selection_CC'
    if have_cont_num:
        return 'selection_SC'
    if have_SQ and not have_SBARQ:
        return 'Y/N'
    if have_ask_say:
        return 'instruction'
    if have_WH:
        return 'WH'

if __name__ == "__main__":
    with CoreNLPServer(*jars):
        parser = CoreNLPParser()
        #parse = next(parser.raw_parse("I put the book in the box on the table."))
        st1 = 'How can I help you?'
        st2 = 'Are you staying or going?'
        st3 = '...Just ask me for news, politics, or a story from history. What would you like to do?'
        st4 = 'A: high, B: medium, C: low. Choose one.'
        st5 = 'What’s your zip code?'
        st6 = 'Are you ready?'
        st7 = 'You’re going, aren’t you?'
        st8 = 'Welcome to the Reddit Notifier skill... just Say: Help me'
        st9 = 'To get started, you can get a quote, listen to the daily briefing, or get an account summary'

        print(determine_qeustion_type(st1,parser))
        print(determine_qeustion_type(st2,parser))
        print(determine_qeustion_type(st3,parser))
        print(determine_qeustion_type(st4,parser))
        print(determine_qeustion_type(st5,parser))
        print(determine_qeustion_type(st6,parser))
        print(determine_qeustion_type(st7,parser))
        print(determine_qeustion_type(st8,parser))
        print(determine_qeustion_type(st9,parser))

    #server.stop()


    '''
    some example

    How can I help you?
    (ROOT
    (SBARQ
        (WHADVP (WRB How))
        (SQ (MD can) (NP (PRP I)) (VP (VB help) (NP (PRP you))))
        (. ?)))
    Are you ready?
    (ROOT (SQ (VBP Are) (NP (PRP you)) (ADJP (JJ ready)) (. ?)))
    You’re going, aren’t you?
    (ROOT
    (SQ
        (S (NP (PRP You)) (VP (VBP ’re) (S (VP (VBG going)))))
        (, ,)
        (SQ (VBP are) (RB n’t) (NP (PRP you)))
        (. ?)))
    1: high, 2: medium, 3: low. Choose one.
    (ROOT
    (S
        (S
        (FRAG
            (NP
            (NP (CD 1))
            (: :)
            (NP (JJ high))
            (, ,)
            (NP
                (NP (CD 2))
                (: :)
                (NP
                (NP (NN medium))
                (, ,)
                (ADJP (NP (CD 3) (SYM :)) (JJ low)))))))
        (. .)
        (S (VP (VB Choose) (NP (CD one))))
        (. .)))
    Are you staying or going?
    (ROOT
    (SQ
        (VBP Are)
        (NP (PRP you))
        (VP (VBG staying) (CC or) (VBG going))
        (. ?)))
    '''