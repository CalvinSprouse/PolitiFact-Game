import pyinputplus as pyip
import question_getter

qg = question_getter.QuestionGetter("https://www.politifact.com/factchecks/2021/mar/05/mike-pence/pence-falsely-says-if-hr-1-passes-millions-people-/", True)
link_list = []
while True:
    print(qg.get_person() + " " + qg.get_quote_context() + "\n\t\"" + qg.get_quote() + "\"\n")
    answer = pyip.inputYesNo("> Is this true?")
    print("> You answered " + answer + " the correct answer was: " + qg.get_truth())

    # this query is just meant to pass time so the computer doesnt explode
    if pyip.inputYesNo("> Continue?") == "no":
        break

    # rest the question getter to a new random
    new_url = qg.get_new_url()
    link_list.append(new_url)
    qg = question_getter.QuestionGetter(new_url)
