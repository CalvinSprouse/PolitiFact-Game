'''
type() is my new best friend
ONLY USED AS A LEARNING PLATFORM NOT NECCESARY FOR GAME BUT KEPT ANYWAYS
'''

from bs4 import BeautifulSoup
import config
import random
import urllib.request

# temporary URL generator just to ensure universal functionality
'''
url = random.choice(["https://www.politifact.com/factchecks/2021/mar/05/mike-pence/pence-falsely-says-if-hr-1-passes-millions-people-/",
                     "https://www.politifact.com/factchecks/2021/mar/05/karen-brinson-bell/nc-elections-board-leader-downplays-rule-changes/",
                     "https://www.politifact.com/factchecks/2021/mar/06/ron-kim/new-york-nursing-homes-not-blanket-immunity-close/"]) '''
url = "https://www.politifact.com/factchecks/2021/mar/05/mike-pence/pence-falsely-says-if-hr-1-passes-millions-people-/"

''' config processes which will need to be implemented in the class below '''
# define a user agent to avoid being blocked (redundant due to config)
# user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0"
# headers = {'User-Agent': user_agent, }

# define the request to combine attributes ^
request = urllib.request.Request(url, None, config.HEADERS)

# fetch html
response = urllib.request.urlopen(request)
html_doc = response.read()

# parse html file
soup = BeautifulSoup(html_doc, "html.parser")


''' retrieving information to format the question TODO: place in a class as an object which given a URL can return the question '''
quote = str(soup.findAll("div", class_="m-statement__quote")[0].text).strip()  # retrieves the quote based on the idea the first m-statement__quote is the heading
quote_context = str(soup.findAll("div", class_="m-statement__desc")[0].text).strip()  # retrieves the subtext regarding when the statement was made
person = str(soup.findAll("a", class_="m-statement__name")[0].text).strip()  # retrieves the statement based on same principle ^

truth = soup.findAll("div", class_="m-statement__meter")[0]  # retrieves the truth-o-meter value based on the alternate title of the first image in the page source
truth = truth.findAll("img")[0]["alt"]  # must be done in sep steps because ...

# retrieve the explanation which can be provided after the player responds
explanation = soup.findAll("div", class_="short-on-time")[0]
explanation_list = [str(data.text).strip() for data in explanation.findAll("li")]  # generates the bullet pointed list as a list

# retrieve the original statement made by the individual (first link in references)
sources_box = soup.findAll("article", class_="m-superbox__content")[0]

# trying to remove non link containing tags - result is a list of dictionarys
sources_list = sources_box.findAll("p")
source_list_dict = [source.find("a") for source in sources_list if source.find("a") is not None]

# definitions for ease of output
original_source = sources_list[0]
original_source_link = original_source.a["href"]
original_source_text = original_source.text

if True:  # container for print statements so I can work on other elements cleanly
    print("Person:\t", person)
    print("Quote:\t", quote)
    print("Statement Made:\t", quote_context)
    print("Truth:\t", truth)

    # print("Original Source(s):\t", original_source)
    print("Original Source Link:\t", original_source_link)
    print("Original Source Text:\t", original_source_text)

    # print("Explanation:\n" + "\n".join("{}".format(k) for k in explanation_list))
    # print("Sources List:\n" + "\n\n".join("{}".format(k) for k in sources_list))


''' from the given url get more urls from below, possibly ignore anything with the keyword facebook '''
url_list = soup.findAll("ul", class_="o-listicle__list")[0]
url_from_list = random.choice((url_list.findAll("article")))  # .prettify() to ... make pretty this is also where the actual link is chosen so randomize this part
url_content = url_from_list.findAll("div", "m-statement__content")
url_link = "https://www.politifact.com" + str(url_content[0].findAll("a")[0]["href"]).strip()
print("New Url:\t", url_link)

''' same version as above but will not generate a dup link '''
new_url = url
while new_url == url:
    url_list = soup.findAll("ul", class_="o-listicle__list")[0]
    url_from_list = random.choice((url_list.findAll("article")))  # .prettify() to ... make pretty this is also where the actual link is chosen so randomize this part
    url_content = url_from_list.findAll("div", "m-statement__content")
    new_url = "https://www.politifact.com" + str(url_content[0].findAll("a")[0]["href"]).strip()
print("New Url Non-Dupe:\t", new_url)


''' retrieve the persons image for later '''
image_link = soup.findAll("div", class_="m-statement__author")[0]
image_link = image_link.findAll("img", class_="c-image__original")[0]["src"]
# print(image_link)
