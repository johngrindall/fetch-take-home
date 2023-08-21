# fetch-take-home

## Introduction
Thank you for considering my application to Fetch! Here's my submission, feel free to reach out if you have any questions :) 

## Installation
- I've written the program in Python, so no need to install anything. Additionally the script will install all dependencies automatically from the requirements.txt file included in the repo.

## Usage
The project was designed to be run using python3, it includes 4 primary functions, outlined below.

- Usage: python3 AccessScript.py [options]

- Options:
  - help            Show This Help Message and Exit 
  - deleteSQS       Deletes SQS Messages Following Read
  - SQSCount        Displays # of Messages in SQS Queue and Exit
  - clearDB         Clears the Database Table of All Rows

  - Note: Running with no option will mask and add all records to the database   without deleting them from the SQS queue

- Example:
  python3 AccessScript.py deleteSQS

## Whats Next?

If I had more time to flush out this project there are a few things that I may have added/done to improve both the usability and and the functionality of my code.

- The first thing I'd have added would have been a user interface using Tkinter or a similar Python library. This interface could have a menu displaying items currently contained in the SQS queue as well as a parallel menu displaying records currently masked and stored in the PostgreSQL DB. This would alleviate the need to constantly check each DB, and make the application much more approachable for non-technical personel.
- I'd also add additional functionality in regards to automation, such at the ability to run the application and have it watch for new SQS messages, mask/delete them, and write them to the database automatically. This would enable the application to run as a standalone service. Who knows, perhaps with some tinkering it could even be Dockerized for additional portability.
  
## Deploying in a Production Environment.

I think that my second bullet point from above is actually a great first step towards bringing this application into a production environment. Automating the application and then creating a Docker image based on it would be a great way to manage dependencies and ease of deployability. It would also make the application easier to scale horizontally if more instances were needed.

## Scaling with a growing dataset.

Like I mentioned above, Dockerizing the application would allow for some horizontal scalability, but ultimately if the program needs to run on significantly larger datasets there are some efficiency improvements that I could make such as.

1. Compressing the masking and storage loops into a single loop so that the dataset is only traversed once. This was something that I did for readability sake given that the dataset in the assignment is fairly small. But merging these two loops would improve program performance on large datasets.
2. Explore re-writing in a different language. Being interpreted, Python is fairly topheavy, it also has very limited support for true-multithreading which inherently limits paralellization potential. Reconstructing the program in C would allow for better optimization.

## Recovering PII Data 

The application uses SHA-256 hashing to obscure data, this makes duplicate values noticable by analysts, while still making data accessible so long as we still have access to the original dataset in some fashion.

## Assumptions

The following are some assumptions that I made while developing my submission.

1. The user is somewhat tech savvy: In making the program a Python script I'm inherently assuming that the user is aware of how to run the script using a command line and has python 3.7 installed.
2. The user already has the Docker images included set up: I assumed that the user has an environment for which I am developing a ulility, therefore I did not include any instructions on how to install/configure the docker constainers.

