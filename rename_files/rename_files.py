import os, string

def get_localfiles():
    directory = os.getcwd()
    file_list = os.listdir( directory )
    return file_list

def rename_file(old, new):
    directory = os.getcwd()
    old_file = os.path.join( directory, old )
    new_file = os.path.join( directory, new )
    os.rename(old_file, new_file)

def msg(old, new):
    print("Renaming file from {} to {}".format(old, new))

for file_name in get_localfiles():
    """ Renames files using the original name without any numbers """
    
    new_name = ""
    for letter in file_name:
        new_name = file_name.translate(None, string.digits)
    msg(file_name, new_name)
    rename_file(file_name, new_name)

print("All files have been processed")

    
