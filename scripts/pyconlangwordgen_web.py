# -*- coding: utf-8 -*-
# PyConlangWordGen v1.1.3

import sys
import random
import re
import time
from browser import document, html

if document['rules'].value.strip() == "":
    fake_qs = '?foo=%s' %time.time()
    document['rules'].value = open('scripts/samplelanguage.txt'+fake_qs).read()

def run():

    sections = ['-CATEGORIES', '-REWRITE', '-SYLLABLES', '-ILLEGAL',
                '-ILLEGALEXCEPTIONS', '-PARAMS', '']
    paramlist = ['minsylls', 'maxsylls', 'showrejected', 'show_pre_rewrite',
                'show_rewrite_trigger', 'filter_duplicates', 'never_generate_file']
    categories = {}
    syllables = []
    illegal = []
    rewritekeys = []  # Normally you'd just store these as a dictionary. However, we want the program to run
    rewritevalues = []  # these rules in the order the user defines them. Iterating through a dictionary doesn't always do that.
    exceptions = []
    # Parameters
    minsyllables = 1
    maxsyllables = 3
    showrejected = False
    show_pre_rewrite = False
    show_rewrite_trigger = False

    filter_duplicates = True
    already_generated = []
    never_generate_file = ""

    # Clear output box
    document['output'].text = ''
    #Ensure that rules box is not empty
    if not document['rules'].value.strip():
        document['output'] <= "You haven't specified any rules!\n"
        document['output'] <= "Specify some rules and try again."
        return False

    rules = [x.strip() for x in document['rules'].value.split('\n')]
    #Recursively returns a list of clusters that fit the rule
    def generate_clusters(rule):
        if len(rule) > 1:
            outp = []
            try:
                for x in categories[rule[0]]:
                    for y in generate_clusters(rule[1:]):
                        outp.append(x + y)
                return outp
            except KeyError:
                for y in generate_clusters(rule[1:]):
                    outp.append(rule[0] + y)
                return outp
        else:
            outp = []
            try:
                for x in categories[rule[0]]:
                    outp.append(x)
                return outp
            except KeyError:
                return [rule[0]]

    # Set up phoneme categories
    try:
        for i in range(rules.index('-CATEGORIES') + 1, len(rules)):
            if rules[i] in sections:
                break
            cat, included = rules[i].split(':')
            cat = cat.strip()
            included = included.strip().replace(' ', '')
            if len(cat) > 1:
                document['output'] <= "Your category names must be only one character long." + html.BR()
                document['output'] <= cat + " is invalid." + html.BR()
                sys.exit()
            if len(included) < 1:
                document['output'] <= "You must include some phonemes in category " + cat + html.BR()
                sys.exit()
            categories[cat] = [char for char in included]
    except ValueError:
        document['output'] <= "You must specify some categories." + html.BR()
        sys.exit()

    # Set up syllable types
    try:
        for i in range(rules.index('-SYLLABLES') + 1, len(rules)):
            if rules[i].strip() in sections:
                break
            syllables.append(rules[i].strip())
    except ValueError:
        document['output'] <= "You must specify some syllable types." + html.BR()
        sys.exit()

    # Set up illegal clusters
    try:
        for i in range(rules.index('-ILLEGAL') + 1, len(rules)):
            if rules[i].strip() in sections:
                break
            if len(rules[i].strip()) < 2:
                document['output'] <= "Error with illegal cluster: " + rules[i] + html.BR()
                document['output'] <= "Illegal clusters must be longer than a single category." + html.BR()
                sys.exit()

            # Recursively returns a regex that fits the rule
            def generate_regex(rule):
                if len(rule) > 2:
                    try:
                        return "[" + ''.join(categories[rule[0]]) + "]" + generate_regex(rule[1:])
                    except KeyError:
                        return "[" + rule[0] + "]" + generate_regex(rule[1:])
                else:
                    try:
                        cat1 = ''.join(categories[rule[0]])
                    except KeyError:
                        cat1 = rule[0]
                    try:
                        cat2 = ''.join(categories[rule[1]])
                    except KeyError:
                        cat2 = rule[1]
                    finally:
                        return "[" + cat1 + "][" + cat2 + "]"

            illegal.append("(?=(" + generate_regex(rules[i].strip()) + "))")
    except ValueError:
        document['output'] <= "Warning: No illegal clusters specified." +  html.BR()
        document['output'] <= "You don't have to specify any, but most languages do." + html.BR() + html.BR()

    # Create a list of exceptionss
    try:
        for i in range(rules.index('-ILLEGALEXCEPTIONS') + 1, len(rules)):
            if rules[i].strip() in sections:
                break
            exceptions += generate_clusters(rules[i].strip())
    except ValueError:
        pass  # User hasn't specified any exceptions, and that's okay.

    # Set up rewrite rules
    try:
        for i in range(rules.index('-REWRITE') + 1, len(rules)):
            if rules[i].strip() in sections:
                break
            inp, outp = rules[i].split('|')
            inp = inp.strip()
            outp = outp.strip()
            if len(inp) < 1:
                document['output'] <= "Invalid rewrite rule: " + rules[i] + html.BR()
                sys.exit()
            for repl in generate_clusters(inp):
                rewritekeys.append(repl)
                rewritevalues.append(outp)
    except ValueError:
        pass  # The user didn't specify any rewrite rules, that's okay.

    # Read parameters
    try:
        for i in range(rules.index('-PARAMS') + 1, len(rules)):
            if rules[i] in sections:
                break
            param = rules[i].split("=")
            if param[0].strip() not in paramlist:
                document['output'] <= param[0] + " is not a valid parameter. Make sure  you have spelled the parameter name correctly." + html.BR()
            elif param[0].strip() == 'minsylls':
                try:
                    minSyllables = int(param[1])
                except ValueError:
                    document['output'] <= rules[i] + " is an invalid parameter declaration. Using default value of minsylls: " + str(minSyllables) + html.BR()
            elif param[0].strip() == 'maxsylls':
                try:
                    maxSyllables = int(param[1])
                except ValueError:
                    document['output'] <= rules[i] + " is an invalid parameter declaration. Using default value of minsylls: " + str(maxSyllables) + html.BR()
            elif param[0].strip() == 'showrejected':
                showrejected = True if param[1].strip() == 'True' else False
            elif param[0].strip() == 'show_pre_rewrite':
                show_pre_rewrite = True if param[1].strip() == 'True' else False
            elif param[0].strip() == 'show_rewrite_trigger':
                show_rewrite_trigger = True if param[1].strip() == 'True' else False
            elif param[0].strip() == 'filter_duplicates':
                filter_duplicates = False if param[1].strip() == 'False' else True
            elif param[0].strip() == 'never_generate_file':
                never_generate_file = param[1].strip()
    except ValueError:
        pass  # No parameters? No problem.

    #Set up never-generate file
    if never_generate_file:
        try:
            f = open(never_generate_file)
            ng = f.read().split('\n')
            already_generated += ng
        except OSError:
            document['output'] <= "Could not find never-generate file at \"" + never_generate_file + "\"" + html.BR()
            document['output'] <= "Please make sure the path is correct before trying again." + html.BR()
            sys.exit()

    def generatesyllable(index, size):
        syll = random.choice(syllables)
        # Ensure that we aren't putting a word-initial or word-final syllable
        # in the middle of the word.
        while ("#" in syll and index != 0) or ("%" in syll and index != size):
            syll = random.choice(syllables)
        syll = syll[1:] if "#" in syll else syll
        syll = syll[:-1] if "%" in syll else syll
        outp = ""
        for char in syll:
            try:
                outp = outp + random.choice(categories[char])
            except KeyError:
                outp = outp + char
        return outp


    def check_illegal(word):
        if word == "#%":
            return True
        if illegal == []:
            return False
        if filter_duplicates and word[1:-1] in already_generated:
            if showrejected:
                document['output'] <= word[1:-1] + " rejected because it's a duplicate." + html.BR()
            return True
        if never_generate_file:
            if word[1:-1] in already_generated:
                if showrejected:
                    document['output'] <= word[1:-1] + " rejected for being a duplicate" + html.BR()
                return True
            # This is so it works whether the word is specified in phoneme symbols
            # or in the conlang's final orthography.
            elif rewrite_word(word).replace('#', '').replace('%', '') in already_generated:
                if showrejected:
                    document['output'] <= word[1:-1] + " rejected for being a duplicate" + html.BR()
                return True
        # So, this is an unreadable monster, isn't it?
        # This bit of code first applies each illegality rule (a regex) to the word.
        # If it matches anything, it gets the index of each bit that matched.
        #
        # Then, it takes a slice containing the illegal string and the two
        # characters on either side (which allows the user to specify exceptional
        # environments.
        #
        # Finally, it checks if any of the illegality exceptions 'pardon' the string.
        # If at any point a string is found that both fits the illegality rules and
        # is not handled by an exception, return that the word is illegal.
        for ill in illegal:
            matches = re.findall(ill, word)
            if matches:
                lastindex = 0
                for m in matches:
                    lastindex = word.find(m, lastindex + 1)
                    handled = False
                    for ex in exceptions:
                        if len(ex) == len(m):  # Not an environment exception
                            if ex == m:
                                handled = True
                                break
                            continue
                        elif len(ex) < len(m):  # Not an exception to this rule
                            continue
                        if lastindex > 0:
                            if len(word) > 1 + len(m) + lastindex:
                                cut = word[lastindex-1:lastindex+len(m)+1]
                            else:
                                cut = word[lastindex-1:len(word)]
                        else:
                            if len(word) > 2 + len(m):
                                cut = word[0:len(m)+2]
                            else:
                                cut = word
                        if ex in cut:
                            handled = True
                            break
                    if not handled:
                        if showrejected:
                                document['output'] <= word[1:-1] + " rejected due to rule " + ill + html.BR()
                        return True
        return False


    def rewrite_word(word):
        if rewritekeys == []:
            return word
        for inp, outp in zip(rewritekeys, rewritevalues):
            if inp in word:
                if show_rewrite_trigger:
                    document['output'] <= "Replacing " + inp + " in " + word + " with " + outp + html.BR()
                word = word.replace(inp, outp)
        return word


    # Actually generate words
    for n in range(0, 20):
        word = ""
        while check_illegal("#" + word + "%"):
            word = ""
            size = random.randint(minsyllables, maxsyllables)
            for s in range(0, size + 1):
                word = word + generatesyllable(s, size - 1)
        if show_pre_rewrite:
            document['output'] <= "Pre-Rewrite: " + word + html.BR()
        # Note: # and % must be added to the word in order to allow the user to
        # specify rewrite rules including the beginning and end of the word.
        # The final two .replace() statements are the only safe way to remove
        # these characters from the output, since the rewrite rule results in
        # # and % being removed from the string. Thus, taking word[1:-1] doesn't
        # work here, even if it's cleaner.
        document['output'] <= rewrite_word("#" + word + "%").replace('#', '').replace('%', '') + html.BR()
        if filter_duplicates: already_generated.append(word)

#This just sets up stuff so the user can input.
document['generate'].bind('click', run)