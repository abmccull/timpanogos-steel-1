import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('page_generation.log'),
        logging.StreamHandler()
    ]
)

class PageGenerator:
    def __init__(self, templates_dir, build_dir, data_dir):
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.build_dir = build_dir
        self.data_dir = data_dir
        self.batch_size = 100
        
        # Load configuration from environment variables or use defaults
        self.config = {
            'form_endpoint': os.getenv('FORM_ENDPOINT', 'https://script.google.com/macros/s/your-script-id/exec'),
            'recaptcha_site_key': os.getenv('RECAPTCHA_SITE_KEY', 'your-recaptcha-site-key'),
            'sentry_dsn': os.getenv('SENTRY_DSN', 'your-sentry-dsn'),
            'ga_tracking_id': os.getenv('GA_TRACKING_ID', 'your-ga-tracking-id'),
            'current_year': datetime.now().year
        }

        # Section configurations
        self.sections = {
            'residential': {'name': 'Residential', 'section': 'residential'},
            'commercial': {'name': 'Commercial', 'section': 'commercial'},
            'industrial': {'name': 'Industrial', 'section': 'industrial'},
            'agricultural': {'name': 'Agricultural', 'section': 'agricultural'}
        }

    def read_csv_data(self, filename):
        """Read and validate CSV data"""
        try:
            csv_path = os.path.join(self.data_dir, filename)
            logging.info(f"Reading CSV file from: {csv_path}")
            df = pd.read_csv(csv_path)
            
            required_columns = [
                'City', 'State', 'Latitude', 'Longitude',
                'Introduction', 'CityIntro',
                'ResidentialContent', 'CommercialContent',
                'IndustrialContent', 'AgriculturalContent'
            ]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            logging.info(f"Successfully read CSV with {len(df)} rows")
            return df
            
        except Exception as e:
            logging.error(f"Error reading CSV file: {str(e)}")
            raise

    def generate_filename(self, city, state):
        """Generate SEO-friendly filename for the city page"""
        city_slug = city.lower().replace(' ', '-')
        state_slug = state.lower().replace(' ', '-')
        return f"steel-buildings-{city_slug}-{state_slug}.html"

    def generate_page(self, row):
        """Generate a single page using the template and data"""
        try:
            template = self.env.get_template('base.html')
            
            # Get the page URL for form submission
            filename = self.generate_filename(row['City'], row['State'])
            page_url = f"https://timpanogos-steel.com/{filename}"
            
            # Prepare template variables
            context = {
                'city': row['City'],
                'state': row['State'],
                'latitude': row['Latitude'],
                'longitude': row['Longitude'],
                'hero_content': row['Introduction'],
                'city_intro': row['CityIntro'],
                'residential_static_content': self.get_static_content('residential'),
                'residential_dynamic_content': row['ResidentialContent'],
                'commercial_static_content': self.get_static_content('commercial'),
                'commercial_dynamic_content': row['CommercialContent'],
                'industrial_static_content': self.get_static_content('industrial'),
                'industrial_dynamic_content': row['IndustrialContent'],
                'agricultural_static_content': self.get_static_content('agricultural'),
                'agricultural_dynamic_content': row['AgriculturalContent'],
                'sections': self.sections,
                'page_url': page_url,  # Add page URL for form tracking
                **self.config
            }
            
            # Render the template
            html_content = template.render(**context)
            
            # Generate filename and save
            filepath = os.path.join(self.build_dir, filename)
            
            # Ensure build directory exists
            os.makedirs(self.build_dir, exist_ok=True)
            
            # Write the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logging.info(f"Generated page for {row['City']}, {row['State']}: {filename}")
            
        except Exception as e:
            logging.error(f"Error generating page for {row['City']}, {row['State']}: {str(e)}")
            raise

    def get_static_content(self, section):
        """Return static content for each section"""
        # This would typically load from a content management system or static files
        static_content = {
            'residential': """
                Our residential steel buildings offer durability and versatility 
                for homeowners seeking reliable storage solutions, workshops, or garages. 
                Built to withstand local weather conditions and engineered for maximum efficiency, 
                our structures provide the perfect blend of functionality and value.
            """,
            'commercial': """
                Businesses trust our commercial steel buildings for their 
                exceptional strength and adaptability. From retail spaces to warehouses, 
                our customizable designs meet diverse business needs while ensuring 
                compliance with local building codes and regulations.
            """,
            'industrial': """
                Industrial operations benefit from our robust steel building 
                solutions. Engineered for heavy-duty applications, our structures provide 
                the space and durability needed for manufacturing, storage, and processing 
                facilities while maintaining cost-effectiveness.
            """,
            'agricultural': """
                Farmers and ranchers rely on our agricultural steel buildings 
                for protecting livestock, storing equipment, and securing harvests. 
                Our designs incorporate features specifically tailored to agricultural 
                needs, ensuring long-lasting performance in rural environments.
            """
        }
        return static_content.get(section, '')

    def generate_all_pages(self, csv_filename):
        """Generate all pages in batches"""
        try:
            df = self.read_csv_data(csv_filename)
            total_pages = len(df)
            batches = range(0, total_pages, self.batch_size)
            
            logging.info(f"Starting generation of {total_pages} pages in batches of {self.batch_size}")
            
            for start in batches:
                end = min(start + self.batch_size, total_pages)
                batch_df = df.iloc[start:end]
                
                logging.info(f"Processing batch {start//self.batch_size + 1}: pages {start+1} to {end}")
                
                for _, row in batch_df.iterrows():
                    self.generate_page(row)
                
                logging.info(f"Completed batch {start//self.batch_size + 1}")
            
            logging.info("Page generation completed successfully")
            
        except Exception as e:
            logging.error(f"Error in generate_all_pages: {str(e)}")
            raise

def main():
    """Main execution function"""
    try:
        # Initialize paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        templates_dir = os.path.join(base_dir, 'templates')
        build_dir = os.path.join(base_dir, 'build')
        data_dir = os.path.join(base_dir, 'data')
        
        # Create generator instance
        generator = PageGenerator(templates_dir, build_dir, data_dir)
        
        # Generate pages
        generator.generate_all_pages('city_data_sample.csv')
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == '__main__':
    main()
