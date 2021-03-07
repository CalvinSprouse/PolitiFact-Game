from bs4 import BeautifulSoup
import config
import datetime
import random
# import time  # was used for testing the timeout
import urllib.request


'''
the question getter preforms all the operations in scrapper
- get data from url (question, statement, personality, factuality, etc.)
- get list of new potential urls
- return any element including a list or singular of any new urls
- return an explanation (WIP)
'''


class QuestionGetter:
    def __init__(self, url, randomize=False):
        self.url = url

        # call the website and save the HTML response
        request = urllib.request.Request(self.url, None, config.HEADERS)
        response = urllib.request.urlopen(request)
        html_doc = response.read()

        # soupify it
        soup = BeautifulSoup(html_doc, "html.parser")

        # find and save relevant information
        # retrieves the quote based on the idea the first m-statement__quote is the heading
        self.quote = str(soup.findAll("div", class_="m-statement__quote")[0].text).strip()
        # retrieves the subtext regarding when the statement was made
        self.quote_context = str(soup.findAll("div", class_="m-statement__desc")[0].text).strip()
        # retrieves the statement based on same principle ^
        self.person = str(soup.findAll("a", class_="m-statement__name")[0].text).strip()
        # retrieves the persons picture for potential use in the game
        image_link = soup.findAll("div", class_="m-statement__author")[0]
        image_link = image_link.findAll("img", class_="c-image__original")[0]["src"]
        self.person_image = str(image_link).strip()

        # retrieves the truth/factuality
        # retrieves the truth-o-meter value based on the alternate title of the first image in the page source
        self.truth = soup.findAll("div", class_="m-statement__meter")[0]
        # must be done in sep steps because ...
        self.truth = self.truth.findAll("img")[0]["alt"]

        try:
            # retrieve the explanation which can be provided after response (WIP)
            self.explanation = soup.findAll("div", class_="short-on-time")[0]
            # generates the bullet pointed list as a list
            self.explanation_list = [str(data.text).strip() for data in self.explanation.findAll("li")]
        except IndexError:
            # this means there is no shorthand explanation to provide
            self.explanation = None
            self.explanation_list = None

        # retrieve the original statement made by the individual (first link in references)
        self.sources_box = soup.findAll("article", class_="m-superbox__content")[0]

        # trying to remove non link containing tags - result is a list of dictionarys
        self.sources_list = self.sources_box.findAll("p")
        self.source_list_dict = [source.find("a") for source in self.sources_list if source.find("a") is not None]

        # definitions for ease of output
        try:
            self.original_source = self.sources_list[0]
            self.original_source_link = self.original_source.a["href"]
            self.original_source_text = self.original_source.text
        except TypeError:
            # this means the original source does not have a link (likely an email)
            self.original_source = self.sources_list[0]
            self.original_source_link = None
            self.original_source_text = self.original_source.text

        # get list of other urls - handle randomization later to account for repeats
        self.url_list = soup.findAll("ul", class_="o-listicle__list")[0]

        if randomize:
            self.__init__(self.get_new_url())

    def _signal_alarm(self, sig, tb):
        raise GenerationTimeoutError("timeout")

    def get_quote(self):
        return self.quote

    def get_quote_context(self):
        return self.quote_context

    def get_person(self):
        return self.person

    def get_person_image(self):
        return self.person_image

    def get_truth(self):
        return self.truth

    def get_explanation_bullets(self):
        return self.explanation_list

    def get_original_source_link(self):
        return self.original_source_link

    def get_original_source_text(self):
        return self.original_source_text

    def get_new_url(self, blacklist=[], timeout=5, recursion_depth=0):
        # .prettify() to ... make pretty this is also where the actual link is chosen so randomize this part

        # set the new url to the old url to guarantee access to the generation loop
        new_url = self.url
        if self.url not in blacklist:
            blacklist.append(self.url)

        time_to_run = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        try:
            # constantly generate new urls from the page (randomly) and stop after a time to avoid locking up
            while new_url in blacklist:
                url_from_list = random.choice((self.url_list.findAll("article")))  # .prettify() to ... make pretty this is also where the actual link is chosen so randomize this part
                url_content = url_from_list.findAll("div", "m-statement__content")
                new_url = "https://www.politifact.com" + str(url_content[0].findAll("a")[0]["href"]).strip()
                if time_to_run < datetime.datetime.now():
                    raise GenerationTimeoutError
            return new_url
        except GenerationTimeoutError:
            # now collect a question from the main page using a similar method
            # because the main page also holds everything in an o-listicle__list
            # https://www.politifact.com/factchecks/list/?page=2

            # regen some soup but on a different page of "lates fact checks"
            # starting on page 2 because thats where the new stuff should be
            page_url = "https://www.politifact.com/factchecks/list/?page=" + str(int(recursion_depth) + 2)
            request = urllib.request.Request(page_url, None, config.HEADERS)
            response = urllib.request.urlopen(request)
            html_doc = response.read()
            soup = BeautifulSoup(html_doc, "html.parser")

            # regen that list because its based off the same sorting methods as the bottom of a normal page
            self.url_list = soup.findAll("ul", class_="o-listicle__list")[0]

            # using nasty nasty recursion we can iterate through the pages until we find a new link
            if recursion_depth < 10:
                # print("RECURSION OH NO")  # just in case we want to know when ***it*** happens
                return self.get_new_url(blacklist=blacklist, timeout=timeout, recursion_depth=recursion_depth+1)
            else:
                # ensures the computer wont recusively dig through the whole website and do bad things - find a better way to hard stop
                return "Too Far Buddy"


class GenerationTimeoutError (Exception):
    pass
