# import praw


import configparser
config = configparser.ConfigParser()
config.read('./mydata.cfg')

client_id = 'ZPCLNw8081MjQQ'
client_secret = 'hWDqk5ZpXrc5BISDQUl7ZbPysgc'
user_agent = 'socialcryptomodeling:socialcryptomodeling:1.0.0 (by /u/socialcryptomodeling)'


class SubredditObject(object):

    def __init__(self, subreddit=''):
        import praw
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

