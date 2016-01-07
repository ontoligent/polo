import os, re, configparser, sqlite3, codecs
from collections import OrderedDict
from lxml import etree
from math import log

class Mallet:
    
    # The data model
    tbl_defs = {}
    tbl_defs['doc'] = OrderedDict([('doc_id', 'TEXT'), ('doc_label', 'TEXT'), ('doc_content', 'TEXT')])
    tbl_defs['topic'] = OrderedDict([('topic_id', 'TEXT'), ('topic_alpha', 'REAL'), ('total_tokens', 'INTEGER'), ('topic_words', 'TEXT')])
    tbl_defs['doctopic'] = OrderedDict([('doc_id', 'TEXT'), ('doc_label', 'TEXT'), ('topic_entropy', 'REAL'), ('_topics_', 'REAL')])
    tbl_defs['wordtopic'] = OrderedDict([('word_id', 'INTEGER'), ('word_str', 'TEXT'), ('_topics_', 'INTEGER')])
    tbl_defs['topicphrase'] = OrderedDict([('topic_id', 'TEXT'), ('topic_phrase', 'TEXT'), ('phrase_count', 'INTEGER'), ('phrase_weight', 'REAL')])
    #tbl_defs['topicword'] = OrderedDict([('word_str','TEXT'),('_topics_','REAL')])

    def __init__(self,project,trial,mallet_path,projects_path='projects'):
        self.project = project
        self.trial = trial
        self.project_path = '%s/%s' % (projects_path, self.project)
        self.trial_path = '%s/trials/%s' % (self.project_path,self.trial)
        self.mallet_path = mallet_path
        self.verbose = False
        self.import_config()
        self.mallet_init()

    def import_config(self):
        cfg_file = '%s/config.ini' % self.project_path
        if os.path.exists(cfg_file):
            self.cfg = configparser.ConfigParser()
            self.cfg.read(cfg_file)
            return 1
        else:
            return 0

    def mallet_init(self):
        self.mallet = {'import-file':{}, 'train-topics':{}}
        self.mallet['import-file']['extra-stopwords'] = '%s/corpus/extra-stopwords.txt' % self.project_path
        self.mallet['import-file']['input'] = '%s/corpus/corpus.csv' % self.project_path
        self.mallet['import-file']['output'] = '%s/corpus.mallet' % self.trial_path
        self.mallet['import-file']['keep-sequence'] = '' # Delete key to remove option
        self.mallet['import-file']['remove-stopwords'] = '' # Delete key to remove option
        self.mallet['train-topics']['num-topics'] = 40 # default
        self.mallet['train-topics']['num-top-words'] = 7 # default
        self.mallet['train-topics']['num-iterations'] = 100 # default
        self.mallet['train-topics']['optimize-interval'] = 10 # default
        self.mallet['train-topics']['num-threads'] = 1 # default
        self.mallet['train-topics']['input'] = self.mallet['import-file']['output']
        self.mallet['train-topics']['output-topic-keys'] = '%s/model-topic-keys.txt' % self.trial_path
        self.mallet['train-topics']['output-doc-topics'] = '%s/model-doc-topics.txt' % self.trial_path
        self.mallet['train-topics']['word-topic-counts-file'] = '%s/model-word-topic-counts.txt' % self.trial_path
        self.mallet['train-topics']['xml-topic-report'] = '%s/model-topic-report.xml' % self.trial_path
        self.mallet['train-topics']['xml-topic-phrase-report'] = '%s/model-topic-phrase-report.xml' % self.trial_path
        #self.mallet['train-topics']['topic-word-weights-file'] = '%s/model-topic-word-weights.txt' % self.trial_path

        # Override values if found in the config file for the trial
        user_args = ['num-topics','num-top-words','num-iterations','optimize-interval','num-threads']
        for arg in user_args:
            if self.cfg[self.trial][arg]:
                self.mallet['train-topics'][arg] = self.cfg[self.trial][arg]

    def mallet_run_command(self,op):
        my_cmd = '{0} {1}'.format(self.mallet_path, op)
        my_args = ['--{0} {1}'.format(arg,self.mallet[op][arg]) for arg in self.mallet[op]]
        self.cmd_response = os.system('{0} {1}'.format(my_cmd, ' '.join(my_args)))
        
    def mallet_import(self):
        self.mallet_run_command('import-file')

    def mallet_train(self):
        self.mallet_run_command('train-topics')

    def create_table_defs(self):
        z = self.mallet['train-topics']['num-topics']        
        self.tbl_sql = {}   
        for table in Mallet.tbl_defs:
            self.tbl_sql[table] = "CREATE TABLE IF NOT EXISTS %s (" % table
            fields = []
            for field, ftype in Mallet.tbl_defs[table].items():
                if field == '_topics_':
                    for x in range(int(z)):
                        fields.append('t%s %s' % (x,ftype))
                else:
                    fields.append("'%s' %s" % (field,ftype))
            self.tbl_sql[table] += ','.join(fields)
            self.tbl_sql[table] += ")"

    def generate_dbfilename(self):
        z = self.mallet['train-topics']['num-topics']
        iterations = self.mallet['train-topics']['num-iterations']            
        return '{0}/{1}-{2}-z{3}-i{4}.db'.format(self.trial_path,self.project,self.trial,z,iterations)

    def import_model(self):
        z = self.mallet['train-topics']['num-topics']

        srcfiles = {'csv': {}, 'xml': {}}
        srcfiles['csv']['doc'] = self.mallet['import-file']['input']
        srcfiles['csv']['topic'] = self.mallet['train-topics']['output-topic-keys']
        srcfiles['csv']['doctopic'] = self.mallet['train-topics']['output-doc-topics']
        srcfiles['csv']['wordtopic'] = self.mallet['train-topics']['word-topic-counts-file']
        srcfiles['xml']['topicphrase'] = self.mallet['train-topics']['xml-topic-phrase-report']
        #srcfiles['csv']['topicword'] = self.mallet['train-topics']['topic-word-weights-file']
        
        dbfile = self.generate_dbfilename()
        with sqlite3.connect(dbfile) as conn:
            cur = conn.cursor()

            # Create a table for the config data
            cur.execute('DROP TABLE IF EXISTS config')
            cur.execute('CREATE TABLE config (key TEXT, value TEXT)')
            conn.commit()
            for k1 in self.mallet:
                for k2 in self.mallet[k1]:
                    k = re.sub('-', '_', 'mallet_{0}_{1}'.format(k1,k2))
                    v = self.mallet[k1][k2]
                    cur.execute('INSERT INTO config VALUES (?,?)',[k,v])
            for k in self.cfg['DEFAULT']:
                cur.execute('INSERT INTO config VALUES (?,?)',['project_'+k, self.cfg['DEFAULT'][k]])
            conn.commit()
                    
            # Import the CSV files
            for table in srcfiles['csv']:
                if self.verbose: print('HEY Loading table',table)

                # Drop or truncate the table
                cur.execute('DROP TABLE IF EXISTS %s' % table)
                cur.execute(self.tbl_sql[table])
                conn.commit()
                
                # Open the source file
                src_file = srcfiles['csv'][table]
                with codecs.open(src_file, 'r', encoding='utf-8', errors='ignore') as src_data:
                #with open(src_file,'r') as src_data:
                    if self.verbose: print('HEY Loading csv file',src_file)
                
                    # Handle special case of topicword
                    '''
                    if table == 'topicword':
                        weights = {}
                        field_str = 'word_str,' + ','.join(['t{0}'.format(i) for i in range(int(z))])
                        for line in src_data.readlines():
                            row = line.strip().split('\t')
                            #topic_id = 't'+row[0] # Not used; instead we use order of topics in src file
                            word_str = row[1]
                            word_wgt = row[2]
                            if word_str not in weights.keys():
                                weights[word_str] = []
                            weights[word_str].append(word_wgt)
                        for word_str in weights.keys():
                            sql = "INSERT INTO topicword (%s) VALUES ('%s',%s)" % (field_str,word_str,','.join(weights[word_str]))
                            cur.execute(sql)
                        conn.commit() # Do this outside of preceding for loop
                        continue
                    '''
    
                    # Create the field_str for use in the SQL statement
                    fields = []
                    for field, ftype in Mallet.tbl_defs[table].items():
                        if field == '_topics_':
                            for i in range(int(z)):
                                fields.append('t'+str(i))
                        else:
                            fields.append(field)
                    field_str = ','.join(fields)

                    if self.verbose: print('HEY Creating table with fields:',field_str)
                        
                    # Generate the value string, then insert
                    for line in src_data.readlines():
                        if (re.match('^#',line)):
                            continue
                        line = line.strip()
                        values = [] # Used to create the value_str in the SQL statement
    		
                        if table == 'doctopic':
                            row = line.split('\t')
                            info = row[1].split(',') 
                            values.append(info[0]) # doc_id
                            values.append(info[1]) # doc_label
                            H = 0 # Entropy
                            tws = [0 for i in range(int(z))]
                            for i in range(2,int(z)*2,2): 
                                tn = int(row[int(i)])
                                tw = float(row[int(i)+1])
                                tws[tn] = tw
                                if tw != 0:
                                    H += tw * log(tw)
                            values.append(-1 * H) # topic_entropy
                            for tw in tws:
                                values.append(tw) # topic weights (t1 ... tn)
    		
                        elif table == 'wordtopic':
                            row = line.split(' ')
                            values.append(row[0]) # word_id
                            values.append(row[1]) # word_str
                            counts = {} # word_counts
                            for x in row[2:]:
                                y = x.split(':') # y[0] = topic num, y[1] = word count
                                counts[str(y[0])] = y[1]
                            for i in range(int(z)):
                                tn = str(i)
                                if tn in counts.keys(): values.append(counts[tn])
                                else: values.append(0)
    
                        elif table == 'topic':
                            row = line.split('\t')
                            values.append('t%s' % row[0]) # topic_id
                            values.append(row[1]) # topic_alpha
                            values.append(0) # Place holder for total_tokens until XML file is handled
                            values.append(row[2]) # topic_list

                        #elif table == 'topicword':
                        #    continue # This is handled above
                            
                        elif table == 'doc':
                            row = line.split(',')
                            values.append(row[0]) # doc_id
                            values.append(row[1]) # doc_label
                            values.append(row[2]) # doc_content
                        
                        arg_str = ','.join(['?' for _ in range(len(values))])
                        sql2 = 'INSERT INTO `{0}` ({1}) VALUES ({2})'.format(table,field_str,arg_str)
                        cur.execute(sql2,values)
    		
                    conn.commit() # Commit after each table
            
            for table in srcfiles['xml']:
                if self.verbose: print('HEY Loading table',table)
                if table == 'topicphrase':
                    cur.execute('DROP TABLE IF EXISTS %s' % table)
                    cur.execute(self.tbl_sql[table])
                    conn.commit()
                    src_file = srcfiles['xml'][table]
                    with open(src_file) as fd:
                        if self.verbose: print('HEY Parsing xml file', src_file)
                        tree = etree.parse(fd)
                        for topic in tree.xpath('/topics/topic'):
                            topic_id = 't'+topic.xpath('@id')[0]
                            total_tokens = topic.xpath('@totalTokens')[0]
                            sql1 = "UPDATE topic SET total_tokens = ? WHERE topic_id = ?"
                            cur.execute(sql1,[total_tokens,topic_id])                            
                            for phrase in topic.xpath('phrase'):
                                phrase_weight = phrase.xpath('@weight')[0]
                                phrase_count = phrase.xpath('@count')[0]
                                topic_phrase = phrase.xpath('text()')[0]
                                sql2 = 'INSERT INTO topicphrase (topic_id,topic_phrase,phrase_count,phrase_weight) VALUES (?,?,?,?)'
                                cur.execute(sql2,[topic_id,topic_phrase,phrase_count,phrase_weight])        
                conn.commit()
                                    
            cur.close()
        return 1

if __name__ == '__main__':

    print('Welcome to Polo. This is the Mallet class, which makes it easy to run mallet. Try play to use it.')
