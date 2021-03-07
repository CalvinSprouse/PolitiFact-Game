from collections import Counter
import datetime
import pyinputplus as pyip
import time
import question_getter

qg = question_getter.QuestionGetter("https://www.politifact.com/factchecks/2021/mar/05/mike-pence/pence-falsely-says-if-hr-1-passes-millions-people-/", True)
link_list = []
answer_whitelist = ["true", "pants-fire", "barely-true", "false", "mostly-true", "half-true"]


def pick_question():
    global qg
    global link_list
    global answer_whitelist
    
    new_url = qg.get_new_url(blacklist=link_list)
    while question_getter.QuestionGetter(new_url).get_answer() not in answer_whitelist:
        new_url = qg.get_new_url(blacklist=link_list)
    link_list.append(new_url)
    return question_getter.QuestionGetter(new_url)


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
        gq = pick_question()


def collect_data(run_time):
    global qg
    global link_list
    print("collecting data for " + str(run_time) + " minutes")

    # data collection loop to find out how many possible answers there are
    question_num = 0
    responses_list = []
    time_to_run = datetime.datetime.now() + datetime.timedelta(minutes=run_time)

    # DATA
    while time_to_run > datetime.datetime.now():
        # iterate and ensure CPU does not explode
        question_num += 1
        time.sleep(0.25)

        # print so I know it's still alive
        print("\nQuestion Num:", question_num)
        print("Data Status:", str(dict(Counter(responses_list))))
        print(qg.get_person() + " " + qg.get_quote_context() + "\n\t\"" + qg.get_quote() + "\"")
        print("> The correct answer was: " + qg.get_truth())
        responses_list.append(qg.get_truth())

        # ensure even in failure we get DATA
        try:
            qg = pick_question()
        except Exception:
            break

    # output results
    print(dict(Counter(responses_list)))
    with open("data.txt", "w") as writer:
        writer.write("Total Questions: " + str(question_num))
        writer.write(str(dict(Counter(responses_list))))


collect_data(15)
