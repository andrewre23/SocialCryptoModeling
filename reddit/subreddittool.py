# import praw

import re
import json
import praw
import configparser
from datetime import date, datetime, timedelta
from nltk.corpus import stopwords
from pandas import DataFrame
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError

config = configparser.ConfigParser()
config.read('./mydata.cfg')

client_id = 'ZPCLNw8081MjQQ'
client_secret = 'hWDqk5ZpXrc5BISDQUl7ZbPysgc'
user_agent = 'socialcryptomodeling:socialcryptomodeling:1.0.0 (by /u/socialcryptomodeling)'

sw = stopwords.words('english')

STARTDATE = '2013-08-01 '
DATEFORMAT = "%Y-%m-%d %H:%M:%S"


class SubredditTool(object):
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

    def get_top_titles(self, n, filter='all'):
        """
        Return list of top n top titles
        """
        self.filter_check(filter)
        return [submission.title for submission in self.get_top_submissions(n=n, filter=filter)]

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

    def convert_to_datetime(self, inputdt):
        """
        Return datetime object with date for parameter
        """
        return datetime.strptime(inputdt, DATEFORMAT)

    def write_top_submissions(self, n):
        """
        Write JSON file that contains all n top submissions for subreddit
        """
        if not (type(n) == int and n > 0):
            raise ValueError("n must be integer larger than 0")
        submissions = self.get_top_submissions(n)
        all_subs = {}

        for num in range(n):
            if num % 100 == 0 and num > 0:                                  # print every 100th submission
                print('gathering submission #{}'.format(num))
            try:
                # iterate through all submissions and extract information to
                # write to JSON object
                sub = submissions[num]
                # create dict to hold all data for submission
                output = {}
                # add submission-level data to output data
                output['created'] = str(self.convert_from_utc(sub.created_utc))
                output['title'] = sub.title
                try:
                    author = sub.author.name
                except AttributeError:
                    author = ''
                output['author'] = author
                output['id'] = sub.id
                output['num_comments'] = sub.num_comments
                output['upvote_ratio'] = sub.upvote_ratio
                output['score'] = sub.score
                output['num_crossposts'] = sub.num_crossposts
                # create comment section and add all comments
                sub.comments.replace_more(limit=None)
                # comment field to be list of tuples containing:
                # (time created / comment body / comment score)
                all_comments = []
                for comment in sub.comments.list():
                    try:
                        com = (str(self.convert_from_utc(comment.created)),
                             comment.id,                    # comment ID
                             comment.author.name,           # author name
                             comment.body,                  # body of post
                             comment.score,                 # score of post
                             int(comment.is_submitter))     # 0/1 if author is submitter of post
                    except AttributeError:
                        com = ()                   # handle error if no comments
                    if com: all_comments.append(com)
                output['comments'] = all_comments
                # add to master list
                all_subs[num] = output
            except IndexError:
                # print error if subreddit has < n submissions in total
                print('Max submissions ({}) reached'.format(num))
                break

        with open('reddit/submissions/{}.json'.format(self.subreddit.display_name.lower()), 'w') as outfile:
            json.dump(all_subs, outfile)

    def read_top_submissions(self):
        """
        Return dictionary of JSON file of n submissions
        """
        try:
            with open('reddit/submissions/{}.json'.format(self.subreddit.display_name.lower())) as f:
                return json.load(f)
        except FileNotFoundError:
            # error if file not found in submissions folder
            print('Error: submission file not found for {}'.format(self.subreddit.display_name.lower()))

    def read_raw_words_from_submissions(self):
        """
        Return list of raw words from all submissions
        """
        subs = self.read_top_submissions()

        words = []

        for num in range(len(subs.keys())):
            try:
                sub = subs[str(num)]
                # iterate through all words in title
                for word in sub['title'].split():
                    words.append(word.strip().lower())
                # iterate through all comments
                comments = sub['comments']
                for comnum in range(len(comments)):
                    com = comments[comnum]
                    for word in com[3].split():
                        words.append(word.strip().lower())
            except:
                print("Error during word extraction")
        return words

    def append_regex_field(self, pattern=None, fieldname=None):
        """
        Append all strings matching regex pattern to extractions file
        """
        if not (pattern is not None and fieldname is not None and
                type(pattern) == str and type(fieldname) == str):
            raise ValueError('Error with parameters')
        words = self.read_raw_words_from_submissions()
        try:
            with open('reddit/extractions/{}.json'.format(self.subreddit.display_name.lower())) as f:
                data = json.load(f)
        except FileNotFoundError:
            # error if file not found in cleanedwords folder
            print('Warning: file of extracts not found for {}'.format(self.subreddit.display_name.lower()))
            print('Creating file for {}'.format(self.subreddit.display_name.lower()))
            open('reddit/extractions/{}.json'.format(self.subreddit.display_name.lower()), 'w').close()
            data = dict()
        except json.JSONDecodeError:
            print('Warning: blank extract file')
            data = dict()
        output = re.findall(pattern, ' '.join(words))
        data.update({fieldname: output})
        with open('reddit/extractions/{}.json'.format(self.subreddit.display_name.lower()), 'w') as outfile:
            json.dump(data, outfile)

    def write_words_from_submissions(self):
        """
        Extract all words for processing from previous submission data
        """
        output = dict()
        output['words'] = self.read_raw_words_from_submissions()
        with open('reddit/cleanedwords/{}.json'.format(self.subreddit.display_name.lower()), 'w') as outfile:
            json.dump(output, outfile)

    def read_words_from_submissions(self):
        """
        Return dictionary of JSON file of list of words
        """
        try:
            with open('reddit/cleanedwords/{}.json'.format(self.subreddit.display_name.lower())) as f:
                return json.load(f)
        except FileNotFoundError:
            # error if file not found in cleanedwords folder
            print('Error: file of words not found for {}'.format(self.subreddit.display_name.lower()))

    def get_word_counts(self):
        """
        Get word counts from extracted words
        """
        wordlist = self.read_words_from_submissions()['words']
        try:
            wordcounts = {}
            for word in wordlist:
                # iterate through all words in submission
                wordcounts[word] = wordcounts.get(word, 0) + 1
            return wordcounts
        except:
            print("Error during word extraction")

    def get_top_words(self, n):
        """
        Get top n most common words from list of extracted words
        """
        # remove stopwords
        allwords = self.get_word_counts()
        counts = {}
        for word in allwords.keys():
            if word not in sw:
                counts[word] = allwords[word]
        # first, determine word at nth position
        sortedcounts = sorted(counts, key=counts.get, reverse=True)
        # lower index of topcount
        max_index = min(len(sortedcounts), n) - 1
        topcount = counts[sortedcounts[max_index]]
        output = {}
        # select subset of words with >= topcount instances
        for key in counts.keys():
            if counts[key] >= topcount:
                output[key] = counts[key]
        return output

    def write_top_words(self, n):
        """
        Read top n words from subreddit and write them to JSON file in topwords folder
        """
        words = self.get_top_words(n)
        try:
            output = dict()
            output['words'] = words
            with open('reddit/topwords/{}.json'.format(self.subreddit.display_name.lower()), 'w') as outfile:
                json.dump(output, outfile)
        except:
            print("Error during top word extraction")

    def read_top_words(self):
        """
        Return dictionary of JSON file of list of top words
        """
        try:
            with open('reddit/topwords/{}.json'.format(self.subreddit.display_name.lower())) as f:
                return json.load(f)
        except FileNotFoundError:
            # error if file not found in cleanedwords folder
            print('Error: file of words not found for {}'.format(self.subreddit.display_name.lower()))

    def write_google_trends(self):
        """
        Get Google Trends data for top words in topwords folder
        """
        topwords = self.read_top_words()['words']
        trends = TrendReq(hl='en-US', tz=360)
        yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        searchdate = STARTDATE + yesterday
        df = DataFrame()
        for word in sorted(topwords, key=topwords.get, reverse=True):
            kw_list = [word]
            try:
                trends.build_payload(kw_list, cat=0, timeframe=searchdate, geo='', gprop='')
                results = trends.interest_over_time()
                trendresults = results[results.columns[0]]
                df[word] = trendresults
            except ResponseError:
                print('Error retrieving data for "{}"'.format(word))
                continue
            except IndexError:
                print('Error retrieving data for "{}"'.format(word))
                continue
        df.to_json('google/trends/{}.json'.format(self.subreddit.display_name.lower()))

    def extract_stats_on_submissions(self):
        """
        Extract statistics on submissions and write them out to JSON file
        """
        subs = self.read_top_submissions()
        top = self.read_top_words()
        output = dict()
        for num in range(len(subs.keys())):
            # iterate through all submissions
            sub = subs[str(num + 1)]
            temp = dict()
            # number of words in submission
            numwords = 0
            # number of words in submission from list of top n words
            numtops = 0
            temp['title'] = sub['title']
            temp['created'] = sub['created']
            # iterate through all comments
            intertimes = []
            comments = sorted(sub['comments'], key=lambda x: x[0])
            for i, tup in enumerate(comments):
                t, com, score = tup[0], tup[1], tup[2]
                for word in com.split():
                    if word.strip().lower() in top:
                        numtops += 1
                    numwords += 1
                if i == 0:
                    start = self.convert_to_datetime(sub['created'])
                    first = self.convert_to_datetime(t)
                    intertimes.append(str(first - start))
                else:
                    last = self.convert_to_datetime(comments[i - 1][0])
                    curr = self.convert_to_datetime(t)
                    intertimes.append(str(curr - last))
            temp['numwords'] = numwords
            temp['topwords'] = numtops
            temp['intertimes'] = intertimes
            output[num] = temp
        try:
            with open('reddit/submissionanalysis/{}.json'.format(self.subreddit.display_name.lower()), 'w') as outfile:
                json.dump(output, outfile)
        except:
            print("Error during stats extraction")
