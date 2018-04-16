# import praw

client_id = 'ZPCLNw8081MjQQ'
client_secret = 'hWDqk5ZpXrc5BISDQUl7ZbPysgc'
user_agent = 'socialcryptomodeling:socialcryptomodeling:1.0.0 (by /u/socialcryptomodeling)'


def get_top_hot_titles(subreddit, n=1):
    for submission in reddit.subreddit(subreddit).hot(limit=n):
        print(submission.title)


def get_top_hot_comments(subreddit, n=1):
    for submission in reddit.subreddit(subreddit).hot(limit=n):
        print(submission.title)
        print('=' * 60)
        submission.comments.replace_more(limit=0)
        for top_level_comment in submission.comments:
            print(top_level_comment.body)
        print('=' * 60)
        print('=' * 60)


def get_all_comments(subreddit, limit=1):
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            print(comment.body)


class SubredditObject(object):

    def __init__(self, subreddit=''):
        import praw
        self.reddit = praw.Reddit(client_id=client_id,
                                  client_secret=client_secret,
                                  user_agent=user_agent)
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
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
