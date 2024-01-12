import numpy as np

def hasNumbers(inputString):
    """
    Check if a string contains any digits.

    Args:
    - inputString (str): The input string to check.

    Returns:
    - bool: True if the input string contains any digits, False otherwise.
    """
    return any(char.isdigit() for char in inputString)

def extractData(splitted_line):
    """
    Extract numerical data from a line of text.

    Args:
    - splitted_line (str): The input line of text containing data.

    Returns:
    - numpy.ndarray: An array of numerical data extracted from the input line.
    """
    segments = splitted_line.split()
    data = np.ones(len(segments) - 1)

    for i in range(1, len(segments)):
        if hasNumbers(segments[i]):
            data[i - 1] = segments[i].replace(',', '.')
        else:
            data[i - 1] = np.nan

    return data

def extractHead(splitted_line):
    """
    Extract the head and message from a line of text.

    Args:
    - splitted_line (str): The input line of text.

    Returns:
    - tuple: A tuple containing the head and message extracted from the input line.
    """
    segments = splitted_line.split()
    head = segments[1]
    if len(segments) > 2:
        message = segments[2:]
    else:
        message = []
    return head, message

def extractDevice(list_line):
    """
    Extract device information from a list of lines.

    Args:
    - list_line (list): A list of lines.

    Returns:
    - list: A list of devices extracted from the input list.
    """
    devices = []
    for i in range(2, len(list_line)):
        if list_line[i] == "Empatica_E4":
            devices.append(list_line[i - 1])

    return devices

def extractMessages(splitted_line):
    """
    Extract messages and lines from a line of text.

    Args:
    - splitted_line (str): The input line of text.

    Returns:
    - tuple: A tuple containing the extracted message and lines.
    """
    if len(splitted_line):
        if splitted_line.find("\n") == -1:
            msg = splitted_line
            lines = []
        else:
            lines = splitted_line.split("\n")
            msg = lines[-1]
            lines = lines[:-1]
    else:
        msg = ""
        lines = []

    return msg, lines
