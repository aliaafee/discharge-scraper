import os
import re
import docx2txt
from .data_writer import CSVWriter, DataWriter
from .bsconverter import bsconverter
import collections

class Scraper:
    def __init__(self):
        self.field_definition = {}
        
        self.default_process = [
            self.clean_up,
            self.get_first_line,
            self.get_pretab,
            self.clean_up,
            self.get_prelongspace
        ]
        
        self.field_process = {}

        self.files_processed = 0
        self.bad_files = []
        

    def get_field_names(self):
        return [field for field in self.field_definition.keys()] + ['file_path']
        
        
    def set_field_definition(self, field_definition):
        self.field_definition = field_definition
        self.generate_field_regex()
        
        
    def set_custom_processing(self, field_process):
        self.field_process = field_process
        
        
    def generate_field_regex(self):
        self.field_regex = {}
        for field, aliases in self.field_definition.items():
            self.field_regex[field] = []
            for alias in aliases:
                self.field_regex[field].append(re.compile(alias, re.IGNORECASE))


    def get_first_line(self, text):
        line, sep, rest = text.partition("\n")
        return line


    def get_pretab(self, text):
        line, sep, rest = text.partition("\t")
        return line


    def get_prelongspace(self, text):
        line, sep, rest = text.partition("  ")
        return line


    def get_predoublelinebreak(self, text):
        line, sep, rest = text.partition("\n\n")
        return line


    def clean_up(self, text):
        text = text.replace(":", "")
        text = text.strip()
        return text


    def extract_age(self, text):
        convert_factor = 1.0
        
        if  any(item in text.casefold() for item in ['day', 'd']):
            convert_factor = 365.0

        if 'month' in text.casefold():
            convert_factor = 12.0
        
        match = re.search(r'\d{1,3}', text)
        if match:
            return float(match.group())/convert_factor
        print("Cannot extract age '{}'".format(text))
        return text


    def sanitize_sex(self, text):
        if 'f' in text.casefold():
            return "Female"
        if 'm' in text.casefold():
            return "Male"
        print("Cannot sanitize sex '{}'".format(text))
        return text


    def extract_date(self, text):
        match = re.search(r'\d{4}(?:-|/)\d{1,2}(?:-|/)\d{1,2}', text)
        if match:
            return match.group()
        match = re.search(r'\d{1,2}(?:-|/)\d{1,2}(?:-|/)\d{4}', text)
        if match:
            return match.group()
        match = re.search(r'\d{3}(?:-|/)\d{1,2}(?:-|/)\d{1,2}', text)
        if match:
            return match.group()
        match = re.search(r'\d{1,2}(?:-|/)\d{1,2}(?:-|/)\d{3}', text)
        if match:
            return match.group()
        match = re.search(r'\d{1,2}(?:-|/)\d{1,2}(?:-|/)\d{1,2}', text)
        if match:
            return match.group()
        return ""


    def remove_date(self, text):
        date_text = self.extract_date(text)
        return text.replace(date_text, "")


    def sanitize_date(self, text):
        text = text.strip()
        if not text:
            return text

        text = text.replace('-', '/')

        text = "/".join(str(int(field)) for field in text.split('/'))

        match = re.search(r'207\d{1}', text)
        if match:
            if text.find(match.group()) == (len(text) - 4):
                #Date ends with year
                text = "/".join(reversed(text.split("/")))
                return text
            if text.find(match.group()) == 0:
                #Date starts with year
                return text

        #Has two digit year
        match = re.search(r'7\d{1}', text)
        if match:
            text = text.replace(match.group(), "20"+match.group())
            if text.find(match.group()) == (len(text) - 2):
                #Ends with two digit year
                text = "/".join(reversed(text.split("/")))
                return text
            return text
        
        match = re.search(r'\d{4}(?:/)\d{1,2}(?:/)\d{1,2}', text)
        if not match:
            print("Unsanitizable Date '{}'".format(text))
            return text
        return text


    def convert_date_bs2ad(self, text):
        text = text.strip()
        if not text:
            return text
        
        try:
            text_array = [int(item) for item in text.split("/")]
        except:
            print("Cannot Convert '{}'".format(text))
            return "#DATE_ERROR#"
        
        try:
            return bsconverter.bs2ad(text_array[0], text_array[1], text_array[2])
        except:
            print("Cannot Convert '{}'".format(text))
            return "#DATE_ERROR#"


    def get_fulltext(self, filename):
        try:
            text = docx2txt.process(filename)
            return text
        except:
            print("Cannot open file '{}'".format(filename))
            return None
        
    def match_field(self, field_name, text):
        for field_regex in self.field_regex[field_name]:
            match = field_regex.search(text)
            if match:
                return match
        return None


    def execute_process_list(self, process, text):
        result = text
        for task in process:
            result = task(result)
        return result



    def extract_fields(self, text):
        result = {}
        nomatch = []
        for field_name in self.field_definition:
            match = self.match_field(field_name, text)
            if match:
                field_text = (text[match.end():])

                if field_name in self.field_process:
                    field_text = self.execute_process_list(self.field_process[field_name], field_text)
                else:
                    field_text = self.execute_process_list(self.default_process, field_text)

                result[field_name] = field_text
            else:
                nomatch.append(field_name)
        return result, nomatch


    def gen_ouput_row(self, row):
        output_row = []
        for field_name in self.field_definition.keys():
            if field_name in row.keys():
                output_row.append(row[field_name])
            else:
                output_row.append("")
        output_row.append(row["file_path"])
        return output_row


    def is_excluded_filename(self, filename, exclude_filename_prefix, include_filename_extension):
        if filename[0] in exclude_filename_prefix:
            return True
        filename_base, filename_extension = os.path.splitext(filename)
        if filename_extension in include_filename_extension:
            return False
        return True


    def extract_data(self, src_folder, data_writer, exclude_filename_prefix=["~", "."], include_filename_extension=[".docx"]):
        self.files_processed = 0
        for root, subdirs, files in os.walk(src_folder):
            for filename in files:
                if not self.is_excluded_filename(filename, exclude_filename_prefix, include_filename_extension):
                    filepath = os.path.join(root, filename)
                    file_text = self.get_fulltext(filepath)
                    if file_text:
                        fields, nomatch = self.extract_fields(file_text)
                        fields["file_path"] = filepath
                        data_writer.write_record(fields)
                    else:
                        print("No content in '{}'".format(filepath))
                        self.bad_files.append(filepath)
                    self.files_processed += 1



if __name__ == '__main__':

    scraper = Scraper()

    FIELDS = collections.OrderedDict()
    
    #Fields that will be extracted
    FIELDS = collections.OrderedDict()
    FIELDS["name"] = ["Name:"]
    FIELDS["age"] = ["Age:"]
    FIELDS["sex"] = ["Sex:"]
    
    scraper.set_field_definition(FIELDS)
    
    with CSVWriter('test.csv', scraper.get_field_names()) as writer:
        scraper.extract_data("./test", writer)
    
