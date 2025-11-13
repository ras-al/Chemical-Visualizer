import pandas as pd
import io

def process_csv_file(file_obj):
    try:
        file_data = file_obj.read().decode('utf-8-sig')
        data_io = io.StringIO(file_data)
        df = pd.read_csv(data_io)

    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")

    # Perform Data Analysis
    
    # 1. Check for required columns
    required_cols = {'Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

    # 2. Perform analysis as required by the project
    try:
        summary_data = {
            'total_count': int(len(df)),
            'averages': {
                'flowrate_avg': round(df['Flowrate'].mean(), 2),
                'pressure_avg': round(df['Pressure'].mean(), 2),
                'temperature_avg': round(df['Temperature'].mean(), 2),
            },
            'type_distribution': df['Type'].value_counts().to_dict()
        }
        
        return summary_data
        
    except pd.errors.EmptyDataError:
        raise ValueError("The CSV file is empty.")
    except Exception as e:
        raise ValueError(f"Error during data analysis: {str(e)}")