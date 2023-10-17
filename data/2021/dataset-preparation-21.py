import pandas as pd
import random
import os

dirpath = os.path.dirname(__file__)

column_names =['userId', 'sys', 'segId', 'Q', 'src', 'tgt', 'score', 'docId', 'whole_doc', 'start', 'end']
wmt21 = pd.read_csv(f'{dirpath}/wmt21.csv', names=column_names, header=None)

en_cs = wmt21[(wmt21['Q']=='TGT')&(wmt21['src']=='eng')&(wmt21['tgt']=='ces')]
en_cs.to_csv(f'{dirpath}/eng_ces21.csv')

en_ru = wmt21[(wmt21['Q']=='TGT')&(wmt21['src']=='eng')&(wmt21['tgt']=='rus')]
en_ru.to_csv(f'{dirpath}/eng_rus21.csv')

for lang in ['cs', 'ru']:
    if lang  == 'cs':
        df = pd.read_csv(f'{dirpath}/eng_ces21.csv')
    else: df = pd.read_csv(f'{dirpath}/eng_rus21.csv')
    # filter by score value (>=98)
    filtered = df[df['score']>=98]
    filtered.to_csv(f'{dirpath}/en_{lang}_21_98.csv')
    filtered['segId'] = filtered['segId'].astype(str)
    
    meta = pd.read_csv(f'{dirpath}/metadata/newstest2021.en-{lang}.csv', sep='\t')
    meta['num'] = range(1, len(meta) + 1)
    
    systems = filtered['sys'].unique()
    if not os.path.isdir(f'{dirpath}/best-lines-21'):
        os.mkdir(f'{dirpath}/best-lines-21')
    all_best_lines = open(f'{dirpath}/best-lines-21/all-best-lines-{lang}-21.txt', 'w')
    for sys in systems:
        if sys.startswith('NVIDIA'):
            continue
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
                    line = meta.loc[(meta['document'] == key) & (meta['segment'] == int(item))]['num']
                    valid_sentences.append(line._values[0])
        sorted(valid_sentences)
        
        for sent in sorted(valid_sentences):
            sent = str(sent) + ',' + sys
            all_best_lines.write("%s\n" % sent)
            
    all_best_lines.close()
    
    mt_final_dataset_lines = []
    human_final_dataset_lines = []
    all_best_lines = open(f'{dirpath}/best-lines-21/all-best-lines-{lang}-21.txt', 'r')
    lines = all_best_lines.readlines()
    for i in range(1,1003):
        line_choice_mt = []
        line_choice_human = []
        for line in lines:
            line = line.strip()
            line_parts = line.split(',')
            if line_parts[0] == str(i):
                if line_parts[1] == 'translator-B':
                    if lang == 'cs':
                        continue
                    else: line_choice_human.append(line)
                elif line_parts[1] == 'translator-A':
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
            
    final_mt_dataset = open(f'{dirpath}/mt-dataset-21-{lang}.txt', 'w', encoding='UTF-8')
    final_human_dataset = open(f'{dirpath}/human-dataset-21-{lang}.txt', 'w', encoding='UTF-8')


    for sys in sys_sents_mt.keys():
        sys_output = open(f'{dirpath}/en-{lang}-21/newstest2021.en-{lang}.hyp.{sys}.{lang}.txt', 'r', encoding='UTF-8')
        sents = sys_output.readlines()
        for num in sys_sents_mt[sys]:
            sent = sents[num-1].strip()
            sent = sent + '|mt'
            final_mt_dataset.write("%s\n" % sent)

    for sys in sys_sents_human.keys():
        if sys == 'translator-A':
            sys_name = 'ref-A'
        if sys == 'translator-B':
            sys_name = 'ref-B'
        sys_output = open(f'{dirpath}/en-{lang}-21/newstest2021.en-{lang}.ref.{sys_name}.{lang}.txt', 'r', encoding='UTF-8')
        sents = sys_output.readlines()
        for num in sys_sents_human[sys]:
            sent = sents[num-1].strip()
            sent = sent + '|human'
            final_human_dataset.write("%s\n" % sent)
            
    final_mt_dataset.close()
    final_human_dataset.close()