# Web-scraping-AWS
Guide for Web Scraping with Python + AWS Services. Build your own dataset!

## Intro
This project will guide you on how to Web Scrape an e-commerce page and store the date into a managed SQL database service using Python and some AWS Services. (We are not dealing with Anti-Scraping tools)

## Goal
Help data science enthusiasts with web scraping and AWS services, also encourage them building and sharing their own datasets.

## Previous knowledge
Some knowledge is mandatory to understand and pass through this project, I strongly recommend having the knowledge above:
- SQL fundamentals (how to create a table, extract and store data using SQL);
- Python fundamentals;
- Pandas fundamentals;
- Python virtual environments;
- HTML fundamentals (knowing how to use the browser's console to identify html elements is enough).

## Web Scraping
This is the first fase of this project, we will manage to extract data from a Brazilian online car selling platform (Web motors). To accomplish that, we will use a Python library called Beautiful Soup, all the code is detailed and even illustrated on "Webscraping webmotors.ipynb" notebook

Firstly I recommend creating a new Python virtual enviroment before start coding, in the future steps to deploy your solution on a cloud service you'll want to upload only the required libs. You can take a look [here](https://learnpython.com/blog/change-python-versions/) to learn how to do that.

A key step for web scrapping is mapping which data you need to get and identify how they're loaded on the page's HTML. If you have no ideia on how doing that, check [this article](https://blog.hubspot.com/website/how-to-inspect#:~:text=Right%2Dclicking%20a%20specific%20page,choose%20More%20Tools%20%3E%20Developer%20Tools.). To help you undertanding the HTML's elements used an as it can change over time as the web page developer's can update the site, on "Page elements ref.pdf" file I show how 
