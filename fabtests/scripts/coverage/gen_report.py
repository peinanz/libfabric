import os
import sys
import json
import getopt
import copy

verbosity = 0
data_format = []
output_format = ""

def get_input_param(argv):
    global verbosity
    global abspath
    global master_file
    global output_format

    filename = "master_features.json"
    abspath = os.path.abspath(os.getcwd())
    provs = ["all"]

    opts, args = getopt.getopt(argv, "d:m:p:v:c", [])
    for opt, arg in opts:
        if opt in ['-v']:
            verbosity = int(arg)
        elif opt in ['-d']:
            abspath = os.path.abspath(arg)
        elif opt in ['-m']:
            filename = arg
        elif opt in ['-p']:
            provs = arg.split(",")
        elif opt in ['-c']:
            output_format = "csv"
        else:
            print("option: [-m <master_file>][-d <data_path>][-p <providers>]\
                   [-v <verbosity_level>")
            print("ignore invalid options")

    return (abspath, filename, provs)

def get_attribute_list(data):
    keys = []
    values = []
    for item in data:
        keys.append(item[0])
        values.append(item[1])
    return (keys, values)

def get_feature_list(data):
    
    global data_format

    types = []
    features = []
    covers = []

    for item in data:
        val_list = []
        types.append(item[0])
        for elem in item[1]:
            val_list.append((0, []))
        features.append(item[1])
        covers.append(val_list)
    data_format = copy.deepcopy(covers)
    return (types, features, covers)

def create_master_list(filename):
    attrs = []
    fields = []
    types = []
    features = []
    results = []

    with open(filename, "r") as rf:
        context = json.load(rf)
        mlist = list(context.items())

        for ft in mlist:
            tag = ft[0]
            data = list(ft[1].items())
            if tag == "attributes":
                (attrs, fields) = get_attribute_list(data)
            elif tag == "features":
                (types, features, results) = get_feature_list(data)

    return (attrs, fields, types, features, results)

def read_dirs(path):
    dirs = []
    dir_list = os.listdir(path)
    for f in dir_list:
        if os.path.isdir(os.path.join(path, f)):
            dirs.append(f)
    return dirs

def read_files(path):
    files = []
    dir_list = os.listdir(path)
    for f in dir_list:
        if os.path.isfile(os.path.join(path, f)) and f.endswith("_feature_list"):
            files.append(os.path.join(path, f))
    return files

def get_val_list(data_str):
    data = data_str.replace("[", "").replace("]","").replace(" ","")
    return  data.split(',')

def get_feature_name(features, data):
    for item in features:
        if item == data:
            return item
        elems = item.split("=")
        if len(elems) > 1:
            if elems[0].strip() == data:
                return elems[1].strip()
    return ""

def parse_attr(attrs, fields, data):
    features = []
    values = []

    cur_attr = data[0].split(":")[0]
    if cur_attr not in attrs:
        return (cur_attr, features, values)

    cur_features = fields[attrs.index(cur_attr)]
    for i in range(1, len(data)):
        items = data[i].split(":")
        if len(items) > 1 and items[1].strip():
            fname = get_feature_name(cur_features, items[0].strip())
            if len(fname) > 0:
                features.append(fname)
                values.append(get_val_list(items[1]))
    return (cur_attr, features, values)

def read_test_result(attrs, fields, filename):
    attrlist = []
    featurelist = []
    datalist = []
    with open(filename, "r") as rf:
        context = json.load(rf)
        for item in context:
            (cur_attr, features, values) = parse_attr(attrs, fields, item)
            if len(cur_attr) and features and values:
                attrlist.append(cur_attr)
                featurelist.append(features)
                datalist.append(values)
    return (attrlist, featurelist, datalist)

def add_test_result(attrs, fields, types, features, filename, results, covers):

    (test_attrs, test_features, test_data) = \
              read_test_result(attrs, fields, filename)
    if not test_attrs or not test_features or not test_data:
        return

    fbasename = os.path.basename(filename)

    for cur_attr, flist, data in zip(test_attrs, test_features, test_data):
        for cur_f, val_list in zip(flist, data):
            if cur_f in types:
                tidx = types.index(cur_f)
                flist = features[tidx]
                vlist = covers[tidx]
                cur_vlist = results[tidx]
                if cur_f == "iov_limit":
                    if int(val_list[0]) > 1:
                        (cnt, files) = vlist[0]
                        if fbasename not in files:
                            files.append(fbasename)
                        vlist[0] = (cnt+1, files)
                        cur_vlist[0] = (1, [])
                else:
                    for cur_val in val_list:
                        if cur_val in flist:
                            vidx = flist.index(cur_val)
                            (cnt, files) = vlist[vidx]
                            if fbasename not in files:
                                files.append(fbasename)
                            vlist[vidx] = (cnt+1, files)
                            cur_vlist[vidx] = (1, [])
                covers[tidx] = vlist
                results[tidx] = cur_vlist

def add_coverage(attrs, fields, types, features, test_files, covers):

    results = copy.deepcopy(data_format)
    for f in test_files:
        add_test_result(attrs, fields, types, features, f, results, covers)

    return results

def check_coverage(attrs, fields, types, features, provs, abspath, results):

    test_files = []
    cover_list = []

    dir_list = read_dirs(abspath)

    avail_provs = [d for d in provs if d in dir_list]
    if "all"  in  provs:
        for d in dir_list:
            if d not in avail_provs:
                avail_provs.append(d)

    for p in avail_provs:
        cur_dir = os.path.join(abspath, p)
        test_files = read_files(os.path.join(abspath, p))
        cur_result = add_coverage(attrs, fields, types, features, test_files, results)
        cover_list.append(cur_result)

    test_files = read_files(abspath)
    if test_files:
        avail_provs.append("core")
        cur_result = add_coverage(attrs, fields, types, features, test_files, results)
        cover_list.append(cur_result)

    return (cover_list, avail_provs)

def output_features(types, features, results):
    print("====================")
    print("Coverage Details:")
    print("--------------------")
    for t, flist, rlist in zip(types, features, results):
        for f, res in zip(flist, rlist):
            (fval, flist) = res
            if verbosity > 2:
                print(t.ljust(16, " "), f.ljust(24, " "), fval, flist)
            else:
                if output_format == "csv":
                    print(t, ",", f, ",", fval)
                else:
                    print(t.ljust(16, " "), f.ljust(24, " "), fval)

def output_summary(title, types, features, results):
    global output_format
    total_count = 0.0
    total_covered = 0.0
    print("=====================")
    print(title, "summary")
    print("--------------------")
    for t, flist, rlist in zip(types, features, results):
        cur_count = 0
        cur_covered = 0
        for fval in rlist:
            (value, files) = fval
            cur_count += 1
            if value > 0 :
                cur_covered += 1
        if cur_count > 0 :
            if output_format == "csv":
                print(t,",", "{:.2%}".format(cur_covered / cur_count), \
                   ",(", round(cur_covered), "/", round(cur_count), ")")
            else:
                print(t.ljust(16, " "),     \
                    "{:.2%}".format(cur_covered / cur_count), \
                    "  (", round(cur_covered), "/", round(cur_count), ")")
            total_count += cur_count
            total_covered += cur_covered
    print("--------------------")
    if total_count > 0:
        if output_format == "csv":
            print("coverage,", \
                "{:.2%}".format(total_covered/total_count), \
                ",(", round(total_covered), "/", round(total_count), ")")
        else:
            print("coverage:".ljust(16, " "),  \
                "{:.2%}".format(total_covered/total_count), \
                 "  (", round(total_covered), "/", round(total_count), ")")
       

def main(argv):

    (abspath, master_file, provs) = get_input_param(argv)

    if not os.path.isdir(abspath):
        print("invalid path for test files: ", abspath)
        return

    master_full_path = os.path.join(abspath, master_file)
    if not os.path.isfile(master_full_path):
        master_full_path = os.path.join(os.path.abspath(os.getcwd()), master_file)
        if not os.path.isfile(master_full_path):
            print("invalid master file: ", master_file)
            return
    
    cover_list = []
    (attrs, fields, types, features, total_covers) = \
            create_master_list(master_full_path)
    if not attrs or not fields or not types or not features:
        print("master file: ", master_file, " is not in the right format")
        return

    (prov_covers, avail_provs) = check_coverage(attrs, fields, types,  \
                        features, provs, abspath, total_covers)
    output_summary("Total", types, features, total_covers)
    if verbosity:
        for p, result in zip(avail_provs, prov_covers):
            output_summary(p, types, features, result)
        if verbosity > 1:
            output_features(types, features, total_covers)

if __name__ == "__main__":
    main(sys.argv[1:])
