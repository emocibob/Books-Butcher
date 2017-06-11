A bot that posts whole books on Twitter tweet-by-tweet.

Currently, the bot tweets every 2 minutes. [See it in action!](https://twitter.com/BooksButcher)

## Some notes

- All newlines and whitespace in the books are converted to a single space
- In the script a *word* is a substring surrounded by spaces
- The file `auth_data.txt` is of course not included in this repo since it has my private Twitter auth info
- Details on Twitter's API limits can be found [here](https://support.twitter.com/articles/15364#)

## TODO

- Add an option for more books (currently "Moby Dick" is hardcoded)