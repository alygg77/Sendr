from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field

# Initialize the FirecrawlApp with your API key
app = FirecrawlApp(api_key='fc-00f55c1d16ed4ca5866f68ad393261ba')
def get_description(link):
    class ExtractSchema(BaseModel):
        about: str

    data = app.scrape_url(link, {
        'formats': ['extract'],
        'extract': {
            "prompt": "Write a comprehensive and detailed description about the company."
        }
    })
    return str(data ["extract"]["company"])[0:500]


