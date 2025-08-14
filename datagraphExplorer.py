import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import StringIO
import os
from scipy import stats

def load_csv():
    """Load CSV data from various sources with improved error handling."""
    print("=== Data Graph Explorer ===")
    print("Choose how to load your CSV file:")
    print("1. Upload from local computer")
    print("2. Enter URL")
    print("3. Use hardcoded URL in code")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        file_path = input("Enter the local file path: ").strip()
        if not os.path.exists(file_path):
            print("File not found!")
            return None
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
    
    elif choice == "2":
        url = input("Enter the CSV file URL: ").strip()
        return load_from_url(url)
        
    elif choice == "3":
        # Change this URL to whatever dataset you want to hardcode
        hardcoded_url = "https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv"
        print(f"Loading from: {hardcoded_url}")
        return load_from_url(hardcoded_url)
    else:
        print("Invalid choice!")
        return None

def load_from_url(url):
    """Helper function to load CSV from URL with better error handling."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except requests.exceptions.Timeout:
        print("Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error loading CSV from URL: {e}")
        return None
    except Exception as e:
        print(f"Error parsing CSV data: {e}")
        return None

def explore_dataframe(df):
    """Explore dataframe structure and content."""
    print("\n=== Data Preview ===")
    print(f"Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("\nFirst 3 rows:")
    print(df.head(3))
    
    print("\n=== Data Types ===")
    for col in df.columns:
        dtype = df[col].dtype
        non_null_count = df[col].count()
        null_count = df[col].isnull().sum()
        print(f"{col}: {dtype} ({non_null_count} non-null, {null_count} null)")
    
    column_names = list(df.columns)
    print(f"\nAvailable columns: {column_names}")
    return column_names

def get_numeric_columns(df):
    """Get list of numeric columns for plotting."""
    return df.select_dtypes(include=[np.number]).columns.tolist()

def analyze_relationship(x, y, col_names):
    """Provide statistical analysis of the relationship between variables."""
    print("\n=== Statistical Analysis ===")
    
    # Basic statistics
    print(f"{col_names[0]} - Mean: {np.mean(x):.2f}, Std: {np.std(x):.2f}")
    print(f"{col_names[1]} - Mean: {np.mean(y):.2f}, Std: {np.std(y):.2f}")
    
    # Correlation analysis
    if len(x) > 1 and len(y) > 1:
        correlation = np.corrcoef(x, y)[0, 1]
        if not np.isnan(correlation):
            print(f"Correlation coefficient: {correlation:.3f}")
            
            if abs(correlation) > 0.7:
                strength = "strong"
            elif abs(correlation) > 0.3:
                strength = "moderate"
            else:
                strength = "weak"
            
            direction = "positive" if correlation > 0 else "negative"
            print(f"This indicates a {strength} {direction} relationship.")
    
    # Trend analysis
    if len(y) > 2:
        slope, intercept, r_value, p_value, std_err = stats.linregress(range(len(y)), y)
        if abs(slope) > 0.01:  # Threshold for detecting trend
            trend_direction = "increasing" if slope > 0 else "decreasing"
            print(f"Overall trend: {trend_direction} (slope: {slope:.4f})")
        else:
            print("Overall trend: relatively stable")

def select_and_plot(df, column_names):
    """Interactive plotting function with enhanced features."""
    numeric_cols = get_numeric_columns(df)
    
    if len(numeric_cols) == 0:
        print("No numeric columns found for plotting!")
        return
    
    print(f"\nNumeric columns available for plotting: {numeric_cols}")
    
    while True:
        print(f"\nAll columns: {column_names}")
        print(f"Numeric columns: {numeric_cols}")
        cols = input("Enter 1 or 2 column names separated by commas (or 'q' to quit): ").strip()
        
        if cols.lower() == 'q':
            break
        
        selected_cols = [c.strip() for c in cols.split(",")]
        
        if not all(c in column_names for c in selected_cols):
            print("Invalid column names. Try again.")
            continue
        
        # Handle missing values
        df_clean = df[selected_cols].dropna()
        if df_clean.empty:
            print("No data available after removing missing values.")
            continue
        
        # Prepare data for plotting
        if len(selected_cols) == 1:
            x = np.arange(len(df_clean[selected_cols[0]]))
            y = df_clean[selected_cols[0]].values
            x_label = "Index"
            y_label = selected_cols[0]
        elif len(selected_cols) == 2:
            x = df_clean[selected_cols[0]].values
            y = df_clean[selected_cols[1]].values
            x_label = selected_cols[0]
            y_label = selected_cols[1]
        else:
            print("You can only select 1 or 2 columns.")
            continue
        
        # Choose graph type
        print("Available plot types:")
        print("1. scatter - Scatter plot")
        print("2. line - Line plot")
        print("3. hist - Histogram (single column only)")
        print("4. bar - Bar chart")
        
        plot_choice = input("Enter plot type (scatter/line/hist/bar): ").strip().lower()
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        if plot_choice == "scatter":
            plt.scatter(x, y, alpha=0.6)
            # Add trend line for scatter plots with numeric data
            if len(selected_cols) == 2 and all(col in numeric_cols for col in selected_cols):
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                plt.plot(x, p(x), "r--", alpha=0.8, label=f'Trend line (slope: {z[0]:.3f})')
                plt.legend()
                
        elif plot_choice == "line":
            plt.plot(x, y, marker='o', linewidth=2, markersize=4)
            
        elif plot_choice == "hist":
            if len(selected_cols) == 1:
                plt.hist(y, bins=20, alpha=0.7, edgecolor='black')
                plt.ylabel('Frequency')
            else:
                print("Histogram only works with single column. Using scatter plot instead.")
                plt.scatter(x, y, alpha=0.6)
                
        elif plot_choice == "bar":
            if len(y) > 50:
                print("Too many data points for bar chart. Showing first 50.")
                x, y = x[:50], y[:50]
            plt.bar(range(len(y)), y)
            
        else:
            print("Invalid plot type, defaulting to scatter.")
            plt.scatter(x, y, alpha=0.6)
        
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(f"{plot_choice.capitalize()} Plot: {' vs '.join(selected_cols)}")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        
        # Enhanced interpretation
        if len(selected_cols) == 2 and all(col in numeric_cols for col in selected_cols):
            analyze_relationship(x, y, selected_cols)
        else:
            print("\n=== Basic Analysis ===")
            if len(selected_cols) == 1:
                print(f"Column '{selected_cols[0]}' statistics:")
                print(f"  Min: {np.min(y):.2f}")
                print(f"  Max: {np.max(y):.2f}")
                print(f"  Mean: {np.mean(y):.2f}")
                print(f"  Median: {np.median(y):.2f}")

def main():
    """Main function to orchestrate the data exploration workflow."""
    df = load_csv()
    if df is not None:
        column_names = explore_dataframe(df)
        select_and_plot(df, column_names)
    print("Goodbye!")

if __name__ == "__main__":
    main()