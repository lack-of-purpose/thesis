import pandas as pd
import random
import os

dirpath = os.path.dirname(__file__)

for lang in ['cs', 'ru']:
    wmt20 = pd.read_csv(f'{dirpath}/wmt20-en-{lang}.csv', sep=' ')
    wmt20['DOC'] = ''
    for index, row in wmt20.iterrows():
        parts = row['SID'].split('_')
        if len(parts) != 2:
            sid = parts[-1]
            doc = ''
            for part in parts[:-1]:
                doc = doc + part
            wmt20.loc[index, 'SID'] = sid
            wmt20.loc[index, 'DOC'] = doc
        else:
            wmt20.loc[index, 'SID'] = parts[1]
            wmt20.loc[index, 'DOC'] = parts[0]
    filtered = wmt20[wmt20['RAW.SCR']>=98]
    filtered.to_csv(f'{dirpath}/en_{lang}_20_98.csv')
    meta = pd.read_csv(f'{dirpath}/metadata/en-{lang}.csv', sep='\t', names=['num', 'test', 'langpair', 'doc', 'seg'])
    
    systems = filtered['SYS'].unique()
    if not os.path.isdir(f'{dirpath}/best-lines-20'):
        os.mkdir(f'{dirpath}/best-lines-20')
    all_best_lines = open(f'{dirpath}/best-lines-20/all-best-lines-{lang}-20.txt', 'w')
    for sys in systems:
        temp = filtered[filtered['SYS']==sys]
        docs = temp['DOC'].unique()
        doc_sent = {}
        for doc in docs:
            lines = set()
            doc_lines = temp.loc[temp['DOC'] == doc, 'SID']
            doc_lines.columns =['n', 'idx']
            doc_lines = doc_lines.to_frame()
            for index, row in doc_lines.iterrows():
                lines.add(row['SID'])
            doc_sent[doc] = lines

        for key in doc_sent.keys():
            doc_sent[key] = list(doc_sent[key])
        
        valid_sentences = []
        for key in doc_sent.keys():
            for item in doc_sent[key]:
                if not '-' in item and item != '0':
                    line = meta.loc[(meta['doc'] == key) & (meta['seg'] == int(item))]['num']
                    if len(line._values) != 0:
                        valid_sentences.append(line._values[0])
        sorted(valid_sentences)
        
        for sent in sorted(valid_sentences):
            sent = str(sent) + ',' + sys
            all_best_lines.write("%s\n" % sent)
            
    all_best_lines.close()
    
    mt_final_dataset_lines = []
    human_final_dataset_lines = []
    all_best_lines = open(f'{dirpath}/best-lines-20/all-best-lines-{lang}-20.txt', 'r')
    lines = all_best_lines.readlines()
    for i in range(1,1419):
        line_choice_mt = []
        line_choice_human = []
        for line in lines:
            line = line.strip()
            line_parts = line.split(',')
            if line_parts[0] == str(i):
                if line_parts[1] == 'HUMAN':
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
            
    final_mt_dataset = open(f'{dirpath}/mt-dataset-20-{lang}.txt', 'w', encoding='UTF-8')
    final_human_dataset = open(f'{dirpath}/human-dataset-20-{lang}.txt', 'w', encoding='UTF-8')


    for sys in sys_sents_mt.keys():
        sys_output = open(f'{dirpath}/en-{lang}-20/newstest2020.en-{lang}.{sys}.txt', 'r', encoding='UTF-8')
        sents = sys_output.readlines()
        for num in sys_sents_mt[sys]:
            sent = sents[num-1].strip()
            sent = sent + '|mt'
            final_mt_dataset.write("%s\n" % sent)

    for sys in sys_sents_human.keys():
        sys_output = open(f'{dirpath}/en-{lang}-20/newstest2020-en{lang}-ref.{lang}.txt', 'r', encoding='UTF-8')
        sents = sys_output.readlines()
        for num in sys_sents_human[sys]:
            sent = sents[num-1].strip()
            sent = sent + '|human'
            final_human_dataset.write("%s\n" % sent)
            
    final_mt_dataset.close()
    final_human_dataset.close()