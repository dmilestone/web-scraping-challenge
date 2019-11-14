
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import pandas as pd

def init_browser():
    # Setting up windows browser with chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    return browser

def scrape():
    browser = init_browser()

    mars_data = {}

    #URL to be scraped
    url = 'https://mars.nasa.gov/news/'
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')

    results = soup.find_all('div', class_="content_title")

    # A blank list to hold the headlines
    news_titles = []
    # Loop over div elements
    for result in results:
        # Identify the anchor...
        if (result.a):
            # And the anchor has non-blank text...
            if (result.a.text):
                # Append thext to the list
                news_titles.append(result)
    
    finalnewstitles = []
    # Print only the headlines
    for x in range(6):
        var=news_titles[x].text
        newvar = var.strip('\n\n')
        finalnewstitles.append(newvar)

    #Find classification for description paragraph below title
    presults = soup.find_all('div', class_="rollover_description_inner")

    news_p = []
    # Loop through the div results to pull out just the text
    for x in range(6):
        var=presults[x].text
        newvar = var.strip('\n\n')
        news_p.append(newvar)
    
    #add titles and paragraphs to dictionary
    mars_data['news_titles'] = finalnewstitles
    mars_data['news_p'] = news_p



    #Mars Space Image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    html=browser.html
    soup = bs(html, 'html.parser')

    #using the footer to trace link to full image
    footer = soup.find('footer')
    link = footer.find('a')
    fornext = link['data-link']

    #going to next page
    base_url='https://www.jpl.nasa.gov'
    clicknext = base_url+fornext
    browser.visit(clicknext)

    html=browser.html
    soup = bs(html, 'html.parser')

    #accessing correct path for full image
    myfig = soup.find('figure',class_='lede')
    link = myfig.find('a')
    featured_image = link['href']

    featured_image_url = base_url+featured_image

    #add space image url to dictionary
    mars_data['featured_image_url'] = featured_image_url

    #Mars Weather
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    html=browser.html
    soup = bs(html, 'html.parser')
    
    #Grabbing weather data
    mars_weather = []
    weather = soup.find('div', class_='js-tweet-text-container')
    mars_weather = weather.text.strip()
    mars_data['mars_weather']=mars_weather


	#Mars Facts
    url = 'https://space-facts.com/mars/'
    response = requests.get(url)
    soup = bs(response.text, 'html.parser')

    tables = pd.read_html(url)
    marsdf = tables[0]
    
    #Naming columns
    marsdf.columns = ['Stat', 'Measurement']

    #fixing format
    s = pd.Series(marsdf['Stat'])
    marsdf['Stat'] = s.str.strip(':')
    marsdf = marsdf.set_index('Stat')

    #Use to_html method to generate HTML tables from df
    html_table = marsdf.to_html()

    #adding to dictionary
    mars_data["html_table"] = html_table


    #Mars Hemispheres
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    nextpage_urls = []
    imgtitles = []
    base_url = 'https://astrogeology.usgs.gov'

    # HTML object
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')
    # Retrieve all elements that contain hemisphere photo info
    divs = soup.find_all('div', class_='description')

    counter = 0
    for div in divs:
        # Use Beautiful Soup's find() method to navigate and retrieve attributes
        link = div.find('a')
        href=link['href']
        img_title = div.a.find('h3')
        img_title = img_title.text
        imgtitles.append(img_title)
        next_page = base_url + href
        nextpage_urls.append(next_page)
        counter = counter+1
        if (counter == 4):
            break

    # Creating loop for high resolution photo on next page
    my_images=[]
    for nextpage_url in nextpage_urls:
        url = nextpage_url
        browser.visit(url)
        html = browser.html
        soup = bs(html, 'html.parser')
        link2 = soup.find('img', class_="wide-image")
        forfinal = link2['src']
        full_img = base_url + forfinal
        my_images.append(full_img)
        nextpage_urls = []
    
    # Creating final list of dictionaries
    hemisphere_image_urls = []

    cerberus = {'title':imgtitles[0], 'img_url': my_images[0]}
    schiaparelli = {'title':imgtitles[1], 'img_url': my_images[1]}
    syrtis = {'title':imgtitles[2], 'img_url': my_images[2]}
    valles = {'title':imgtitles[3], 'img_url': my_images[3]}

    hemisphere_image_urls = [cerberus, schiaparelli, syrtis, valles]

    #adding to dict
    mars_data["hemisphere_image_urls"] = hemisphere_image_urls

    return mars_data

if __name__ == "__main__":
    scrape()