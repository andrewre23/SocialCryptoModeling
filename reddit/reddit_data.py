import praw

client_id = 'ZPCLNw8081MjQQ'
client_secret = 'hWDqk5ZpXrc5BISDQUl7ZbPysgc'
user_agent = 'socialcryptomodeling:socialcryptomodeling:1.0.0 (by /u/socialcryptomodeling)'

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

def get_top_hot_titles(subreddit,n=1):
    for submission in reddit.subreddit(subreddit).hot(limit=n):
        print(submission.title)

def get_top_hot_comments(subreddit,n=1):
    for submission in reddit.subreddit(subreddit).hot(limit=n):
        print(submission.title)
        print('='*60)
        submission.comments.replace_more(limit=0)
        for top_level_comment in submission.comments:
            print(top_level_comment.body)
        print('='*60)
        print('='*60)

def get_all_comments(subreddit,limit=1):
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            print(comment.body)