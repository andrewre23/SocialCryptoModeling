import configparser

from pandas import DataFrame
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

    def get_submission_dataset(self):
        """
        Extract descriptive stats on submission file
        """

        # initialize containers
        sub_list = []
        sub_count = []
        word_count = []
        com_count = []
        early = []
        mid = []
        late = []

        for subreddit in self.get_subreddit_list():
            print('Getting descriptive stats for r/{}'.format(subreddit.capitalize()))

            # create subreddit object and read in data
            sub = SubredditTool(subreddit=subreddit)
            submissions = sub.read_top_submissions()

            # add subreddit name to list
            sub_list.append(subreddit.capitalize())
            sub_count.append(len(submissions))
            word_count.append(len(sub.read_raw_words_from_submissions()))

            # initialize containers
            comments = []
            timestamps = []
            for num in range(len(submissions.keys())):
                sub = submissions[str(num)]
                # iterate through all words in title
                comments.append(len(sub['comments']))
                timestamps.append(sub['created'])
            com_count.append(sum(comments))

            # sort list of timestamps
            timestamps = sorted(timestamps)

            # get earliest timestamps
            try:
                early.append(timestamps[0])
            except IndexError:
                early.append(None)
            # get latest timestamps
            try:
                late.append(timestamps[-1])
            except IndexError:
                late.append(None)
            # get mid-point timestamps
            try:
                i = len(timestamps)
                # get number of timestamps and find midpoint index
                mid_pt = int(i / 2)
                mid.append(timestamps[mid_pt])
            except IndexError:
                mid.append(None)

        df = DataFrame({
            'subreddit': sub_list,
            'num_submissions': sub_count,
            'num_words' : word_count,
            'num_comments': com_count,
            'early_post': early,
            'mid_post': mid,
            'late_post': late
        })
        # writes stats file to CSV
        print('Writing descritpive stats file')
        df.to_csv('reddit/submission_stats.csv', index=False)