import csv


#Data Write Base Class
class DataWriter:
    def __init__(self, field_definition):
        self.field_definition = field_definition

    def __enter__(self):
        return self

    def __exit__(self, type, value,traceback):
        pass
    
    def gen_output_row(self, record):
        output_row = []
        for field_name in self.field_definition:
            if field_name in record.keys():
                output_row.append(record[field_name])
            else:
                output_row.append("")
        #output_row.append(record["file_path"])
        return output_row

    def write_header(self):
        row = self.field_definition
        print("\t".join(row))
            

    def write_record(self, record):
        row = self.gen_output_row(record)
        print("\t".join((str(cell) for cell in row)))



#CSV Data Writer
class CSVWriter(DataWriter):
    def __init__(self, filename, field_definition):
        super().__init__(field_definition)
        self.filename = filename
        

    def __enter__(self):
        print("opening csv file")
        self.datafile = open(self.filename, mode='w', newline='')
        self.datafile_writer = csv.writer(self.datafile, delimiter=',',
                                          quotechar='"', quoting=csv.QUOTE_ALL)
        self.write_header()
        return self

    def write_header(self):
        row = self.field_definition
        self.datafile_writer.writerow(row)
        
    def write_record(self, record):
        row = self.gen_output_row(record)
        self.datafile_writer.writerow(row)
    
    def __exit__(self, type, value,traceback):
        print("closing csv file")
        self.datafile.close()



if __name__ == '__main__':
    #test
    with CSVWriter("test.csv", ['f1', 'f2']) as w:
        w.write_record({"f1": "a", 'f2': 'b'})
