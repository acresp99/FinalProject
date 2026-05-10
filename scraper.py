import pandas as pd


def scrape_us_states_population():
    """
    Scrapes US state population data from worldpopulationreview.com/states
    """
    URL = "https://worldpopulationreview.com/states"
    try:
        # Read all tables from the page
        tables = pd.read_html(URL)
        
        # The state population table is typically the first table
        df = tables[0]
        
        # Clean up column names - remove extra whitespace
        df.columns = df.columns.str.strip()
        
        # Keep only the desired columns: State, Population (2026 Pop.), and Annual Change
        columns_to_keep = [col for col in df.columns if 'State' in col or 'state' in col]
        # Find population column
        pop_col = [col for col in df.columns if '2026' in col or 'Pop' in col][0]
        # Find annual change column
        annual_col = [col for col in df.columns if 'Annual' in col or 'annual' in col][0]
        
        df = df[[columns_to_keep[0], pop_col, annual_col]].copy()
        
        # Rename for clarity
        df.columns = ['State', 'Population', 'Annual Change']
        
        # Create filename
        csv_filename = "state_pop.csv"
        
        # Save to CSV
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"✓ Successfully scraped data from {URL}")
        print(f"✓ Saved to: {csv_filename}")
        print(f"✓ Records extracted: {len(df)}")
        
        return True, csv_filename
        
    except Exception as e:
        print(f"✗ Error during scraping: {e}")
        return False, None


def display_sample_data(csv_filename, limit=10):
    """
    Displays sample data from the scraped CSV file
    """
    try:
        df = pd.read_csv(csv_filename)
        print(f"\n{'='*80}")
        print(f"Sample Data (first {limit} rows):")
        print(f"{'='*80}")
        print(df.head(limit).to_string(index=False))
        print(f"\nTotal rows in dataset: {len(df)}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")


if __name__ == "__main__":
    print("Starting US States Population Scraper...\n")
    
    # Scrape the data
    success, csv_filename = scrape_us_states_population()
    
    # Display sample if successful
    if success and csv_filename:
        display_sample_data(csv_filename, limit=15)
