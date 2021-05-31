import collections
from scraper import Scraper, CSVWriter


#Fields that will be extracted

FIELDS = collections.OrderedDict()
FIELDS["name"] = ["Name:"]
FIELDS["age"] = ["Age:"]
FIELDS["sex"] = ["Sex:"]
FIELDS["address"] = ["Address:"]
FIELDS["ip_number"] = ["IP No.:", "Inpatient no:"]
FIELDS["phone"] = ["Contact No:", "Contact no.:", "Contact:"]

#FIELDS["admitted_bs"] = ["Date of Admission:"]
#FIELDS["discharged_bs"] = ["Date of Discharge:", "Date of Transfer:"]
FIELDS["admitted_ad"] = ["Date of Admission:"]
FIELDS["discharged_ad"] = ["Date of Discharge:", "Date of Transfer:"]

FIELDS["diagnosis"] = ["Final Diagnosis", "FINAL DIAGNOSIS:"]

#FIELDS["operated_bs"] = ["Date:", "Operations", "Surgery:"]
FIELDS["operated_ad"] = ["Date:", "Operations", "Surgery:"]

FIELDS["surgeons"] = ["Surgeons:", "Surgeon:", "Surgeons :"]
FIELDS["operation"] = ["Operations", "Surgery:"]


#initialize the scraper
scraper = Scraper(FIELDS)


#set custom field process
FIELD_PROCESS = {}
FIELD_PROCESS["age"] = scraper.default_process + [scraper.extract_age]
FIELD_PROCESS["sex"] = scraper.default_process + [scraper.sanitize_sex]

FIELD_PROCESS["admitted_bs"] = scraper.default_process + [scraper.extract_date, scraper.sanitize_date]
FIELD_PROCESS["discharged_bs"] = scraper.default_process + [scraper.extract_date, scraper.sanitize_date]
FIELD_PROCESS["admitted_ad"] = FIELD_PROCESS["admitted_bs"] + [scraper.convert_date_bs2ad]
FIELD_PROCESS["discharged_ad"] = FIELD_PROCESS["discharged_bs"] + [scraper.convert_date_bs2ad]

FIELD_PROCESS["surgeons"] = scraper.default_process
FIELD_PROCESS["operation"] = scraper.default_process + [scraper.remove_date]
FIELD_PROCESS["operated_bs"] = scraper.default_process + [scraper.extract_date, scraper.sanitize_date]
FIELD_PROCESS["operated_ad"] = FIELD_PROCESS["discharged_bs"] + [scraper.convert_date_bs2ad]

scraper.set_custom_processing(FIELD_PROCESS)

with CSVWriter('test.csv', scraper.get_field_names()) as writer:
    scraper.extract_data("./test", writer)