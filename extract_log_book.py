import collections
import getopt
from scraper.data_writer import DataWriter
from scraper import Scraper, CSVWriter
import sys

import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread

#Initialize the scraper
scraper = Scraper()


#Fields that will be extracted
fields = collections.OrderedDict()
fields["name"] = ["Name:"]
fields["age"] = ["Age:"]
fields["sex"] = ["Sex:"]
fields["address"] = ["Address:"]
fields["ip_number"] = ["IP No.:", "Inpatient no:"]
fields["phone"] = ["Contact No:", "Contact no.:", "Contact:"]
#fields["admitted_bs"] = ["Date of Admission:"]
#fields["discharged_bs"] = ["Date of Discharge:", "Date of Transfer:"]
fields["admitted_ad"] = ["Date of Admission:"]
fields["discharged_ad"] = ["Date of Discharge:", "Date of Transfer:"]
fields["diagnosis"] = ["Final Diagnosis", "FINAL DIAGNOSIS:"]
#fields["operated_bs"] = ["Date:", "Operations", "Surgery:"]
fields["operated_ad"] = ["Date:", "Operations", "Surgery:"]
fields["surgeons"] = ["Surgeons:", "Surgeon:", "Surgeons :"]
fields["operation"] = ["Operations", "Surgery:"]

#Custom field process
field_process = {}
field_process["age"] = scraper.default_process + [scraper.extract_age]
field_process["sex"] = scraper.default_process + [scraper.sanitize_sex]
field_process["admitted_bs"] = scraper.default_process + [scraper.extract_date, scraper.sanitize_date]
field_process["discharged_bs"] = scraper.default_process + [scraper.extract_date, scraper.sanitize_date]
field_process["admitted_ad"] = field_process["admitted_bs"] + [scraper.convert_date_bs2ad]
field_process["discharged_ad"] = field_process["discharged_bs"] + [scraper.convert_date_bs2ad]
field_process["surgeons"] = scraper.default_process
field_process["operation"] = scraper.default_process + [scraper.remove_date]
field_process["operated_bs"] = scraper.default_process + [scraper.extract_date, scraper.sanitize_date]
field_process["operated_ad"] = field_process["discharged_bs"] + [scraper.convert_date_bs2ad]

scraper.set_field_definition(fields)
scraper.set_custom_processing(field_process)


def scrape(src_folder, out_file_csv=""):
    if not out_file_csv:
        with DataWriter(scraper.get_field_names()) as writer:
            scraper.extract_data(src_folder, writer)
        return

    with CSVWriter(out_file_csv, scraper.get_field_names()) as writer:
        scraper.extract_data(src_folder, writer)


def usage():
    """App usage"""
    print(f"Usage: {sys.argv[0]} [OPTIONS]... [FOLDER]")
    print("Extract data from all .docx discharge files located in [FOLDER]")
    print("Recursively looks in all folders")
    print("    -o, --out")
    print("       Output CSV file")
    print("    -h, --help")
    print("       Displays this help")



def main_gui():
    root = tk.Tk()
    root.title("Discharge Scraper")
    root.geometry('300x50+50+50')

    status = tk.Label(root, text="0 Files Processed")

    status.pack()

    src_folder = filedialog.askdirectory(title="Folder Containing Discharges")

    if not src_folder:
        root.withdraw()
        return

    out_file_csv = filedialog.asksaveasfilename(title="Output CSV file", filetypes=(("csv files","*.csv"),("all files","*.*")))

    if not out_file_csv:
        root.withdraw()
        return

    def scrape_function():
        with CSVWriter(out_file_csv, scraper.get_field_names()) as writer:
            scraper.extract_data(src_folder, writer)

    new_thread = Thread(target=scrape_function)

    def monitor():
        if new_thread.is_alive():
            status.config(text ="{} File Processed".format(scraper.files_processed))
            status.update()
            root.after(100, monitor)
        else:
            status.config(text ="{} Completed Processing".format(scraper.files_processed))
            status.update()
            messagebox.showinfo("Done", "Finished extracting data from discharges to {}".format(out_file_csv))
            root.destroy()
    
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    new_thread.start()
    monitor()

    root.mainloop()
    
    
def main(argv):
    src_folder = ""
    out_file_csv = ""
    
    try:
        opts, args = getopt.getopt(argv, "ho:", ["help", "out="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if args:
        src_folder = args[0]
    else:
        #usage()
        #sys.exit(2)
        main_gui()
        return

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        if opt in ("-o", "--out"):
            out_file_csv = arg

    if not src_folder:
        usage()
        sys.exit(2)
    scrape(src_folder, out_file_csv)
        
        

    
    


if __name__ == '__main__':
    main(sys.argv[1:])
