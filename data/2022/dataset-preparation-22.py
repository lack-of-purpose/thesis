import pandas as pd
import random
import os

dirpath = os.path.dirname(__file__)

column_names =['userId', 'sys', 'segId', 'Q', 'src', 'tgt', 'score', 'docId', 'whole_doc', 'start', 'end']
wmt22 = pd.read_csv(f'{dirpath}/WMT22.csv', names=column_names, header=None)

en_cs = wmt22[(wmt22['Q']=='TGT')&(wmt22['src']=='eng')&(wmt22['tgt']=='ces')]
en_cs.to_csv(f'{dirpath}/eng_ces22.csv')

en_ru = wmt22[(wmt22['Q']=='TGT')&(wmt22['src']=='eng')&(wmt22['tgt']=='rus')]
en_ru.to_csv(f'{dirpath}/eng_rus22.csv')

for lang in ['cs', 'ru']:
    if lang  == 'cs':
        df = pd.read_csv(f'{dirpath}/eng_ces22.csv')
    else: df = pd.read_csv(f'{dirpath}/eng_rus22.csv')
    # filter by score value (>=98)
    filtered = df[df['score']>=98]
    filtered.to_csv(f'{dirpath}/en_{lang}_22_98.csv')
    
    # process metadata
    meta = pd.read_csv(f'{dirpath}/metadata/en-{lang}.csv', sep='\t', names=['type', 'doc'], header=None)
    meta['num'] = range(1, len(meta) + 1)
    meta['local_index'] = 0
    i = 1
    doc = meta.at[0, 'doc']
    for index, row in meta.iterrows():
        if row['doc'] == doc:
            meta.at[index, 'local_index'] = i
        else:
            doc = row['doc']
            i = 1
            meta.at[index, 'local_index'] = i
        i += 1
    
    #group sentences by translation system 
    systems = filtered['sys'].unique()
    if not os.path.isdir(f'{dirpath}/best-lines-22'):
        os.mkdir(f'{dirpath}/best-lines-22')
    all_best_lines = open(f'{dirpath}/best-lines-22/all-best-lines-{lang}-22.txt', 'w')
    for sys in systems:
        temp = filtered[filtered['sys']==sys]
        docs = temp['docId'].unique()
        doc_sent = {}
        for doc in docs:
            lines = set()
            doc_lines = temp.loc[temp['docId'] == doc, 'segId']
            doc_lines.columns =['n', 'idx']
            doc_lines = doc_lines.to_frame()
            for index, row in doc_lines.iterrows():
                lines.add(row['segId'])
            doc_sent[doc] = lines
    
        for key in doc_sent.keys():
            doc_sent[key] = list(doc_sent[key])
        
        valid_sentences = []
        for key in doc_sent.keys():
            for item in doc_sent[key]:
                if not '-' in item and item != '0':
                    line = meta.loc[(meta['doc'] == key) & (meta['local_index'] == int(item))]['num']
                    valid_sentences.append(line._values[0])
        sorted(valid_sentences)
        
        for sent in sorted(valid_sentences):
            sent = str(sent) + ',' + sys
            all_best_lines.write("%s\n" % sent)
    
    #line numbers for final dataset
    mt_final_dataset_lines = []
    human_final_dataset_lines = []
    all_best_lines = open(f'{dirpath}/best-lines-22/all-best-lines-{lang}-22.txt', 'r')
    lines = all_best_lines.readlines()
    for i in range(1,2038):
        line_choice_mt = []
        line_choice_human = []
        for line in lines:
            line = line.strip()
            line_parts = line.split(',')
            if line_parts[0] == str(i):
                if line_parts[1].startswith('translator'):
                    line_choice_human.append(line)
                else:
                    line_choice_mt.append(line)
        if len(line_choice_mt) != 0:
            rand_sent = random.choice(line_choice_mt)
            mt_final_dataset_lines.append(rand_sent)
        
        if len(line_choice_human) != 0:
            rand_sent = random.choice(line_choice_human)
            human_final_dataset_lines.append(rand_sent)
            
    print(len(mt_final_dataset_lines))
    print(len(human_final_dataset_lines))

    sys_sents_mt = {}
    for line in mt_final_dataset_lines:
        line = line.strip()
        line_parts = line.split(',')
        if line_parts[1] in sys_sents_mt.keys():
            sys_sents_mt[line_parts[1]].append(int(line_parts[0]))
        else:
            sys_sents_mt[line_parts[1]] = [int(line_parts[0])]

    sys_sents_human = {}
    for line in human_final_dataset_lines:
        line = line.strip()
        line_parts = line.split(',')
        if line_parts[1] in sys_sents_human.keys():
            sys_sents_human[line_parts[1]].append(int(line_parts[0]))
        else:
            sys_sents_human[line_parts[1]] = [int(line_parts[0])]
    
    #construct final dataset
    final_mt_dataset = open(f'{dirpath}/mt-dataset-22-{lang}.txt', 'w', encoding='UTF-8')
    final_human_dataset = open(f'{dirpath}/human-dataset-22-{lang}.txt', 'w', encoding='UTF-8')
    

    for sys in sys_sents_mt.keys():
        sys_output = open(f'{dirpath}/en-{lang}-22/generaltest2022.en-{lang}.hyp.{sys}.{lang}.txt', 'r', encoding='UTF-8')
        sents = sys_output.readlines()
        for num in sys_sents_mt[sys]:
            sent = sents[num-1].strip()
            sent = sent + '|mt'
            final_mt_dataset.write("%s\n" % sent)

    for sys in sys_sents_human.keys():
        if sys == 'translator-C':
            sys_name = 'refC'
        if sys == 'translator-B':
            sys_name = 'refB'
        if sys == 'translator-A':
            sys_name = 'refA'
        sys_output = open(f'{dirpath}/en-{lang}-22/generaltest2022.en-{lang}.ref.{sys_name}.{lang}.txt', 'r', encoding='UTF-8')
        sents = sys_output.readlines()
        for num in sys_sents_human[sys]:
            sent = sents[num-1].strip()
            sent = sent + '|human'
            final_human_dataset.write("%s\n" % sent)
            
    final_mt_dataset.close()
    final_human_dataset.close()