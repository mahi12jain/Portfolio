import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Starting URL
start_url = "http://www.ericwadkins.com/"  # Replace with your target URL
base_domain = urlparse(start_url).netloc  # Restrict to the base domain
output_dir = r"C:\Users\Jain\OneDrive\Desktop\Python\html"  # Directory to save files

# Track visited URLs
visited_urls = set()

# Create output directory
os.makedirs(output_dir, exist_ok=True)

def save_file(content, filepath):
    """Save content to a file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as file:
        file.write(content)

def download_resource(resource_url, base_dir):
    """Download and save a resource (CSS, JS, Image)."""
    try:
        response = requests.get(resource_url, stream=True)
        response.raise_for_status()

        # Generate a file path
        parsed_url = urlparse(resource_url)
        filepath = os.path.join(base_dir, parsed_url.path.lstrip("/"))

        # Save the file
        save_file(response.content, filepath)
        print(f"Downloaded: {resource_url} -> {filepath}")
    except Exception as e:
        print(f"Failed to download resource {resource_url}: {e}")

def save_html_and_resources(url, soup):
    """Save HTML and its associated resources."""
    parsed_url = urlparse(url)
    page_dir = os.path.join(output_dir, parsed_url.path.lstrip("/"))
    os.makedirs(page_dir, exist_ok=True)

    # Save HTML file
    html_path = os.path.join(page_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as file:
        file.write(soup.prettify())
    print(f"Saved HTML: {url} -> {html_path}")

    # Download CSS, JS, and images
    for tag, attr in [("link", "href"), ("script", "src"), ("img", "src")]:
        for element in soup.find_all(tag, {attr: True}):
            resource_url = urljoin(url, element[attr])
            download_resource(resource_url, output_dir)

def crawl(url):
    """Recursively crawl pages and download resources."""
    if url in visited_urls:
        return
    visited_urls.add(url)

    try:
        print(f"Fetching: {url}")
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        save_html_and_resources(url, soup)

        # Extract and crawl links
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            if urlparse(full_url).netloc == base_domain:  # Stay within domain
                crawl(full_url)

    except Exception as e:
        print(f"Failed to fetch {url}: {e}")

# Start crawling
crawl(start_url)
print("Crawling completed!")
