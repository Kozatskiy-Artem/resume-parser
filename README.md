# ResumeFinderBot

## Description

This project is developed to automate the job search process through popular resume search websites. 
It includes parsers for two well-known websites and a Telegram bot that allows users 
to specify search parameters and receive the most relevant results from both sources simultaneously.

## Stack

- Python 3.11
- Selenium
- Requests
- BeautifulSoup4
- PyTelegramBotApi

## Key Features

- Resume searcher and parser for work.ua website. 
- Resume searcher and parser for robota.ua website. 
- Telegram bot for resume search. 
- Ability to specify search parameters through the bot. 
- Retrieval of relevant resumes from both websites simultaneously.

## Installation Requirements

- Python 3.11
- Required libraries (specified in the requirements.txt file)
- Internet access
- Access token for Telegram API

## Installation and Usage Instructions

1. Clone the repository to your local machine. 
2. Add `.env` file in project with access token. 
3. Install the required libraries using the command ```pip install -r requirements.txt```. 
4. Run the bot using the command ```python main.py```. 
5. Interact with the bot by specifying the necessary search parameters.

## Usage Example

1. Start the bot. 
2. Send the `/start` command to initiate interaction.
3. Enter search parameters (e.g., position, location, salary expectations, etc.). 
4. Receive search results and select the most suitable job listings.

## All bot commands

- `/start` - Command to start bot.
- `/help` - Command to display a list of all available commands and their brief descriptions.
- `/check` - Command to display the specified parameters for resume search.
- `/clear` - Command to clear the specified parameters.
- `/find_on_work` - Command to perform a search for relevant resumes based on 
the previously specified parameters on the work.ua website.
- `/find_on_robota` - Command to perform a search for relevant resumes based on 
the previously specified parameters on the robota.ua website.
- `/find_on_all` - Command to perform a search for relevant resumes based on 
the previously specified parameters on both platforms.