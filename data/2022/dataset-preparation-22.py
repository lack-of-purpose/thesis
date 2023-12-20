import pandas as pd
import random
import os
import csv
from collections import defaultdict


def main(score, translation):
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
        if not os.path.isdir(f'{dirpath}/filtered-by-score'):
            os.mkdir(f'{dirpath}/filtered-by-score')
        filtered = df[df['score']>=score]
        filtered.to_csv(f'{dirpath}/filtered-by-score/en_{lang}_22_{score}.csv')
        
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
        #all_best_lines = open(f'{dirpath}/best-lines-22/all-best-lines-{lang}-22.txt', 'w')
        best_lines_mt = open(f'{dirpath}/best-lines-22/best-lines-{lang}-22-mt.csv', 'w', newline='')
        best_lines_human = open(f'{dirpath}/best-lines-22/best-lines-{lang}-22-human.csv', 'w', newline='')
        header = ['num', 'sys']
        mt_writer = csv.writer(best_lines_mt)
        mt_writer.writerow(header)
        human_writer = csv.writer(best_lines_human)
        human_writer.writerow(header)
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
            
            for sent in sorted(valid_sentences):
                #sent = str(sent) + ',' + sys
                row = []
                row.append(str(sent))
                row.append(sys)
                if sys.startswith('translator'):
                    human_writer.writerow(row)
                else:
                    mt_writer.writerow(row)
                #all_best_lines.write("%s\n" % sent)
                
        best_lines_mt.close()
        best_lines_human.close()
        '''
        best = pd.read_csv(f'{dirpath}/best-lines-22/best-lines-{lang}-22-mt.csv', names=['num', 'sys'], header=None)
        best = best.sort_values(by=['num'])
        best.to_csv(f'{dirpath}/best-lines-22/best-lines-{lang}-22-mt.csv')
        
        best = pd.read_csv(f'{dirpath}/best-lines-22/best-lines-{lang}-22-human.csv', names=['num', 'sys'], header=None)
        best = best.sort_values(by=['num'])
        best.to_csv(f'{dirpath}/best-lines-22/best-lines-{lang}-22-human.csv')
        
        
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
                #rand_sent = random.choice(line_choice_mt)
                for rand_sent in line_choice_mt:
                    mt_final_dataset_lines.append(rand_sent)
            
            if len(line_choice_human) != 0:
                #rand_sent = random.choice(line_choice_human)
                for rand_sent in line_choice_human:
                    human_final_dataset_lines.append(rand_sent)
                
        print(len(mt_final_dataset_lines))
        print(len(human_final_dataset_lines))
        
        '''
        src = defaultdict()
        best_lines_mt = open(f'{dirpath}/best-lines-22/best-lines-{lang}-22-mt.csv', 'r')
        best_lines_human = open(f'{dirpath}/best-lines-22/best-lines-{lang}-22-human.csv', 'r')
        sources = open(f'{dirpath}/sources/generaltest2022.en-{lang}.src.en.txt', 'r', encoding='UTF-8')
        source_sents = sources.readlines()
        mt_reader = csv.reader(best_lines_mt, delimiter=',')
        human_reader = csv.reader(best_lines_human, delimiter=',')
        mt = defaultdict(set)
        for row in mt_reader:
            if row[0] ==  'num':
                continue
            sys_output = open(f'{dirpath}/en-{lang}-22/generaltest2022.en-{lang}.hyp.{row[1]}.{lang}.txt', 'r', encoding='UTF-8')
            sents = sys_output.readlines()
            if row[0] in mt.keys():
                mt[row[0]].add(sents[int(row[0])-1].strip())
            else:
                mt[row[0]] = set()
                mt[row[0]].add(sents[int(row[0])-1].strip())
            if not row[0] in src.keys():
                src[row[0]] = source_sents[int(row[0])-1].strip()
            sys_output.close()
        
        human = defaultdict(set)
        for row in human_reader:
            if row[0] ==  'num':
                continue
            if row[1] == 'translator-C':
                sys_name = 'refC'
            if row[1] == 'translator-B':
                sys_name = 'refB'
            if row[1] == 'translator-A':
                sys_name = 'refA'
            sys_output = open(f'{dirpath}/en-{lang}-22/generaltest2022.en-{lang}.ref.{sys_name}.{lang}.txt', 'r', encoding='UTF-8')
            sents = sys_output.readlines()
            if row[0] in human.keys():
                human[row[0]].add(sents[int(row[0])-1].strip())
            else:
                human[row[0]] = set()
                human[row[0]].add(sents[int(row[0])-1].strip())
            if not row[0] in src.keys():
                src[row[0]] = source_sents[int(row[0])-1].strip()
            sys_output.close()
        
        '''
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
        '''
        
        #construct final dataset
        if not os.path.isdir(f'{dirpath}/mt'):
            os.mkdir(f'{dirpath}/mt')
        if not os.path.isdir(f'{dirpath}/human'):
            os.mkdir(f'{dirpath}/human')
        final_mt_dataset = open(f'{dirpath}/mt/mt-dataset-22-{lang}-{score}-{translation}.txt', 'w', encoding='UTF-8')
        final_human_dataset = open(f'{dirpath}//human/human-dataset-22-{lang}-{score}-{translation}.txt', 'w', encoding='UTF-8')
        
        for key in mt.keys():
            sentences = list(mt[key])
            source =  src[key]
            for sent in sentences:
                line = source + '|' + sent + '|mt'
                final_mt_dataset.write("%s\n" % line)
                
        for key in human.keys():
            sentences = list(human[key])
            source =  src[key]
            for sent in sentences:
                line = source + '|' + sent + '|human'
                final_human_dataset.write("%s\n" % line)
        '''
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
        '''
               
        final_mt_dataset.close()
        final_human_dataset.close()
    
if __name__ == "__main__":
    main(95, 'src-tgt')