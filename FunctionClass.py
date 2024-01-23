import pandas as pd
import os
import psutil
import matplotlib.pyplot as plt
import time
from kafka import KafkaConsumer
import json
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import webbrowser

class Function:

    def Files():

        files = os.listdir('C:/Users/oergun/Desktop/innova/proje/csv_files')
        return files

    def csv_list(files):

        print("\n")
        for file in files:
            print(file)
        print("\n%d datasets are available..." %len(files))

    def csv_check(ingest, files):

        if ingest in files:
            print("%s is being ingested as a kafka topic with logstash..." %ingest)
            return ingest
        else:
            print("There is no such dataset to ingest!")
            exit()

    def ConfigModifier(choice):

        path = "C:\\Users\\oergun\\Desktop\\innova\\proje\\csv_files\\" + choice
        df = pd.read_csv(path)
        list_of_column_names = list(df.columns)
        replace_text2 = '      columns => ' + str(list_of_column_names) + '\n'
        replace_text3 = '      topic_id => "' + choice + '"\n'

        a_file = open("C:/Users/oergun/Desktop/innova/proje/logstash/logstash.conf", "r")
        list_of_lines = a_file.readlines()
        list_of_lines[6] = replace_text2
        list_of_lines[12] = replace_text3

        a_file = open("C:/Users/oergun/Desktop/innova/proje/logstash/logstash.conf", "w")
        a_file.writelines(list_of_lines)
        a_file.close()

        return path

    def LogstashRunner(path):

        os.system('cmd /c "cd C:/Users/oergun/Desktop/innova/proje/logstash/bin && type ' + path + ' | logstash -f logstash.conf"')

    def TopicReader(TopicName):
        
        consumer = KafkaConsumer(
            TopicName,
            bootstrap_servers = 'localhost:9092',
            auto_offset_reset = 'earliest',
            consumer_timeout_ms=1000
        )
        
        z = []
        print("\n")
        for message in consumer:
            z.append(json.loads(message.value))
        
        return z


    def CpuVisualizer_and_DataDistributor(KafkaMessages, ind):

        x = []
        y = []

        z = 0

        while True:

            if z < (len(KafkaMessages)):

                cpu = psutil.cpu_percent(interval=1)
                x.append(time.strftime("%H:%M:%S"))
                y.append(cpu)

                plt.ylim(0, 100)
                plt.yticks(fontsize=8)

                ax = plt.gca()
                ax.axes.xaxis.set_ticklabels([])
                ax.xaxis.label.set_size(10)
                ax.yaxis.label.set_size(10)

                plt.locator_params(axis='y', nbins=20)
                for i in range(len(y)):
                    plt.ylabel("%" + str(y[i]) + "       ", rotation = 0)
                    plt.xlabel(x[i])

                if y[i] > 50:
                    client = MongoClient('mongodb://localhost:27017')
                    m_ind = ind.replace(".csv", "")
                    db = client[m_ind + "db"]
                    customers = db[ind]
                    customers.insert_one(KafkaMessages[i])
                    print(str(KafkaMessages[i]) + ' is ingested in MongoDB')
                else:
                    client = Elasticsearch("http://localhost:9200")
                    client.index(index=ind, id=i, document=KafkaMessages[i])
                    print(str(KafkaMessages[i]) + ' is ingested in Elasticsearch')

                plt.plot(x, y, color = 'blue')

                plt.pause(1)

                z = z + 1

            else:
                webbrowser.open("http://localhost:5601")
                webbrowser.open("http://localhost:8081")
                exit()

        plt.show()
