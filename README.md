# Web-scraping-AWS
Guide for Web Scraping with Python + AWS Services. Build your own dataset!


## Intro
This project will guide you how to Web Scrape an e-commerce page and store the date into a managed SQL database service using Python and some AWS Services. (We are not dealing with Anti-Scraping tools)


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
This is the first phase of this project, we will manage to extract data from a Brazilian online car selling platform (Web motors). To accomplish that, we will use a Python library called Beautiful Soup, all the code is detailed and even illustrated on "[Webscraping webmotors.ipynb](https://github.com/magnunn/cloud-web-scraping/blob/main_english/Webscraping%20webmotors.ipynb)" notebook

Firstly, I recommend creating a new Python virtual environment before start coding, in the future steps to deploy your solution to a cloud service you'll want to upload only the required libs. You can take a look [here](https://learnpython.com/blog/change-python-versions/) to learn how to do that.

A key step for web scrapping is mapping which data you need to get and identify how they're loaded on the page's HTML. If you have no idea on how doing that, check [this article](https://blog.hubspot.com/website/how-to-inspect#:~:text=Right%2Dclicking%20a%20specific%20page,choose%20More%20Tools%20%3E%20Developer%20Tools.). To help you  understand the HTML's elements used an as it can change over time as the web page developer's can update the site, in the "[html_elements_ref.pdf](https://github.com/magnunn/cloud-web-scraping/blob/main_english/instructions/html_elements_ref.pdf)" file I show how 


## Creating a cloud DB Instance
For storing our data, we're going to use AWS RDS (Relational Database Service). All steps are described in the "[create_aws_db_rds.pdf](https://github.com/magnunn/cloud-web-scraping/blob/main_english/instructions/create_aws_db_rds.pdf)" file.

## Dealing with sensitive data and editable configurations
It's  not a good idea keeping into your python scripts sensitive data, such as users, passwords and endpoint address, especially if you will be sharing your project somewhere. Also for some configurations into your script that may require constant updates a good idea is using "configparser" lib, with it you can use a ".ini" file to store values for your variables, here is a [short guide](https://zetcode.com/python/configparser/) to use configparser lib.

Our "[config.ini](https://github.com/magnunn/cloud-web-scraping/blob/main_english/config.ini)" file keep two kind of data. First, we configure it with the classes of web elements used for scraping (I notice that from time to time it changes in minor updates), and second sensitive data from our DB instance (user, password, host...).


## Rewriting the code
If you are considering deploying this solution, it's necessary rewriting this code from a notebook's didactic structure to a a deployable code. In the "[webscraping_webmotors.py](https://github.com/magnunn/cloud-web-scraping/blob/main_english/webscraping_webmotors.py)" file we have a rewritten the code using most of python best practices, [here](https://data-flair.training/blogs/python-best-practices/) there are plenty of tips. 

In the final part of this code, it was added "upload_aws" function, that is responsible for connecting and uploading data to AWS, and also a final session to help validating if the data was uploaded or not.


## Building a Docker image and uploading to AWS
To make it possible running our code in a cloud environment, such as AWS's Lambda Functions, we shall some how replicate all python's dependencies from our project, Docker is a tool that enables users to publish and share container-based applications, and AWS ECR (Elastic Container Registry) is where we can upload this image to replicate on AWS services all our python environment.

All steps from building an image to push it to AWS can be followed in "[dealing_with_container_image.pdf](https://github.com/magnunn/cloud-web-scraping/blob/main_english/instructions/dealing_with_container_image.pdf)" file. 


## Deploying and scheduling Lambda Function
Finally, the most expected moment, deploying it in a production environment. We are going to use the AWS Lambda service, once it is quite easy to implement and can handle a relatively simple script like this (Lambdas biggest limitation is having a maximum timeout of 15 minutes). And probably it's also desired to schedule this function to run from times to times, this schedule will be made with AWS EventBridge. All steps are listed in "[creating_scheuling_lambda_function.pdf](https://github.com/magnunn/cloud-web-scraping/blob/main_english/instructions/creating_scheuling_lambda_function.pdf)" file.


## AWS billing cautions
Even all these AWS services being free, at least in the first 12 months, they have their "free limits", above I list some important follow ups to mitigate unwanted billings:
  - Always take a look at the AWS Billing Dashboard, there you can find "Free tier" session, which give us a forecast if we are going to use more than the free tier supports.
  - Make sure that you are always closing the SQL connection, AWS RDS has a maximum time connection limit.
  - Be careful with script errors and Lambdas settings, script errors may cause Lambda Function trying to repeat and execute the code multiple times overusing its time limit. you may consider changing at functions configuration the "Retry attempts" to zero.
