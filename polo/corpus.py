
import re, nltk
from gensim.corpora import Dictionary
from database import Database

import timeit

class Corpus:

    db_schema = {
        'doc': ('doc_id INTEGER','doc_str TEXT'),
        'word': ('word_id INTEGER','word_str TEXT','word_freq INTEGER'),
        'docword': ('doc_id INTEGER','word_id INTEGER','word_count INTEGER')
    }

    def __init__(self,dbfile,dictfile=None):
        self.dictfile = dictfile + '.dict'
        self.dbi = Database(dbfile,self.db_schema)

    # This method is abstract and must be overwritten for each case.
    # The generator should yield a single line of text. The generator
    # should also make sure the doc is unique
    def src_doc_generator(self):
        pass

    # One problem with Gensim is that it does not preserve document
    # IDs and tags; it relies on the list index. So at some point you
    # need to create a mapping between the source doc_id and the local
    # gensim id. This will require changing the generator so that it
    # supplies these values in addition to the text string. Also, need
    # to make stopwords configurable. And leave NLP preprocessing to
    # the generator.
    def produce(self):
        doc_n = 0
        #docs = set() # We use a set to filter out simple duplicates ... >>> SHOULD THIS HAPPEN HERE? NO -- IN THE GENERATOR
        docs = []
        doctokens = [] # AKA gensim "text"
        stopwords = nltk.corpus.stopwords.words('english')

        NOALPHA = re.compile('[^a-z]+')
        def prep_string(my_string,pattern = NOALPHA):
            return re.sub(pattern, ' ', my_string.strip().lower())

        print('Getting src docs')
        for doc in self.src_doc_generator():
            content = re.sub(NOALPHA, ' ', doc.strip().lower())
            #docs.add(content)
            docs.append(content)
            doctokens.append([token for token in nltk.word_tokenize(content) if token not in stopwords])
            doc_n += 1
            if doc_n % 1000 == 0: print(doc_n)
                
        print('Creating the dictionary')
        dictionary = Dictionary(doctokens)
        dictionary.compactify()
        dictionary.filter_extremes(keep_n=None)
        if self.dictfile:
            dictionary.save_as_text(self.dictfile, sort_by_word=True)

        with self.dbi as db:

            print('Creating DOC')
            db.create_table('doc')
            for i, doc in enumerate(docs):
                db.cur.execute('INSERT INTO doc VALUES (?,?)',(i,doc))

            print('Creating WORD')
            db.create_table('word')
            for item in dictionary.iteritems():
                db.cur.execute('INSERT INTO word (word_id, word_str) VALUES (?,?)',item)

            print('Creating DOCWORD')
            db.create_table('docword')
            for i, tokens in enumerate(doctokens):
                for item in (dictionary.doc2bow(tokens)):
                    db.cur.execute('INSERT INTO docword (doc_id,word_id,word_count) VALUES (?,?,?)',[i,item[0],item[1]])

    def update_word_freqs(self):
        with self.dbi as db:
            for r in db.cur.execute("SELECT sum(word_count) as 'word_freq', word_id FROM docword GROUP BY word_id"):
                db.cur.execute("UPDATE word SET word_freq = ? WHERE word_id = ?",r)

    def pull_gensim_corpus(self):
        with self.dbi as db:
            n = db.cur.execute("SELECT count(*) FROM docword").fetchone()[0]
            self.gensim_corpus = [[] for _ in range(n)]
            for r in db.cur.execute('SELECT doc_id, word_id, word_count FROM docword ORDER BY doc_id, word_id'):
                self.gensim_corpus[r[0]].append((r[1], r[2]))

    def pull_gensim_token2id(self):
        self.gensim_token2id = {}
        with self.dbi as db:
            for r in db.cur.execute("SELECT word_str,word_id FROM word"):
                self.gensim_token2id[r[0]] = r[1]

    def pull_gensim_id2token(self):
        self.gensim_id2token = {}
        with self.dbi as db:
            for r in db.cur.execute("SELECT word_str,word_id FROM word"):
                self.gensim_id2token[r[1]] = r[0]
        
        
if __name__ == '__main__':

    print('This is an abstract class. Override src_doc_generator in another class to use it.')
