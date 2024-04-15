"""
Archives scraped datas
"""


"""
Libraries
"""
import os
import shutil
import datetime

from common_variables import path_data_source, path_data_archives


"""
Functions
"""
def createDataArchive():
    """
    Create a data archive by copying files and directories from the source path to the archive path.

    :param path_data_source: The path to the source directory.
    :param path_data_archives: The path to the archive directory.
    """
    # Create a new folder with the current date
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    new_folder = os.path.join(path_data_archives, today)

    # Create the new folder if it doesn't already exist
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    for filename in os.listdir(path_data_source):
        source_file = os.path.join(path_data_source, filename)
        destination_file = os.path.join(new_folder, filename)

        shutil.copy(source_file, destination_file)