thonimport json
import os
from extractors.webmd_parser import WebMDParser
from outputs.data_exporter import DataExporter

def main():
    # Initialize the scraper and data exporter
    parser = WebMDParser()
    exporter = DataExporter()

    # Example search URL (you can modify this as needed)
    search_url = "https://doctor.webmd.com/results?q=heart&d=40&newpatient=false&isvirtualvisit=false&entity=all&gender=all&exp=min_max&hospPromo=false&pt=33.9745,-118.2475&zc=90001&city=Los+Angeles&state=CA"
    
    # Scrape data
    doctor_profiles = parser.scrape_doctor_profiles(search_url)
    
    # Export the data
    output_path = os.path.join("data", "sample_output.json")
    exporter.export_to_json(doctor_profiles, output_path)

if __name__ == "__main__":
    main()