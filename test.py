from collections import Counter
import config
import datetime
import pyinputplus as pyip
import time
import question_getter

# other vars
LIST_SIZE = 10

# variables the real game will have to manage, maybe class?
qg = question_getter.QuestionGetter("https://www.politifact.com/factchecks/2021/mar/05/mike-pence/pence-falsely-says-if-hr-1-passes-millions-people-/", config.ANSWER_WHITELIST)
question_list = qg.generate_url_list(size=LIST_SIZE, answer_whitelist=config.ANSWER_WHITELIST, order_randomized=True)
answered_list = []  # will be used as a url blacklist to store questions already asked, maybe later a dict to store answers or something for a right/wrong review


# timer to be used as decorator
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print(str(method.__name__) + " (" + str(args) + ", " + str(kw) + ") + " + str(te-ts) + " sec")
        return result
    return timed


# reset the question on the question getter, the game will have to manage the question blacklist
def pick_question():
    global question_list

    # remove element and add it to the black list
    question = question_list.pop(0)
    answered_list.append(question)

    # if the question list is dry generate more questions
    if len(question_list) <= 0:
        question_list = qg.generate_url_list(size=LIST_SIZE, answer_whitelist=config.ANSWER_WHITELIST, link_blacklist=answered_list, order_randomized=True)
    return question_getter.QuestionGetter(url=question, answer_whitelist=config.ANSWER_WHITELIST)


# run a very dumb quiz
def test_class():
    global qg
    global link_list

    while True:
        print(qg.get_person() + " " + qg.get_quote_context() + "\n\t\"" + qg.get_quote() + "\"\n")
        answer = pyip.inputYesNo("> Is this true?")
        print("> You answered " + answer + " the correct answer was: " + qg.get_truth())

        # this query is just meant to pass time so the computer doesnt explode
        if pyip.inputYesNo("> Continue?") == "no":
            break

        # rest the question getter to a new random
        qg = pick_question()


# collects information on potential answers
def collect_data(run_time):
    global qg

    print("collecting data for " + str(run_time) + " minutes")

    # data collection loop to find out how many possible answers there are
    question_num = 0
    responses_list = []
    time_to_run = datetime.datetime.now() + datetime.timedelta(minutes=run_time)

    # DATA
    while time_to_run > datetime.datetime.now():
        # iterate and ensure CPU does not explode
        question_num += 1

        # print so I know it's still alive
        print("\nQuestion Num:", question_num)
        if False:
            print("Data Status:", str(dict(Counter(responses_list))))
            print(qg.get_person() + " " + qg.get_quote_context() + "\n\t\"" + qg.get_quote() + "\"")
            print("> The correct answer was: " + qg.get_truth())
        responses_list.append(qg.get_truth())

        # ensure even in failure we get DATA
        try:
            qg = pick_question()
        except Exception as oops:
            print(oops)
            break

    # output results
    print(dict(Counter(responses_list)))
    with open("data.txt", "w") as writer:
        writer.write("Total Questions: " + str(question_num))
        writer.write(str(dict(Counter(responses_list))))
