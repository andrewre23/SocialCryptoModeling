import configparser
from .subreddittool import SubredditTool

config = configparser.ConfigParser()
config.read('./mydata.cfg')

client_id = 'ZPCLNw8081MjQQ'
client_secret = 'hWDqk5ZpXrc5BISDQUl7ZbPysgc'
user_agent = 'socialcryptomodeling:socialcryptomodeling:1.0.0 (by /u/socialcryptomodeling)'


class RedditTool(object):
    """
    Object to house functionality for entire Reddit data retrieval
    """

    def __init__(self):
        pass

    def get_subreddit_list(self):
        """
        Return list of subreddits saved in subreddit file
        """
        subreddits = []
        with open('reddit/subreddits.txt', 'r') as f:
            for line in f:
                subreddits.append(line.strip())
        return subreddits

    def get_top_submissions(self, n):
        """
        Write JSON file for top n submissions for each subreddit in subreddits.txt
        """
        for subreddit in self.get_subreddit_list():
            print('Extracting top {} submissions for r/{}'.format(n, subreddit.capitalize()))
            sub = SubredditTool(subreddit=subreddit)
            sub.write_top_submissions(n)

    def get_submission_words(self):
        """
        Extract all words from each of the submissions in the top n submissions files
        """
        for subreddit in self.get_subreddit_list():
            print('Extracting words from submissions for r/{}'.format(subreddit.capitalize()))
            sub = SubredditTool(subreddit=subreddit)
            sub.write_words_from_submissions()

    def get_top_words(self, n):
        """
        Extract top n words from each of the submissions in the submissions files
        """
        for subreddit in self.get_subreddit_list():
            print('Extracting top {} words from submissions for r/{}'.format(n, subreddit.capitalize()))
            sub = SubredditTool(subreddit=subreddit)
            sub.write_top_words(n)

    def get_submission_stats(self):
        """
        Extract stats from each of the submissions in the top n submissions files
        """
        for subreddit in self.get_subreddit_list():
            print('Extracting stats from submissions for r/{}'.format(subreddit.capitalize()))
            sub = SubredditTool(subreddit=subreddit)
            sub.extract_stats_on_submissions()

    def get_google_trends(self):
        """
        Extract Google trends JSON files for all top words currently extracted
        """
        for subreddit in self.get_subreddit_list():
            print('Extracting Google Trend Data for top words from r/{}'.format(subreddit.capitalize()))
            sub = SubredditTool(subreddit=subreddit)
            sub.write_google_trends()
