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

    def get_subreddit_list(self):
        """
        Return list of subreddits saved in subreddit file
        """
        subreddits = []
        with open('reddit/subreddits.txt', 'r') as f:
            for line in f:
                subreddits.append(line.strip())
        return subreddits

    def extract_top_submissions(self, n):
        """
        Write JSON file for top n submissions for each subreddit in subreddits.txt
        """
        for subreddit in self.get_subreddit_list():
            print('Extracting top {} submissions for r/{}'.format(n, subreddit.capitalize()))
            sub = SubredditObject(subreddit=subreddit)
            sub.write_top_submissions(n)

    def extract_words(self):
        """
        Extract all words from each of the submissions in the top n submissions files
        """
        for subreddit in self.get_subreddit_list():
            print('Extracting words from submissions for r/{}'.format(subreddit.capitalize()))
            sub = SubredditObject(subreddit=subreddit)
            sub.extract_words_from_submissions()


class SubredditObject(object):
    """
    Object to house functionality for each individual Subreddit
    """

    def __init__(self, subreddit=''):
        # reddit API data
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
        # ensure valid filter for parameters
        if filter not in [None, 'all', 'day', 'hour', 'month', 'week', 'year']:
            raise ValueError('filter must be one of: all|day|hour|month|week|year')

    def get_hot_submissions(self, n):
        # get n hot submissions
        return [submission for submission in self.subreddit.hot(limit=n)]

    def get_top_submissions(self, n, filter='all'):
        # get n top submissions
        self.filter_check(filter)
        return [submission for submission in self.subreddit.top(limit=n, time_filter=filter)]

    def get_search_submissions(self, term='', filter='all'):
        # return submissions matching term
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
        # get comments from n hot submissions
        coms = []
        for submission in self.get_hot_submissions(n):
            submission.comments.replace_more(limit=limit, threshold=threshold)
            for comment in submission.comments.list():
                coms.append(comment.body)
        return coms

    def get_top_comments(self, n, filter='all', limit=None, threshold=0):
        # get comments from n top submissions
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

    def read_top_submissions(self):
        """
        Return dictionary of JSON file of n submissions
        """
        try:
            with open('reddit/submissions/{}.json'.format(self.subreddit.display_name.lower())) as f:
                return (json.load(f))
        except FileNotFoundError:
            # error if file not found in submissions folder
            print('Error: submission file not found for {}'.format(self.subreddit.display_name.lower()))

    def write_top_submissions(self, n):
        """
        Write JSON file that contains all n top submissions for subreddit
        """
        if not (type(n) == int and n > 0):
            raise ValueError("n must be integer larger than 0")
        submissions = self.get_top_submissions(n)
        all_subs = {}

        for num in range(n):
            try:
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
                # comment field to be list of tuples containing:
                # (time created / comment body / comment score)
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
                # print error if subreddit has < n submissions in total
                print('Max submissions ({}) reached'.format(num))
                break

        with open('reddit/submissions/{}.json'.format(self.subreddit.display_name.lower()), 'w') as outfile:
            json.dump(all_subs, outfile)

    def extract_words_from_submissions(self):
        """
        Extract all words for processing from previous submission data
        """
        subs = self.read_top_submissions()
        try:
            words = []
            for num in range(len(subs.keys())):
                sub = subs[str(num + 1)]
                # iterate through all words in title
                for word in sub['title'].split():
                    words.append(word.strip().lower())
                # iterate through all comments
                comments = sub['comments']
                for comnum in range(len(comments)):
                    com = comments[comnum]
                    for word in com[1].split():
                        words.append(word.strip().lower())
            data = dict()
            data['words'] = words

            with open('reddit/cleanedwords/{}.json'.format(self.subreddit.display_name.lower()), 'w') as outfile:
                json.dump(data, outfile)
        except:
            print("Error during word extraction")
