# import praw

from datetime import datetime
import json
import configparser
import praw

config = configparser.ConfigParser()
config.read('./mydata.cfg')

client_id = 'ZPCLNw8081MjQQ'
client_secret = 'hWDqk5ZpXrc5BISDQUl7ZbPysgc'
user_agent = 'socialcryptomodeling:socialcryptomodeling:1.0.0 (by /u/socialcryptomodeling)'


class RedditCollector(object):
    """
    Object to house functionality for entire Reddit data retrieval
    """

    def __init__(self):
        pass

    def extract_top_submissions(self, n):
        """
        Write JSON file for top n submissions for each subreddit in subreddits.txt
        """
        with open('reddit/subreddits.txt', 'r') as f:
            for line in f:
                subreddit = line.strip()
                print('Extracting top {} submissions for r/{}'.format(n, subreddit.capitalize()))
                sub = SubredditObject(subreddit=subreddit)
                sub.write_top_submissions(n)


class SubredditObject(object):
    """
    Object to house functionality for each individual Subreddit
    """

    def __init__(self, subreddit=''):
        self.client_id = config['reddit']['client_id']
        self.client_secret = config['reddit']['client_secret']
        self.user_agent = config['reddit']['user_agent']
        self.reddit = praw.Reddit(client_id=self.client_id,
                                  client_secret=self.client_secret,
                                  user_agent=self.user_agent)

        if type(subreddit) != str:
            raise ValueError('subreddit must be string object')
        self.subreddit = self.reddit.subreddit(subreddit.lower())

    def filter_check(self, filter):
        if filter not in [None, 'all', 'day', 'hour', 'month', 'week', 'year']:
            raise ValueError('filter must be one of: all|day|hour|month|week|year')

    def get_hot_submissions(self, n):
        return [submission for submission in self.subreddit.hot(limit=n)]

    def get_top_submissions(self, n, filter='all'):
        self.filter_check(filter)
        return [submission for submission in self.subreddit.top(limit=n, time_filter=filter)]

    def get_search_submissions(self, term='', filter='all'):
        self.filter_check(filter)
        if not isinstance(term, str):
            raise ValueError('Invalid term string')
        return [submission for submission in self.subreddit.search(term.lower())]

    def get_hot_titles(self, n):
        """
        Return list of top n hot titles
        """
        return [submission.title for submission in self.get_hot_submissions(n=n)]

    def get_top_titles(self, n, filter='all'):
        """
        Return list of top n top titles
        """
        self.filter_check(filter)
        return [submission.title for submission in self.get_top_submissions(n=n, filter=filter)]

    def get_hot_comments(self, n, limit=None, threshold=0):
        coms = []
        for submission in self.get_hot_submissions(n):
            submission.comments.replace_more(limit=limit, threshold=threshold)
            for comment in submission.comments.list():
                coms.append(comment.body)
        return coms

    def get_top_comments(self, n, filter='all', limit=None, threshold=0):
        coms = []
        self.filter_check(filter)
        for submission in self.get_top_submissions(n, filter):
            submission.comments.replace_more(limit=limit, threshold=threshold)
            for comment in submission.comments.list():
                coms.append(comment.body)
        return coms

    def convert_from_utc(self, utc_time):
        """
        Convert from UTC to datetime object
        """
        return datetime.utcfromtimestamp(utc_time)

    def write_top_submissions(self, n):
        """
        Write JSON file that contains all n top submissions for subreddit
        """
        if not (type(n) == int and n > 0):
            raise ValueError("n must be integer larger than 0")
        submissions = self.get_top_submissions(n)
        all_subs = {}
        try:
            for num in range(n):
                # iterate through all submissions and extract information to
                # write to JSON object
                sub = submissions[num]
                # create dict to hold all data for submission
                output = {}
                # add submission-level data to output data
                output['created'] = str(self.convert_from_utc(sub.created_utc))
                output['title'] = sub.title
                output['num_comments'] = sub.num_comments
                output['upvote_ratio'] = sub.upvote_ratio
                output['score'] = sub.score
                output['num_crossposts'] = sub.num_crossposts
                # create comment section and add all comments
                sub.comments.replace_more(limit=n)
                comments = [
                    (str(self.convert_from_utc(comment.created)),
                     comment.body,
                     comment.score)
                    for comment in sub.comments.list()
                ]
                output['comments'] = comments
                # add to master list
                all_subs[num + 1] = output
        except IndexError:
            print('Max submissions reached')

        with open('reddit/submissions/{}.json'.format(self.subreddit.display_name.lower()), 'w') as outfile:
            json.dump(all_subs, outfile)
