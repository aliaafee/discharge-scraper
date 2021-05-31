import collections
from scraper import Scraper, CSVWriter

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
with CSVWriter('test.csv', scraper.get_field_names()) as writer:
    scraper.extract_data("./test", writer)