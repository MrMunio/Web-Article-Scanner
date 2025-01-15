import os
import json
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urlparse
import re
import requests
from duckduckgo_search import DDGS
from openai import OpenAI

class ArticleCollector:
    def __init__(self, openai_api_key,wkhtmltopdf_path):
        self.openai_api_key = openai_api_key
        self.wkhtmltopdf_path= wkhtmltopdf_path

    def generate_search_queries(self, domain_description, num_queries=5):
        """Generate relevant search queries using GPT"""
        print(f"generating {num_queries} search queies using openai")
        client = OpenAI(api_key=self.openai_api_key)
        prompt = f"""Generate  exactly {num_queries} search queries (each query under 10 words) for finding research papers and articles about:
        {domain_description}try to be enthusiastic and give diverse queries in this domain. if user queries are very specific then use that query along with few other closely related queries.
        Return only a JSON array of objects with 'query' field, no markdown formatting or other text."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        content = content.replace('```json', '').replace('```', '').strip()
        
        try:
            queries = json.loads(content)
            if isinstance(queries, list) and all(isinstance(q, dict) for q in queries):
                return [q['query'] for q in queries]
            return queries
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw content: {content}")
            return [
                "Chemical bond studies in cheminformatics",
                "Drug discovery research papers chemical industry",
                "Cheminformatics studies recent papers",
                "Chemical bonding mechanisms drug design",
                "Chemical industry research articles"
            ]

    def search_articles(self, query, num_results=10):
        """Search for articles using free DUCKDUCKGO Search API"""
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=num_results)
                return [{"link": result['href']} for result in results]
        except Exception as e:
            print(f"Error searching for {query}: {str(e)}")
            return []
        

    def validate_url(self, url):
        """Validate if URL is suitable for scraping and ensure it has dense text data."""
        parsed = urlparse(url)
        blocked_domains = ['youtube.com', 'facebook.com', 'twitter.com']

        # Check for blocked domains
        if any(domain in parsed.netloc for domain in blocked_domains):
            return False

        try:
            # Fetch content and check text density
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            word_count = len(text.split())
            text_density = word_count / len(text) if len(text) > 0 else 0

            # Consider valid if it has a minimum of 500 words and dense text
            return word_count > 3000 and text_density > 0.1

        except Exception as e:
            print(f"Error validating URL {url}: {e}")
            return False


    def convert_to_pdf(self,url, output_path):
        """Convert webpage to PDF using pdfkit"""
        # Clean URL for filename (removes invalid characters)
        cleaned_url = re.sub(r'[\\/*?:"<>|]', '-', url)
        filename = cleaned_url[:100]  # Limit filename length for safety
        pdf_path = os.path.join(output_path, f"{filename}.pdf")
        try:
            config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)

            # Convert to PDF
            pdfkit.from_url(url, pdf_path, configuration=config)
            print(f"URL converted to PDF and saved to: {pdf_path}")
            return pdf_path
    
        except Exception as e:
            print(f"Error converting {url} to PDF: {str(e)}. Checking if URL is a direct PDF file...")
            
            try:
                # Check if the URL is a direct PDF file
                response = requests.head(url)
                if response.headers.get("Content-Type") == "application/pdf":
                    response = requests.get(url)
                    with open(pdf_path, "wb") as file:
                        file.write(response.content)
                    print(f"PDF file downloaded directly to: {pdf_path}")
                    return pdf_path
                else:
                    print("URL is not a direct PDF file.")
                    return None
            except Exception as e:
                print(f"Error while verifying or downloading PDF: {str(e)}")
                return None
        

    def collect_articles(self, domain_description, output_dir, num_articles=50):
        """Main method to collect and convert articles"""
        articles_per_query=5 #adjust this paramenter
        if num_articles<articles_per_query:
            articles_per_query=num_articles

        num_search_res = articles_per_query * 5 # no need to change its a reasonalbe ratio.asuming it takes 5 urls to find one decent article.
        num_queries=num_articles//articles_per_query
        if num_queries <1:
            num_queries=1

        os.makedirs(output_dir, exist_ok=True)
        collected_urls = set()
        results = []
        
        queries = self.generate_search_queries(domain_description, num_queries=num_queries)
        print(f"Generated {len(queries)} queries: {queries}")
        
        for query in queries:
            print(f"\nProcessing query: {query}")
            if len(collected_urls) >= num_articles:
                break
            enhanced_query = query+" a detailed Article or research paper or journal"
            articles = self.search_articles(enhanced_query,num_results=num_search_res) # mention you need a detailed article.
            print(f"Found {len(articles)} articles for query")
            count_for_each_query = 0
            for article in articles:
                url = article.get('link')
                if url and url not in collected_urls and self.validate_url(url):
                    print(f"\nProcessing URL: {url}")
                    pdf_path = self.convert_to_pdf(url, output_dir)
                    if pdf_path:
                        print(f"Successfully created PDF: {pdf_path}")
                        results.append({
                            'title': article.get('title'),
                            'url': url,
                            'pdf_path': pdf_path
                        })
                        yield {  
                        'title': article.get('title'),
                        'url': url,
                        'pdf_path': pdf_path
                        }
                        collected_urls.add(url)
                        count_for_each_query+=1
                        print(f"collected urls: {len(collected_urls)}/{num_articles}") 
                        if count_for_each_query >articles_per_query: # limiting to collect only 5 articles for each query topic.
                            print("quoto completed for query:",query)
                            break
                    else:
                        print("Failed to create PDF")
                   
                if len(collected_urls) >= num_articles:
                    print(f" target reached  :{len(collected_urls)}/{num_articles} articles collected. stopping prematurely!")
                    return results
                    
        print(f"\nCollection ended. Generated {len(collected_urls)} PDFs")
        if len(collected_urls)< num_articles:
            print("restarting the process to collect remaing documents...")
            rem_art=num_articles-len(collected_urls)
            results = results+self.collect_articles(domain_description, output_dir, num_articles=rem_art)
        elif len(collected_urls)== num_articles:
            print(f"Required count of documnets {len(results)}/{num_articles} collected successfully")
            return results
        print(f"exiting the main process : {len(results)}/{num_articles} collected successfully")
        return results

# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    OUTPUT_DIR = "collected_articles_3"
    
    collector = ArticleCollector(OPENAI_API_KEY)
    
 
    DOMAIN = "documents related to, chemical industries/Drug discovery/chemo-Informatics(Study of chemical bond and related subjects) and side effects of some drugs or rare diseases on various demographics"

    # Collect articles
    results = collector.collect_articles(DOMAIN, OUTPUT_DIR, num_articles=10)
    
    # Save results metadata
    with open(os.path.join(OUTPUT_DIR, 'collection_results.json'), 'w') as f: json.dump(results, f, indent=2)