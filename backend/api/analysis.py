# api/analysis.py
import pandas as pd

def analyze_csv(csv_file):
    try:
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        required_cols = {'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            return None, f"Error: Missing required columns: {', '.join(missing)}"

        # Perform analysis
        summary = {
            'total_count': int(len(df)),
            'averages': {
                'flowrate_avg': round(df['Flowrate'].mean(), 2),
                'pressure_avg': round(df['Pressure'].mean(), 2),
                'temperature_avg': round(df['Temperature'].mean(), 2),
            },
            'type_distribution': df['Type'].value_counts().to_dict(),
            'raw_data': df.to_dict('records')
        }
        return summary, None
    except pd.errors.EmptyDataError:
        return None, "Error: The uploaded CSV file is empty."
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"