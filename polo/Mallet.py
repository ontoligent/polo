import os, configparser, subprocess, sys, sqlite3, re
from math import log
from lxml import etree

class PoloTrial:
    
    def __init__(self,project,trial,mallet_path,projects_path='projects'):
        self.project = project
        self.trial = trial
        self.project_path = '%s/%s' % (projects_path, self.project)
        self.trial_path = '%s/trials/%s' % (self.project_path,self.trial)
        self.mallet_path = mallet_path
        self.verbose = False
        self.import_config()

    def import_config(self):
        cfg_file = '%s/config.ini' % self.project_path
        if os.path.exists(cfg_file):
            self.cfg = configparser.ConfigParser()
            self.cfg.read(cfg_file)
        else:
            sys.exit()        
    
class MalletInterface:
    def __init__(self,trial):
        
        self.trial = trial
        
        self.mallet = {'import-file':{}, 'train-topics':{}}
        self.mallet['import-file']['extra-stopwords'] = '%s/corpus/extra-stopwords.txt' % trial.project_path
        self.mallet['import-file']['input'] = '%s/corpus/corpus.csv' % trial.project_path
        self.mallet['import-file']['output'] = '%s/corpus.mallet' % trial.trial_path
        self.mallet['import-file']['keep-sequence'] = '' # Delete key to remove option
        self.mallet['import-file']['remove-stopwords'] = '' # Delete key to remove option
        self.mallet['train-topics']['num-topics'] = 40 # default
        self.mallet['train-topics']['num-top-words'] = 7 # default
        self.mallet['train-topics']['num-iterations'] = 100 # default
        self.mallet['train-topics']['optimize-interval'] = 10 # default
        self.mallet['train-topics']['num-threads'] = 1 # default
        self.mallet['train-topics']['input'] = self.mallet['import-file']['output']
        self.mallet['train-topics']['output-topic-keys'] = '%s/model-topic-keys.txt' % trial.trial_path
        self.mallet['train-topics']['output-doc-topics'] = '%s/model-doc-topics.txt' % trial.trial_path
        self.mallet['train-topics']['word-topic-counts-file'] = '%s/model-word-topic-counts.txt' % trial.trial_path
        self.mallet['train-topics']['xml-topic-report'] = '%s/model-topic-report.xml' % trial.trial_path
        self.mallet['train-topics']['xml-topic-phrase-report'] = '%s/model-topic-phrase-report.xml' % trial.trial_path

        # Override values if found in the config file for the trial
        user_args = ['num-topics','num-top-words','num-iterations','optimize-interval','num-threads']
        for arg in user_args:
            if trial.cfg[trial.trial][arg]:
                self.mallet['train-topics'][arg] = trial.cfg[trial.trial][arg]

    def mallet_run_command(self,op):
        my_args = ['--{0} {1}'.format(arg,self.mallet[op][arg]) for arg in self.mallet[op]]
        output = subprocess.check_output([self.trial.mallet_path, op] + my_args, shell=False)
        #print(output)
        
    def mallet_import(self):
        self.mallet_run_command('import-file')

    def mallet_train(self):
        self.mallet_run_command('train-topics')

class Table:
    
    src_file_path = None
    
    def __init__(self,name,raw_fields,z=0):
        self.name = name
        self.raw_fields = raw_fields
        self.z = z
        self.tn_list = ['t{0}'.format(tn) for tn in range(int(self.z))]
        self.get_field_defs()
        self.get_sql_def() 
        
    def get_field_defs(self):
        self.field_defs = []
        fields = [] # To use in the field string for INSERTs
        for field in self.raw_fields:
            if field[0] == '_topics_':
                t_type = field[1]
                for i in range(int(self.z)):
                    self.field_defs.append('{0} {1}'.format(self.tn_list[i],t_type))
                    fields.append(self.tn_list[i])
            else:
                self.field_defs.append(' '.join(field))
                fields.append(field[0])
        # Also create the field string for INSERTs
        field_str = ','.join(fields)
        value_str = ','.join(['?' for _ in range(len(fields))])
        self.insert_sql = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(self.name,field_str,value_str)
        
    def get_field_dict(self):
        self.field_dict = {}
        for field_def in self.field_defs:
            k, v = field_def.split(' ')
            self.field_dict[k] = v
                
    def get_sql_def(self):
        sql_def  = ' '.join(['CREATE TABLE IF NOT EXISTS', self.name, '('])
        sql_def += ', '.join(self.field_defs)
        sql_def += ')'
        self.sql_def = sql_def
    
    def create_table(self,conn):
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS {0}'.format(self.name))
        cur.execute(self.sql_def)
        conn.commit()
        cur.close()
    
    def src_data_iter(self):
        with open(self.src_file_path) as src_file:
            for line in src_file.readlines(): 
                yield line.strip()

    # This is an abstract class            
    def import_src_data(self,conn):
        pass
            
class MalletModel:
    
    tables = {
        'doc': object,
        'topic': object,
        'doctopic': object,
        'wordtopic': object,
        'topicphrase': object,
        'config': object
    }
        
    def __init__(self,mallet_interface):
        
        self.trial = mallet_interface.trial
        self.trial_cfg = self.trial.cfg[self.trial.trial]
        self.z = self.trial_cfg['num-topics']
        self.generate_dbfilename()
        
        self.tables['doc'] = self.DocTable()
        self.tables['topic'] = self.TopicTable()
        self.tables['doctopic'] = self.DocTopicTable(self.z)
        self.tables['wordtopic'] = self.WordTopicTable(self.z)
        self.tables['topicphrase'] = self.TopicPhraseTable()
        self.tables['config'] = self.ConfigTable(mallet_interface)

        self.tables['doc'].src_file_path = mallet_interface.mallet['import-file']['input']
        self.tables['topic'].src_file_path = mallet_interface.mallet['train-topics']['output-topic-keys']
        self.tables['doctopic'].src_file_path = mallet_interface.mallet['train-topics']['output-doc-topics']
        self.tables['wordtopic'].src_file_path = mallet_interface.mallet['train-topics']['word-topic-counts-file']        
        self.tables['topicphrase'].src_file_path = mallet_interface.mallet['train-topics']['xml-topic-phrase-report']
        
    class DocTable(Table):
        
        raw_fields = (('doc_id','TEXT'), ('doc_label','TEXT'), ('doc_content','TEXT'))

        def __init__(self):
            Table.__init__(self,'doc',self.raw_fields)
            
        def import_src_data(self, conn):
            self.create_table(conn)
            cur = conn.cursor()
            for line in self.src_data_iter():
                values = []
                row = line.split(',')
                values.append(row[0]) # doc_id
                values.append(row[1]) # doc_label
                values.append(row[2]) # doc_content
                cur.execute(self.insert_sql,values)
            conn.commit()
            cur.close()
            
    class TopicTable(Table):
        
        raw_fields = (('topic_id', 'TEXT'), ('topic_alpha', 'REAL'), ('total_tokens', 'INTEGER'), ('topic_words', 'TEXT'))
        
        def __init__(self):
            Table.__init__(self,'topic',self.raw_fields)

        def import_src_data(self, conn):
            self.create_table(conn)
            cur = conn.cursor()
            for line in self.src_data_iter():
                values = []
                row = line.split('\t')
                values.append('t%s' % row[0]) # topic_id <-- SHOULD THIS USE self.tn_list ?
                values.append(row[1]) # topic_alpha
                values.append(0) # Place holder for total_tokens until XML file is handled
                values.append(row[2]) # topic_list
                cur.execute(self.insert_sql,values)
            conn.commit()
            cur.close()

    class DocTopicTable(Table):
        
        raw_fields = (('doc_id', 'TEXT'), ('doc_label', 'TEXT'), ('topic_entropy', 'REAL'), ('_topics_', 'REAL'))
        
        def __init__(self,z):
            Table.__init__(self,'doctopic',self.raw_fields,z)

        def import_src_data(self, conn):

            # This must handle different versions of MALLET
            
            self.create_table(conn)
            cur = conn.cursor()
            for line in self.src_data_iter():
                if re.match('^#',line):
                    continue
                values = []
                row = line.split('\t')
                info = row[1].split(',') 
                values.append(info[0]) # doc_id
                values.append(info[1]) # doc_label
                H = 0 # Entropy
                tws = [0 for i in range(int(self.z))]

                # Determine how many cols, since MALLET does it two ways ...
                # Shouldn't have to do this for each row, though
                # Should get the row lenght and calculate type once
                src_type = len(row) - 2
                
                # Type A -- Topic weights in order of topic number
                if (src_type == int(self.z)):
                    for i in range(2,int(self.z)):
                        tn = i
                        tw = float(row[i])
                        tws[tn] = tw
                        if tw != 0:
                            H += tw * log(tw)
                
                # Type B -- Topic weights in order to weight, with topic number paired
                elif (src_type == int(self.z) * 2):
                    for i in range(2,int(self.z)*2,2):
                        tn = int(row[i])
                        tw = float(row[i+1])
                        tws[tn] = tw
                        if tw != 0:
                            H += tw * log(tw)
                        
                values.append(-1 * H) # topic_entropy
                for tw in tws:
                    values.append(tw) # topic weights (t1 ... tn)
                    
                cur.execute(self.insert_sql,values)
            conn.commit()
            cur.close()
    
    class WordTopicTable(Table):
        
        raw_fields = (('word_id', 'INTEGER'), ('word_str', 'TEXT'), ('_topics_', 'INTEGER'),('word_sum','INTEGER'))
        
        def __init__(self,z):
            Table.__init__(self,'wordtopic',self.raw_fields,z)

        def import_src_data(self, conn):
            self.create_table(conn)
            cur = conn.cursor()
            for line in self.src_data_iter():
                values = []
                row = line.split(' ')
                values.append(row[0]) # word_id
                values.append(row[1]) # word_str
                counts = {} # word_counts
                word_sum = 0
                for x in row[2:]:
                    y = x.split(':') # y[0] = topic num, y[1] = word count
                    counts[str(y[0])] = y[1]
                for i in range(int(self.z)):
                    tn = str(i)
                    if tn in counts.keys():
                        word_sum += int(counts[tn])
                        values.append(counts[tn])
                    else:
                        values.append(0)
                values.append(word_sum)
                cur.execute(self.insert_sql,values)
            conn.commit()
            cur.close()

    class TopicPhraseTable(Table):
        
        raw_fields = (('topic_id', 'TEXT'), ('topic_phrase', 'TEXT'), ('phrase_count', 'INTEGER'), ('phrase_weight', 'REAL'))
        
        def __init__(self):
            Table.__init__(self,'topicphrase',self.raw_fields)

        def import_src_data(self, conn):
            self.create_table(conn)
            cur = conn.cursor()
            with open(self.src_file_path) as fd:
                tree = etree.parse(fd)
                for topic in tree.xpath('/topics/topic'):
                    topic_id = 't'+topic.xpath('@id')[0]
                    total_tokens = topic.xpath('@totalTokens')[0]
                    sql1 = "UPDATE topic SET total_tokens = ? WHERE topic_id = ?" # Risky
                    cur.execute(sql1,[total_tokens,topic_id])                            
                    for phrase in topic.xpath('phrase'):
                        values = []
                        phrase_weight = phrase.xpath('@weight')[0]
                        phrase_count = phrase.xpath('@count')[0]
                        topic_phrase = phrase.xpath('text()')[0]
                        values.append(topic_id)
                        values.append(topic_phrase)
                        values.append(phrase_count)
                        values.append(phrase_weight)
                        cur.execute(self.insert_sql,values)
            conn.commit()
            cur.close()
            
    class ConfigTable(Table):
        
        raw_fields = (('key','TEXT'),('value','TEXT'))        
        
        def __init__(self,mallet_interface):
            Table.__init__(self,'config',self.raw_fields)
            self.mallet_interface = mallet_interface

        def import_src_data(self, conn):
            self.create_table(conn)
            cur = conn.cursor()
            for k1 in self.mallet_interface.mallet:
                for k2 in self.mallet_interface.mallet[k1]:
                    key = re.sub('-', '_', 'mallet_{0}_{1}'.format(k1,k2))
                    val = self.mallet_interface.mallet[k1][k2]
                    cur.execute('INSERT INTO config VALUES (?,?)',[key,val])
            for k in self.mallet_interface.trial.cfg['DEFAULT']:
                cur.execute('INSERT INTO config VALUES (?,?)',['project_'+k, self.mallet_interface.trial.cfg['DEFAULT'][k]])
            conn.commit()
    
    def populate_model(self):
        with sqlite3.connect(self.dbfilename) as conn:
            for table in sorted(self.tables):
                self.tables[table].import_src_data(conn)
    
    def generate_dbfilename(self):
        iterations = self.trial_cfg['num-iterations']            
        self.dbfilename = '{0}/{1}-{2}-z{3}-i{4}.db'.format(self.trial.trial_path,self.trial.project,self.trial.trial,self.z,iterations)

if __name__ == '__main__':

    project_name  = 'demo'
    trial_name    = 'default'
    projects_path = 'projects'
    mallet_path   = '/usr/local/bin/mallet'
    
    t = PoloTrial(project_name,trial_name,mallet_path,projects_path)

    mi = MalletInterface(t)
    mi.mallet_import()
    mi.mallet_train()
    
    mm = MalletModel(mi)
    mm.generate_dbfilename()
    mm.populate_model()

    print(mm.dbfilename)
    


