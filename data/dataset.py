import random
import os
import csv

dirpath = os.path.dirname(__file__)

def create_csv(name, data):
    file = open(f'{dirpath}/{name}.csv', 'w', encoding='UTF-8', newline='')
    header = ['sentence', 'labels']
    writer = csv.writer(file, delimiter ='|')
    writer.writerow(header)
    for line in data:
        row = []
        for part in line.split('|'):
            row.append(part)
        writer.writerow(row)

    file.close()

def main():
    #human
    human_cs_22 = open(f'{dirpath}/2022/human-dataset-22-cs.txt', 'r', encoding='UTF-8').readlines()
    human_ru_22 = open(f'{dirpath}/2022/human-dataset-22-ru.txt', 'r', encoding='UTF-8').readlines()

    human_cs_21 = open(f'{dirpath}/2021/human-dataset-21-cs.txt', 'r', encoding='UTF-8').readlines()
    human_ru_21 = open(f'{dirpath}/2021/human-dataset-21-ru.txt', 'r', encoding='UTF-8').readlines()

    human_cs_20 = open(f'{dirpath}/2020/human-dataset-20-cs.txt', 'r', encoding='UTF-8').readlines()
    human_ru_20 = open(f'{dirpath}/2020/human-dataset-20-ru.txt', 'r', encoding='UTF-8').readlines()

    human = human_cs_22 + human_ru_22 + human_cs_21 + human_ru_21 + human_cs_20 + human_ru_20


    #mt

    mt_cs_22 = open(f'{dirpath}/2022/mt-dataset-22-cs.txt', 'r', encoding='UTF-8').readlines()
    mt_ru_22 = open(f'{dirpath}/2022/mt-dataset-22-ru.txt', 'r', encoding='UTF-8').readlines()

    mt_cs_21 = open(f'{dirpath}/2021/mt-dataset-21-cs.txt', 'r', encoding='UTF-8').readlines()
    mt_ru_21 = open(f'{dirpath}/2021/mt-dataset-21-ru.txt', 'r', encoding='UTF-8').readlines()

    mt_cs_20 = open(f'{dirpath}/2020/mt-dataset-20-cs.txt', 'r', encoding='UTF-8').readlines()
    mt_ru_20 = open(f'{dirpath}/2020/mt-dataset-20-ru.txt', 'r', encoding='UTF-8').readlines()

    mt = mt_cs_22 + mt_ru_22 + mt_cs_21 + mt_ru_21 + mt_cs_20 + mt_ru_20
    
    #combine, shuffle, split
    dataset = human + mt
    for i in range(0,len(dataset)):
        dataset[i] = dataset[i].strip()
    random.shuffle(dataset)

    test_len = round(len(dataset) * 0.2)

    test = dataset[:test_len]
    rest = dataset[test_len:]

    val_len = round(len(rest) * 0.2)

    val = rest[:val_len]
    train = rest[val_len:]

    create_csv('training', train)
    create_csv('test', test)
    create_csv('validation', val)
    

if __name__ == "__main__":
    main()