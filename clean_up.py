import json


def read_json(filename):
    try:
        with open(filename, 'r') as file:
            version_dict = json.load(file)
            return version_dict
    except FileNotFoundError:
        print('can not find file %s please check file name'%filename)


def output_json(new_tags_dict):
    if new_tags_dict is None or len(new_tags_dict) == 0:
        print('Empty new tag list, can not output json file')
        return

    with open('cleaned_up_version_list.json', 'w') as file:
        json.dump(new_tags_dict, file)


def analysis_version_tag(version_dict):
    if version_dict is None:
        print('version dict can not be None')
        return

    new_tags_dict = {}

    for name, versions in version_dict.items():
        new_tags_dict[name] = list()

        for version in versions:
            version_number = ''
            version_type = ''

            # remove 'v' at the first position for following format
            if version[0] == 'v' and version[1].isdigit():
                version = version[1:]

            # format like 1.0.1-rc0
            if '-' in version:
                components = version.split('-')

                # in early stage, apache named kafka version like kafka-0.7.2-incubating-candidate-5
                if len(components) > 2:
                    for index in range(len(components)):
                        if components[index][0].isdigit():
                            version_number = components[index]
                            version_type = format_type(components[index + 1:])
                            break
                # normal case, 1.0.0-rc1
                else:
                    version_number = components[0]
                    version_type = format_type(components[1])

            #format like 1.0.1rc0
            else:
                version_number, version_type = split_alpha_digit(version)

            new_tag = assemble_new_version_tag(version_number, version_type)
            new_tags_dict[name].append(new_tag)

    output_json(new_tags_dict)


def assemble_new_version_tag(version_number, version_type):
    newTag = ''

    # one special case: tflite-v0.1.7
    if version_number == 'tflite':
        newTag = version_number + '-' + version_type
        return newTag

    if version_number is None or len(version_number) == 0:
        return version_type
    else:
        newTag += 'v' + version_number

    if version_type is None or len(version_type) == 0:
        return newTag
    else:
        newTag += '-' + version_type
        return newTag


def split_alpha_digit(string):
    version_number = ''
    version_type = ''
    for index in range(len(string)):
        if string[index].isdigit() is not True and string[index] != '.':
            version_number = string[0:index]
            version_type = string[index:]
            return version_number, version_type

    return string, version_type


'''
    a1: first alpha version
    b1: first beta version
    bc1: first beta candidate
    rc1: first release candidate
'''


def format_type(version_type):
    newTag = ''

    if version_type is None or len(version_type) == 0:
        print('version type can not be None')
        return ''

    # input a list of words
    if isinstance(version_type, list):
        # e.g 0.8.0-beta1
        if len(version_type) == 1 and version_type[0] == 'beta1':
            return 'b1'
        # e.g 0.8.0-beta1-candidate1
        if len(version_type) == 2 and version_type[0] == 'beta1':
            return 'bc1'
        # e.g kafka-0.7.2-incubating-candidate-5
        if version_type[0] == 'incubating' and version_type[1] == 'candidate':
            newTag = 'rc' + version_type[2]
            return newTag
    # input a string
    elif isinstance(version_type, str):

        # e.g 1.0.0-alpha1 or alpha
        if len(version_type) > 4 and version_type[0:5] == 'alpha':
            if len(version_type) == 5:
                newTag = 'a1'
            else:
                newTag = 'a' + version_type[5]
            return newTag
        # e.g 1.0.0-beta1 or beta
        if len(version_type) > 3 and version_type[0:4] == 'beta':
            if len(version_type) == 4:
                newTag = 'b1'
            else:
                newTag = 'b' + version_type[4]
            return newTag

        return version_type


if __name__ == '__main__':
    analysis_version_tag(read_json('release_list.json'))
