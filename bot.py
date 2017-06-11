import twitter
import logging
from re import sub
from time import sleep


def oauth_login(filename):
    """
    Authorize app access to the Twitter API.

    Args:
        filename: file with the auth data.

    Returns:
        twitter_api: object for making API calls.
    """
    with open(filename, 'r', encoding='utf-8') as infile:
        auth_data = infile.read().splitlines()
    
    consumer_key = auth_data[0]
    consumer_secret = auth_data[1]
    oauth_token = auth_data[2]
    oauth_token_secret = auth_data[3]

    auth = twitter.oauth.OAuth(oauth_token, oauth_token_secret, consumer_key, consumer_secret)
    twitter_api = twitter.Twitter(auth=auth)
    
    return twitter_api

def log_tweet(tweet_counter, req_num, tweet, char_counter):
    """
    Log the posted tweet and book offset in the log file.

    Args:
        tweet_counter: ordinal number of the posted tweet.
        req_num: number of API requests for the current tweet.
        tweet: content of the posted tweet.
        char_counter: character offset in the book string.

    Returns:
        Nothing.
    """
    tweet_msg = 'POSTING TWEET #' + str(tweet_counter).rjust(7, '0') + ' | REQUEST #' + str(req_num).rjust(3, '0') + ' | TWEET: ' + tweet
    book_msg = 'CURRENT OFFSET IN BOOK: ' + str(char_counter)
    logger.info(tweet_msg)
    logger.info(book_msg)

def post_tweet(tweet):
    """
    Post a new tweet, log current progess and sleep a certain amount of seconds.
    If any of that fails, the function tries again a certain amount of times.

    Args:
        tweet: text content for a new tweet.

    Returns:
        new_tweet_counter: global tweet_counter incremented by 1. 
    """
    retries = 15
    cooldown = 120  # seconds
    tweet = sub(r' $', '', tweet)  # remove (if there's any) single space at the end of the tweet
    new_tweet_counter = tweet_counter + 1

    for i in range(1, retries + 1):
        try:
            twitter_api.statuses.update(status=tweet)
            log_tweet(new_tweet_counter, i, tweet, char_counter)
            sleep(cooldown)  # avoid twitter's spam detection
            break
        except:
            if i == retries:
                logger.error('MAX NUMBER OF RETRIES REACHED | EXITING')
                exit()
            sleep(i * cooldown * 10)  # wait some time until the next try

    return new_tweet_counter


if __name__ == '__main__':

    twitter_api = oauth_login('auth_data.txt')

    # get whole book in one string
    with open('books/moby_dick_story.txt', 'r', encoding='utf-8') as infile:
        book = infile.read().replace('\n', ' ')
        book = sub(r'\s+', ' ', book)  # replace whitespace with single space

    char_counter, tweet_counter = 0, 0
    no_more_spaces = False
    word = None

    # open log file
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('logs/books_butcher_moby_dick.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info('STARTED TWEETING BOOK')

    # continue making tweets until last word in book is reached
    while book[char_counter:].find(' ') > -1:

        if word:
            tweet = word  # start tweet with the word that didn't fit in the previous tweet
        else:
            tweet = ''

        while(1):
            space_idx = book[char_counter:].find(' ')
            # check if last word of book is reached
            if space_idx == -1:
                no_more_spaces = True
                break
            new_char_counter = char_counter + space_idx + 1
            word = book[char_counter : new_char_counter]  # get word with trailing single space
            char_counter = new_char_counter
            # check if maximum length of tweet is exceeded
            if len(tweet) + len(word) > 141:
                break
            # check if current word (without the space) fills the tweet to the max limit
            elif len(tweet) + len(word) == 141:
                tweet += word[:-1]  # remove the last space
                word = None
                break
            # continue adding words in current tweet
            else:
                tweet += word
                word = None

        if not no_more_spaces:
            tweet_counter = post_tweet(tweet)

    # last word in book reached
    else:
        word = book[char_counter:]

        # check if last word fits in current tweet
        if len(tweet) + len(word) <= 140:
            tweet += word
            char_counter += len(word)
            tweet_counter = post_tweet(tweet)
        # make 2 tweets if word doesn't fit
        else:
            char_counter += len(word)
            tweet_counter = post_tweet(tweet)
            tweet_counter = post_tweet(word)

    logger.info('FINISHED TWEETING BOOK')
