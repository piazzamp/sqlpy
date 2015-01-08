# sqlpy
a super simple script to blind-fuzz / sql inject your way into a website pass in a URL that points to a page with a login form
example: `python3.4 ./sqlpy.py ringzer0team.com/challenges/1`

###to-do:
 + inject places other than login forms
 + add session cookie
 + add simple test function to analyze response when passed a single-quote
 + consider injecting into the username field as well
 + add a verbose mode to print out all the stuff that is currently commented out
 + be smarter about determining success or failure

###deps:
 + BeautifulSoup4: `pip install beautifulsoup4`
 + requests: `pip install requests`
