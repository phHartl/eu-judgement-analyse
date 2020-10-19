import os
import csv

def __to_whitespace_string(value_list):
    temp_string = ""
    for item in value_list:
        temp_string += item
        temp_string += " "
    temp_string = temp_string[:-1]
    return temp_string

def __convert_dict(mongo_dict):
    csv_dict = {}
    for k,v in mongo_dict.items():
        if isinstance(v, dict):
            csv_dict[k + "_ids"] = __to_whitespace_string(v.get("ids"))
            csv_dict[k + "_labels"] = __to_whitespace_string(v.get("labels"))
        elif isinstance(v, list):
            __to_whitespace_string(v)
        else:
            csv_dict[k] = v
    return csv_dict

def export_to_csv(data):
    directory = os.path.dirname(__file__)
    filename = 'corpus.csv'
    file_exists = os.path.isfile(filename)
    with open(filename, 'a+', newline='') as csvfile:
        fieldnames =[
            "reference",
            "celex",
            "ecli",
            "date",
            "title",
            "text",
            "keywords",
            "parties",
            "subject",
            "endorsements",
            "grounds",
            "decisions_on_costs",
            "operative_part",
            "case_affecting",
            "affected_by_case",
            "author_ids",
            "author_labels",
            "subject_matter_ids",
            "subject_matter_labels",
            "case_law_directory_ids",
            "case_law_directory_labels",
            "applicant_ids",
            "applicant_labels",
            "defendant_ids",
            "defendant_labels",
            "procedure_type_ids",
            "procedure_type_labels"
        ]
        dict_writer = csv.DictWriter(csvfile, delimiter=',', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
        if not file_exists:
            dict_writer.writeheader()
        for doc in data:
            csv_doc = __convert_dict(doc)
            dict_writer.writerow(csv_doc)