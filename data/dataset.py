import random
import os
import csv

dirpath = os.path.dirname(__file__)

def create_csv(name, data, lang, score, translation):
    file = open(f'{dirpath}/{name}/{name}-{lang}-{score}-{translation}.csv', 'w', encoding='UTF-8', newline='')
    if translation == 'src-tgt':
        header = ['source', 'target', 'labels']
    else:
        header = ['sentence', 'labels']
    writer = csv.writer(file, delimiter ='|')
    writer.writerow(header)
    for line in data:
        row = []
        for part in line.split('|'):
            row.append(part)
        writer.writerow(row)

    file.close()

def combine_shuffle_split(train_human, train_mt, val_human, val_mt, test_human, test_mt):
    '''
    #mt
    for i in range(0,len(mt)):
        mt[i] = mt[i].strip()
    test_mt_len = round(len(mt) * 0.2)

    test_mt = mt[:test_mt_len]
    rest_mt = mt[test_mt_len:]

    val_mt_len = round(len(rest_mt) * 0.2)
    val_mt = rest_mt[:val_mt_len]
    train_mt = rest_mt[val_mt_len:]

    
    #human
    for i in range(0,len(human)):
        human[i] = human[i].strip()
    test_human_len = round(len(human) * 0.2)

    test_human = human[:test_human_len]
    rest_human = human[test_human_len:]

    val_human_len = round(len(rest_human) * 0.2)

    val_human = rest_human[:val_human_len]
    train_human = rest_human[val_human_len:]
    '''
    dataset_train = train_human + train_mt
    dataset_val = val_human + val_mt
    dataset_test = test_human + test_mt
    
    for i in range(0,len(dataset_train)):
        dataset_train[i] = dataset_train[i].strip()
    random.shuffle(dataset_train)
    
    for i in range(0,len(dataset_val)):
        dataset_val[i] = dataset_val[i].strip()
    random.shuffle(dataset_val)
    
    for i in range(0,len(dataset_test)):
        dataset_test[i] = dataset_test[i].strip()
    random.shuffle(dataset_test)
    
    return dataset_train, dataset_test, dataset_val

def split(data):
    test_len = round(len(data) * 0.2)
    test = data[:test_len]
    rest = data[test_len:]

    val_len = round(len(rest) * 0.2)
    val = rest[:val_len]
    train = rest[val_len:]
    
    return train, val, test

def concat_shuffle_clean(list_of_parts):
    dataset = []
    for part in list_of_parts:
        dataset += part
    random.shuffle(dataset)
    temp = set()
    for line in dataset:
        temp.add(line)
    dataset = list(temp)
    
    return dataset

def main(score, translation):
    #human
    
    human_cs_22 = open(f'{dirpath}/2022/human/human-dataset-22-cs-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()
    human_ru_22 = open(f'{dirpath}/2022/human/human-dataset-22-ru-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()

    human_cs_21 = open(f'{dirpath}/2021/human/human-dataset-21-cs-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()
    human_ru_21 = open(f'{dirpath}/2021/human/human-dataset-21-ru-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()

    human_cs_20 = open(f'{dirpath}/2020/human/human-dataset-20-cs-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()
    human_ru_20 = open(f'{dirpath}/2020/human/human-dataset-20-ru-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()
    
    train_cs_22, val_cs_22, test_cs_22 = split(human_cs_22)
    train_ru_22, val_ru_22, test_ru_22 = split(human_ru_22)
    train_cs_21, val_cs_21, test_cs_21 = split(human_cs_21)
    train_ru_21, val_ru_21, test_ru_21 = split(human_ru_21)
    train_cs_20, val_cs_20, test_cs_20 = split(human_cs_20)
    train_ru_20, val_ru_20, test_ru_20 = split(human_ru_20)
    
    human_train = concat_shuffle_clean([train_cs_22,train_ru_22,train_cs_21,train_ru_21,train_cs_20,train_ru_20])
    human_train_cs = concat_shuffle_clean([train_cs_22,train_cs_21,train_cs_20])
    human_train_ru = concat_shuffle_clean([train_ru_22,train_ru_21,train_ru_20])    
    
    human_val = concat_shuffle_clean([val_cs_22,val_ru_22,val_cs_21,val_ru_21,val_cs_20,val_ru_20])
    human_val_cs = concat_shuffle_clean([val_cs_22,val_cs_21,val_cs_20])
    human_val_ru = concat_shuffle_clean([val_ru_22,val_ru_21,val_ru_20])
    
    human_test = concat_shuffle_clean([test_cs_22,test_ru_22,test_cs_21,test_ru_21,test_cs_20,test_ru_20])
    human_test_cs = concat_shuffle_clean([test_cs_22,test_cs_21,test_cs_20])
    human_test_ru = concat_shuffle_clean([test_ru_22,test_ru_21,test_ru_20])    
    
    #human = human_cs_22 + human_ru_22 + human_cs_21 + human_ru_21 + human_cs_20 + human_ru_20
    #human_cs = human_cs_22 + human_cs_21 + human_cs_20
    #human_ru = human_ru_22 + human_ru_21 + human_ru_20

    #mt

    mt_cs_22 = open(f'{dirpath}/2022/mt/mt-dataset-22-cs-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()
    mt_ru_22 = open(f'{dirpath}/2022/mt/mt-dataset-22-ru-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()

    mt_cs_21 = open(f'{dirpath}/2021/mt/mt-dataset-21-cs-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()
    mt_ru_21 = open(f'{dirpath}/2021/mt/mt-dataset-21-ru-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()

    mt_cs_20 = open(f'{dirpath}/2020/mt/mt-dataset-20-cs-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()
    mt_ru_20 = open(f'{dirpath}/2020/mt/mt-dataset-20-ru-{score}-{translation}.txt', 'r', encoding='UTF-8').readlines()
    
    train_cs_22, val_cs_22, test_cs_22 = split(mt_cs_22)
    train_ru_22, val_ru_22, test_ru_22 = split(mt_ru_22)
    train_cs_21, val_cs_21, test_cs_21 = split(mt_cs_21)
    train_ru_21, val_ru_21, test_ru_21 = split(mt_ru_21)
    train_cs_20, val_cs_20, test_cs_20 = split(mt_cs_20)
    train_ru_20, val_ru_20, test_ru_20 = split(mt_ru_20)
    
    mt_train = concat_shuffle_clean([train_cs_22,train_ru_22,train_cs_21,train_ru_21,train_cs_20,train_ru_20])
    mt_train_cs = concat_shuffle_clean([train_cs_22,train_cs_21,train_cs_20])
    mt_train_ru = concat_shuffle_clean([train_ru_22,train_ru_21,train_ru_20])
    
    mt_val = concat_shuffle_clean([val_cs_22,val_ru_22,val_cs_21,val_ru_21,val_cs_20,val_ru_20])
    mt_val_cs = concat_shuffle_clean([val_cs_22,val_cs_21,val_cs_20])
    mt_val_ru = concat_shuffle_clean([val_ru_22,val_ru_21,val_ru_20])
    
    mt_test = concat_shuffle_clean([test_cs_22,test_ru_22,test_cs_21,test_ru_21,test_cs_20,test_ru_20])
    mt_test_cs = concat_shuffle_clean([test_cs_22,test_cs_21,test_cs_20])
    mt_test_ru = concat_shuffle_clean([test_ru_22,test_ru_21,test_ru_20])
    

    #mt = mt_cs_22 + mt_ru_22 + mt_cs_21 + mt_ru_21 + mt_cs_20 + mt_ru_20
    #mt_cs = mt_cs_22 + mt_cs_21 + mt_cs_20
    #mt_ru = mt_ru_22 + mt_ru_21 + mt_ru_20
    
    dataset_train, dataset_test, dataset_val = combine_shuffle_split(human_train, mt_train, human_val, mt_val, human_test, mt_test)

    create_csv('training', dataset_train, '', score, translation)
    create_csv('test', dataset_test, '', score, translation)
    create_csv('validation', dataset_val, '', score, translation)
    
    dataset_train_ru, dataset_test_ru, dataset_val_ru = combine_shuffle_split(human_train_ru, mt_train_ru, human_val_ru, mt_val_ru, human_test_ru, mt_test_ru)

    create_csv('training', dataset_train_ru, 'ru', score, translation)
    create_csv('test', dataset_test_ru, 'ru', score, translation)
    create_csv('validation', dataset_val_ru, 'ru', score, translation)
    
    dataset_train_cs, dataset_test_cs, dataset_val_cs = combine_shuffle_split(human_train_cs, mt_train_cs, human_val_cs, mt_val_cs, human_test_cs, mt_test_cs)

    create_csv('training', dataset_train_cs, 'cs', score, translation)
    create_csv('test', dataset_test_cs, 'cs', score, translation)
    create_csv('validation', dataset_val_cs, 'cs', score, translation)

if __name__ == "__main__":
    main(95, 'src-tgt')