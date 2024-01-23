from FunctionClass import Function

class Main:

    if __name__=="__main__":

        Function.csv_list(Function.Files())
        file_name = input("Choose a dataset to ingest: ") + '.csv'
        Function.csv_check(file_name, Function.Files())
        Function.LogstashRunner(Function.ConfigModifier(file_name))
        Function.CpuVisualizer_and_DataDistributor(Function.TopicReader(file_name), file_name)


