import pandas as pd
import csv

def create_csvFile(path):
    """
    Create an empty CSV file at the specified path.

    Args:
    - path (str): The path to the CSV file.

    """
    print('path: ', path)
    with open(path, 'wb') as csvfile:
        csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

def append_to_csvFile(trial, allData, path, columns, control):
    """
    Append data to an existing CSV file.

    Args:
    - trial (int): The trial number.
    - allData (list): A list of data to be appended.
    - path (str): The path to the CSV file.
    - columns (list): The column names for the CSV file.
    - control (bool): Whether to include column headers or not.

    This function appends data to an existing CSV file with the specified format.

    """
    data = []
    for i in range(len(allData)):
        aux = [trial]
        for j in range(allData[i].shape[0]):
            aux.append(allData[i][j])
        data.append(aux)

    dataframe = pd.DataFrame(data, columns=columns)

    with open(path, 'a') as f:
        dataframe.to_csv(f, index=False, header=control)
