thonimport json

class DataExporter:
    def export_to_json(self, data, filepath):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data exported to {filepath}")