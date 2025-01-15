from django.shortcuts import render

# Create your views here.


def homepage(request):
    # Clear uploaded data from the session
    if 'dataframe' in request.session:
        del request.session['dataframe']
    if 'current_file' in request.session:
        del request.session['current_file']

    return render(request, 'homepage.html')



from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import FileUploadForm
from .models import UploadedFile
from django.shortcuts import redirect
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px # For interactive plots

def upload_file(request):
    data_preview = None  # For displaying a preview of the data in the template 
    row_data = None  # For storing the row data
    column_data = None  # For storing the column data
    current_file = None  # For storing the name of the currently uploaded file
    data_len = None  # to displaying the length of the uploaded data
    stats = None # For storing the summary statistics of the data
    all_columns = None # For storing all the columns in the DataFrame
    numeric_columns = None # For storing the numeric columns in the DataFrame
    
    
    # Initialize the form to avoid unbound variable issues
    form = FileUploadForm()

    # Check if there's already an uploaded file in the session
    if 'current_file' in request.session:
        current_file = request.session['current_file']
        if 'dataframe' in request.session:
            df = pd.read_json(request.session['dataframe'])
            data_preview = df.head().to_html()
            data_len = len(df)
            all_columns = df.columns.tolist()
            numeric_columns = df.select_dtypes(include='number').columns.tolist()




    if request.method == 'POST': # POST request to upload file (create new file)
        if 'action' in request.POST:
            # Handle row/column retrieval
            action = request.POST.get('action')
            if 'dataframe' in request.session:
                   # Deserialize the DataFrame from JSON stored in session
                df = pd.read_json(request.session['dataframe'])

                if action == 'get_row':
                    row_index = int(request.POST.get('row_index'))
                    if 0 <= row_index < len(df):
                        row_data = df.iloc[row_index].to_frame().T.to_html()
                    else:
                        row_data = "<p style='color:red;'>Row index out of range.</p>"
                elif action == 'get_column':
                    column_name = request.POST.get('column_name')
                    if column_name in df.columns:
                        column_data = df[column_name].to_frame().to_html()
                    else:
                        column_data = "<p style='color:red;'>Column not found.</p>"
                elif action == 'compute_stats':
                    stat_column = request.POST.get('stat_column')
                    if stat_column in df.columns:
                        try:
                            stats = {
                                'column': stat_column,
                                'mean': df[stat_column].mean(),
                                'median': df[stat_column].median(),
                                'std': df[stat_column].std(),
                                'min': df[stat_column].min(),
                                'max': df[stat_column].max(),
                            }
                        except Exception as e:
                            stats = {'error': f"Could not compute statistics: {e}"}
                    else:
                        stats = {
                            'error': f"Column '{stat_column}' not found or invalid."
                        }


            else:
                row_data = "<p style='color:red;'>No data available. Please upload a CSV file.</p>"
        else:
            # Handle file upload  
            form = FileUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.save()  # Save the file to the database and media folder
                # Read the uploaded CSV file using pandas
                file_path = uploaded_file.file.path  # Get the file path
                
                try:
                    df = pd.read_csv(file_path)  # Read the CSV file into a pandas DataFrame
                    # Store the DataFrame as JSON in the session
                    request.session['dataframe'] = df.to_json()
                    request.session['current_file'] = uploaded_file.name  # Store the file name
                    request.session['all_columns'] = df.columns.tolist()
                    request.session['numeric_columns'] = df.select_dtypes(include='number').columns.tolist()

                    current_file = uploaded_file.name  # Update the current file
                    data_preview = df.head().to_html()  # Convert the first 5 rows to HTML for preview
                    data_len = len(df) # Get the total number of rows
                    
                except Exception as e:
                    return render(request, 'upload.html', {
                        'form': form,
                        'error': f"Error reading CSV file: {e}"
                    })

    return render(request, 'upload.html', {
        'form': form,
        'current_file': current_file,
        'data_preview': data_preview,
        'data_len': data_len,
        'row_data': row_data,
        'column_data': column_data,
        'stats': stats,
        'all_columns': all_columns,
        'numeric_columns': numeric_columns,
    })
 




import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DataVisualizer:
    THEME_COLORS = {
        'background': '#0a0a0a',
        'paper': '#141414',
        'primary': '#b14eef',
        'secondary': '#8a2be2',
        'text': '#ffffff',
        'grid': '#2a2a2a'
    }
    
    @classmethod
    def create_figure_template(cls):
        """Create a custom dark theme template for plots"""
        template = go.layout.Template()
        template.layout = go.Layout(
            paper_bgcolor=cls.THEME_COLORS['paper'],
            plot_bgcolor=cls.THEME_COLORS['background'],
            font={'color': cls.THEME_COLORS['text']},
            xaxis={
                'gridcolor': cls.THEME_COLORS['grid'],
                'linecolor': cls.THEME_COLORS['grid'],
                'zerolinecolor': cls.THEME_COLORS['grid']
            },
            yaxis={
                'gridcolor': cls.THEME_COLORS['grid'],
                'linecolor': cls.THEME_COLORS['grid'],
                'zerolinecolor': cls.THEME_COLORS['grid']
            }
        )
        return template

    @classmethod
    def generate_visualization(cls, df, column, vis_type):
        """Generate visualization with consistent styling"""
        template = cls.create_figure_template()
        
        try:
            if vis_type == 'histogram':
                fig = px.histogram(
                    df,
                    x=column,
                    title=f'Distribution of {column}',
                    template=template,
                    color_discrete_sequence=[cls.THEME_COLORS['primary']],
                    marginal='violin'
                )
                
            elif vis_type == 'scatter':
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                x_col = next((col for col in numeric_cols if col != column), None)
                
                if x_col:
                    fig = px.scatter(
                        df,
                        x=x_col,
                        y=column,
                        title=f'{column} vs {x_col}',
                        template=template,
                        color_discrete_sequence=[cls.THEME_COLORS['primary']],
                        trendline='ols'
                    )
                else:
                    raise ValueError("Need at least two numeric columns for scatter plot")
                
            elif vis_type == 'box':
                fig = px.box(
                    df,
                    y=column,
                    title=f'Box Plot of {column}',
                    template=template,
                    color_discrete_sequence=[cls.THEME_COLORS['primary']]
                )
                
            elif vis_type == 'bar':
                fig = px.bar(
                    df,
                    x=df.index,
                    y=column,
                    title=f'Bar Chart of {column}',
                    template=template,
                    color_discrete_sequence=[cls.THEME_COLORS['primary']]
                )

            # Common layout updates
            fig.update_layout(
                title_x=0.5,
                title_font_size=24,
                showlegend=False,
                hoverlabel=dict(
                    bgcolor=cls.THEME_COLORS['paper'],
                    font_size=14,
                    font_color=cls.THEME_COLORS['text']
                )
            )

            return fig.to_html(
                full_html=False,
                config={
                    'responsive': True,
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                }
            )

        except Exception as e:
            raise Exception(f"Visualization error: {str(e)}")

# Update your visualize view function:
def visualize(request):
    visualization = None
    vis_error = None
    all_columns = None # For storing all the columns in the DataFrame


    if 'dataframe' in request.session:
        df = pd.read_json(request.session['dataframe'])
        all_columns = request.session.get('all_columns', [])


        if request.method == 'POST':
            vis_column = request.POST.get('vis_column')
            vis_type = request.POST.get('vis_type')
            

            if vis_column in df.columns:
                try:
                    visualization = DataVisualizer.generate_visualization(
                        df, vis_column, vis_type
                    )
                except Exception as e:
                    vis_error = str(e)
            else:
                vis_error = f"Column '{vis_column}' not found."
    else:
        vis_error = "No data available. Please upload a CSV file first."

    return render(request, 'visualization.html', {
        'visualization': visualization,
        'vis_error': vis_error,
        'all_columns': all_columns,
    })



"""
def visualize(request):
    visualization = None
    vis_error = None
    # Check if there's data in the session
    if 'dataframe' in request.session:
        df = pd.read_json(request.session['dataframe'])

        if request.method == 'POST':
            vis_column = request.POST.get('vis_column')
            vis_type = request.POST.get('vis_type')

            if vis_column in df.columns:
                try:
                    # Generate the selected visualization
                    if vis_type == 'histogram':
                        fig = px.histogram(df, x=vis_column, title=f"Histogram for {vis_column}", marginal="rug")
                    elif vis_type == 'scatter':
                        other_col = df.select_dtypes(include='number').columns.difference([vis_column]).to_list()
                        if other_col:
                            fig = px.scatter(df, x=other_col[0], y=vis_column, title=f"Scatter Plot for {vis_column}")
                        else:
                            vis_error = "Not enough numeric columns for scatter plot."
                    elif vis_type == 'bar':
                        fig = px.bar(df, x=vis_column, title=f"Bar Chart for {vis_column}")
                    elif vis_type == 'box':
                        fig = px.box(df, y=vis_column, title=f"Box Plot for {vis_column}")

                    # Convert the Plotly figure to HTML
                    visualization = fig.to_html(full_html=False)
                except Exception as e:
                    vis_error = f"Error generating visualization: {e}"
            else:
                vis_error = f"Column '{vis_column}' not found."

    else:
        vis_error = "No data available. Please upload a CSV file first."

    return render(request, 'visualization.html', {
        'visualization': visualization,
        'vis_error': vis_error,
    })

"""