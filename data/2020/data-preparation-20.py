import pandas as pd
import random
import os
import csv
from collections import defaultdict

def main(score, translation):
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
        if not os.path.isdir(f'{dirpath}/filtered-by-score'):
            os.mkdir(f'{dirpath}/filtered-by-score')
        filtered = wmt20[wmt20['RAW.SCR']>=score]
        filtered.to_csv(f'{dirpath}/filtered-by-score/en_{lang}_20_{score}.csv')
        meta = pd.read_csv(f'{dirpath}/metadata/en-{lang}.csv', sep='\t', names=['num', 'test', 'langpair', 'doc', 'seg'])
        
        systems = filtered['SYS'].unique()
        if not os.path.isdir(f'{dirpath}/best-lines-20'):
            os.mkdir(f'{dirpath}/best-lines-20')
        #all_best_lines = open(f'{dirpath}/best-lines-20/all-best-lines-{lang}-20.txt', 'w')
        best_lines_mt = open(f'{dirpath}/best-lines-20/best-lines-{lang}-20-mt.csv', 'w', newline='')
        best_lines_human = open(f'{dirpath}/best-lines-20/best-lines-{lang}-20-human.csv', 'w', newline='')
        header = ['num', 'sys']
        mt_writer = csv.writer(best_lines_mt)
        mt_writer.writerow(header)
        human_writer = csv.writer(best_lines_human)
        human_writer.writerow(header)
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
            
            for sent in sorted(valid_sentences):
                #sent = str(sent) + ',' + sys
                row = []
                row.append(str(sent))
                row.append(sys)
                if sys == 'HUMAN':
                    human_writer.writerow(row)
                else:
                    mt_writer.writerow(row)
                #all_best_lines.write("%s\n" % sent)
        best_lines_mt.close()
        best_lines_human.close()      
        #all_best_lines.close()
        '''
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
        '''
        src = defaultdict()
        best_lines_mt = open(f'{dirpath}/best-lines-20/best-lines-{lang}-20-mt.csv', 'r')
        best_lines_human = open(f'{dirpath}/best-lines-20/best-lines-{lang}-20-human.csv', 'r')
        sources = open(f'{dirpath}/sources/newstest2020-en{lang}-src.en.txt', 'r', encoding='UTF-8')
        source_sents = sources.readlines()
        mt_reader = csv.reader(best_lines_mt, delimiter=',')
        human_reader = csv.reader(best_lines_human, delimiter=',')
        mt = defaultdict(set)
        for row in mt_reader:
            if row[0] ==  'num':
                continue
            sys_output = open(f'{dirpath}/en-{lang}-20/newstest2020.en-{lang}.{row[1]}.txt', 'r', encoding='UTF-8')
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
            sys_output = open(f'{dirpath}/en-{lang}-20/newstest2020-en{lang}-ref.{lang}.txt', 'r', encoding='UTF-8')
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
        if not os.path.isdir(f'{dirpath}/mt'):
            os.mkdir(f'{dirpath}/mt')
        if not os.path.isdir(f'{dirpath}/human'):
            os.mkdir(f'{dirpath}/human')     
        final_mt_dataset = open(f'{dirpath}/mt/mt-dataset-20-{lang}-{score}-{translation}.txt', 'w', encoding='UTF-8')
        final_human_dataset = open(f'{dirpath}/human/human-dataset-20-{lang}-{score}-{translation}.txt', 'w', encoding='UTF-8')
        
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
        '''
              
        final_mt_dataset.close()
        final_human_dataset.close()
        
if __name__ == "__main__":
    main(95, 'src-tgt')