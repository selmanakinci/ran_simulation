import os


def create_dir(sim_param):

    # define the name of the directory to be created
    parent_dir = os.path.join("results", sim_param.timestamp)
    directory1 = "sm"
    path = os.path.join(parent_dir, directory1)
    if not os.path.exists(path):
        os.makedirs(path)

    directory2 = "data"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory1 = "controller"
    path = os.path.join(parent_dir, directory1)
    if not os.path.exists(path):
        os.makedirs(path)

    directory2 = "data"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory1 = "user_results"
    directory2 = "tp"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory2 = "tp2"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory2 = "ql"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory2 = "delay"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory2 = "average_results"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory3 = "data"
    path = os.path.join(parent_dir, directory1, directory2, directory3)
    if not os.path.exists(path):
        os.makedirs(path)

    directory1 = "slice_results"
    '''directory2 = "tp"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory2 = "ql"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory2 = "delay"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)'''

    directory2 = "average_results"
    path = os.path.join(parent_dir, directory1, directory2)
    if not os.path.exists(path):
        os.makedirs(path)

    directory3 = "data"
    path = os.path.join(parent_dir, directory1, directory2, directory3)
    if not os.path.exists(path):
        os.makedirs(path)

    # create logfile and write SimParameters
    log_file = open(parent_dir + "/logfile.txt", "wt")
    attrs = vars(sim_param)
    log_file.write('SimParam\n' + ''.join("%s: %s\n" % item for item in attrs.items()))
    #log_file.close()

    return log_file