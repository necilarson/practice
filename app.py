from flask import Flask, render_template, request, redirect
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

def process_data(df):
    # Data processing and analysis code
    df['Strain'] = df['Product'].str.split('(').str[0]
    split_columns = df['Product Line'].str.split('(', expand=True)
    df['Device'] = split_columns[0]
    df['Type'] = split_columns[1].str.rstrip(')')
    selected_columns = df[['Strain', 'Device', 'Type', 'Amount Sold (Units)']]

    # Perform analysis...
    total_sold_units_by_strain = selected_columns.groupby('Strain')['Amount Sold (Units)'].sum().sort_values(ascending=False)
    total_sold_units_by_type = selected_columns.groupby('Type')['Amount Sold (Units)'].sum().sort_values(ascending=False)
    total_sold_units_by_device = selected_columns.groupby('Device')['Amount Sold (Units)'].sum().sort_values(ascending=False)
    grouped_data = selected_columns.groupby(['Device', 'Type'])['Amount Sold (Units)'].sum().reset_index()
    pivot_table = grouped_data.pivot_table(index='Device', columns='Type', values='Amount Sold (Units)', fill_value=0)
    pivot_table = pivot_table.astype(int)
    pivot_table.index.name = None
    pivot_table.columns.name = None
    pivot_table.fillna(0, inplace=True)

    # Generate bar charts
    plt.figure(figsize=(18, 6))
    total_sold_units_by_strain.plot(kind='barh', color='#44B314', edgecolor='#245433')
    plt.title('Total Sold Units by Strain')
    plt.xlabel('Total Sold Units')
    plt.ylabel('Strain')
    plt.tight_layout()
    # Save the plot to a BytesIO object
    plot_bytes = BytesIO()
    plt.savefig(plot_bytes, format='png')
    plot_bytes.seek(0)
    # Encode the plot as base64 string
    plot_base64 = base64.b64encode(plot_bytes.getvalue()).decode('utf-8')

    # Return processed data and visualizations
    return total_sold_units_by_strain, total_sold_units_by_type, total_sold_units_by_device, pivot_table, plot_base64

@app.route('/', methods=['GET', 'POST'])
def pow_demo():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Read the uploaded CSV file
            df = pd.read_csv(file)
            # Process the data
            total_sold_units_by_strain, total_sold_units_by_type, total_sold_units_by_device, pivot_table, plot_base64 = process_data(df)
            # Render the result template with the processed data and visualizations
            return render_template('result.html', 
                                    total_sold_units_by_strain=total_sold_units_by_strain,
                                    total_sold_units_by_type=total_sold_units_by_type,
                                    total_sold_units_by_device=total_sold_units_by_device,
                                    pivot_table=pivot_table,
                                    plot_base64=plot_base64)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)