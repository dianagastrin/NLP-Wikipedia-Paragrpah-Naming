import unicodedata
import bz2
import re
from bs4 import BeautifulSoup
import pickle
from progressbar import ProgressBar
import time

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii.decode('utf-8')
def count_words(page, minWordsInParagraph):
    words = page.split()
    return len(words) >= minWordsInParagraph

pbar = ProgressBar(redirect_stdout=True)

# global variables
templateA = re.compile("{\{([a-z,A-Z,0-9,_]|\s|=|-)+\|[a-z,A-Z,0-9,_]+([a-z,A-Z,0-9]|\s|=)+\}\}")# :example {{kd-ds|dsd}}
templateB = re.compile("\[\[([a-z,A-Z,0-9]|\s|=)+\|[a-z,A-Z,0-9]+([a-z,A-Z,0-9]|\s|=)+\]\]")
templateC = re.compile("\{\{([a-z,A-Z,0-9]|\s|=|-)+\|([a-z,A-Z,0-9]|\s|=|-)+\|([a-z,A-Z,0-9]|\s|=|-)+\}\}")
templateD = re.compile("([a-z,A-Z,0-9]|\s|\(|\))+\|([a-z,A-Z,0-9]|\s|\(|\)|=)+")
templateE = re.compile("\[\[([a-z,A-Z,0-9]|\s|=)+:[a-z,A-Z,0-9]+([a-z,A-Z,0-9]|\s|=|_)+\]\]")
templateG = re.compile("\{\|(_ | a-z |A-Z |0-9 |\w)+\|\}")
templateH = re.compile(r"\{\{(Infobox|infobox)[\:,\s,a-z,A-Z,0-9,_,\|]+\|\}\}") #{Infobox anyStr |}}
templateI = re.compile("\{\|[\s,a-z,A-Z,0-9,\=,\',_,\-,\,,\",\|,\!,\;,\.,\),\(,\W]*\|\}")#: {| any Str |}
templateJ = re.compile("(\(|\[)(\)|\])")# exampe () or []
match_urls = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""",re.DOTALL)
match_file_or_image = re.compile("\[\[(File:|Image:|image:|file:)[a-z,A-Z,0-9,\|,\-,\=,\',\.,\s,_]+(\[\[[a-z,A-Z,0-9,\|,\-,\=,',\.,\s,_]+\]\])*\]\]")# :example [[file: [[dg]] sdg]]
get_titles = re.compile("\=\=[a-z,A-Z,0-9,\-,\(,\),_]+\=\=")#:example ==title==
get_summary_title = re.compile(":\'\'\'[a-z,A-Z,0-9,\s,=,\-,_,\']+\'\'\'")#:example :''''' someStr '''
get_unwanted_ref = re.compile("<ref[\s,a-z,A-Z,0-9,=,\',_,\-,\,,\"]+/>")#:example <ref someStr />

defaultTitle = "Biography"
summaryTitle = "Summary"
curpos_title_paragraphs = []
curpos_wikipedia_biography = []

def get_title(page):
    return remove_accents(page.title.get_text())
def get_text(page):
    text = clean_text(page.text)
    title = get_title(page)
    get_title_content_paragraph(title, text)
    return text
def clean_left_tags(text):
    ref_iter = get_unwanted_ref.finditer(text)
    for match in ref_iter:
        text = text.replace(match.group(),'')
    soup_deeper = BeautifulSoup(text, "lxml")
    [s.extract() for s in soup_deeper('ref')]
    [s.extract() for s in soup_deeper('center')]
    [s.extract() for s in soup_deeper('gallery')]
    return soup_deeper.text
def find_templates(text):
    templ_urls = match_urls.finditer(text)  # example "http://in.bgu.ac.il/Pages/default.aspx"
    for match in templ_urls:
        text = text.replace(match.group(), '')
    temp_file_image = match_file_or_image.finditer(text)
    for match in temp_file_image:
        text = text.replace(match.group(), '')
    templ_iteratorA = templateA.finditer(text)  # example {{str1 | str2}}
    for match in templ_iteratorA:
        text = text.replace(match.group(), match.group()[match.group().find('|') + 1:-2])  # not includes }}

    templ_iteratorB = templateB.finditer(text)  # example [[str1 | str2]]
    for match in templ_iteratorB:
        text = text.replace(match.group(), match.group()[match.group().find('|') + 1:-2])  # not includes ]]
    templ_iteratorC = templateC.finditer(text)  # example {{str1|str2|str3}}
    for match in templ_iteratorC:
        text = text.replace(match.group(), '')

    templ_iteratorD = templateD.finditer(text)  # example str1|str2
    for match in templ_iteratorD:
        text = text.replace(match.group(), match.group()[match.group().find('|') + 1:])
    templ_iteratorE = templateD.finditer(text)  # example [str1:str]
    for match in templ_iteratorE:
        text = text.replace(match.group(), '')
    templ_iteratorG = templateD.finditer(text)  # example [str1:str]
    for match in templ_iteratorG:
        text = text.replace(match.group(), '')
    templ_iteratorI = templateI.finditer(text) #example {|anySTR|}
    for match in templ_iteratorI:
        text = text.replace(match.group(), '')
    templ_match_file_or_image = match_file_or_image.finditer(text)  # example ()
    for match in templ_match_file_or_image:
        text = text.replace(match.group(), '')

    templ_iteratorJ = templateJ.finditer(text) #example () or []
    for match in templ_iteratorJ:
        text = text.replace(match.group(), '')

    return text
def clean_text(text):
    temp_un_wanted_titles = get_summary_title.finditer(text)
    for match in temp_un_wanted_titles:
        text = text.replace(match.group(),'')
    if text.find('\'\'\'') > 0:
        text = text[text.find('\'\'\''):]
        text = text.replace('\'\'\'', '')
    text = clean_left_tags(text)
    if text.find('==References==') > 0:
        text = text[:text.find('==References==')]
    if text.find('== References ==') > 0:
        text = text[:text.find('== References ==')]
    if text.find('==Ancestors==') > 0:
        text = text[:text.find('==Ancestors==')]
    if text.find('==Notes==') > 0:
        text = text[:text.find('==Notes==')]
    if text.find('== Notes ==') > 0:
        text = text[:text.find('== Notes ==')]
    if text.find('==External links==') > 0:
        text = text[:text.find('==External links==')]
    if text.find('==Gallery==') > 0:
        text = text[:text.find('==Gallery==')]
    if text.find('==Further reading==') > 0:
        text = text[:text.find('==Further reading==')]
    if text.find('==See also==') > 0:
        text = text[:text.find('==See also==')]
    if text.find('==References‬‏==') > 0:
        text = text[:text.find('==References‬‏==')]
    if text.find('== Bibliography ‬‏==') > 0:
        text = text[:text.find('== Bibliography ‬‏==')]
    text = find_templates(text)
    return text.replace(']]', '').replace('[[', '').replace('}}', '').replace('{{', '')

def get_title_content_paragraph(titleOfArticle,cleanText):
    title_paragraph = []
    title_text = []
    titles_of_paragraphs = []
    if cleanText.find('==') > 0:
        templ_title_content = get_titles.finditer(cleanText)  # example ==title==
        for match in templ_title_content:
            title_a_index = match.group().find('==')
            title_b_index = match.group().rfind('==')
            title = match.group()[title_a_index + 2: title_b_index]
            titles_of_paragraphs.append(title)
            summary = cleanText[:cleanText.find(match.group())]
            titles_of_paragraphs.append(summaryTitle)
            title_paragraph.append((summaryTitle, summary))
            text_with_one_less_title = cleanText[cleanText.find(match.group()) + len(match.group()) + 1:]
            if text_with_one_less_title.find('==') > 0:
                paragraph = text_with_one_less_title[:text_with_one_less_title.find('==')]
            else: #this biography doesn't have any title to any paragraph
                paragraph = text_with_one_less_title
            if count_words(paragraph, 7):
                title_paragraph.append((title, paragraph))
    else:
        title = defaultTitle
        paragraph = cleanText
        if count_words(paragraph, 7):
            titles_of_paragraphs.append(title)
            title_paragraph.append((title, paragraph))
    title_text.append((titleOfArticle, title_paragraph))
    return title_text, titles_of_paragraphs


    # list_of_titles = FreqDist(listOfTitles)

'''
@:desc extract the biography from the wikiArticle dump and save it as a list in batches of pickles.
@:param filename - wiki dump in xml.bz2 format (for example 'enwiki-latest-pages-articles.xml.bz2')
@:param numberOfBiographies -  is the amount of the biographies to extract.
'''
def dump_biography(filename, numberOfBiographies):
    biographies = []
    bzfile = bz2.BZ2File(filename)
    page = ''
    j = 0
    for line in bzfile:
        str_line = line.decode("utf-8")  # from byte to string
        # turn from byte code to string type
        page += str_line
        if '</page>' in str_line:
            if 'Persondata' in page:
                j += 1
                #remove the unwanted chars (all the accents chars)
                soup = BeautifulSoup(page, "lxml")
                page = soup.text
                page = remove_accents(page)
                biographies.append((get_title(soup),page))
                print(j)
                if j%1000 == 0:
                    with open('biography' + str(j) + '.pickle', 'wb') as handle:
                            pickle.dump(biographies, handle)
                    biographies = []
                    if j == numberOfBiographies:
                        break
            page = ''

def iterator_on_biography():
    for i in range(1000,15000,1000):
        biographies = pickle.load(open("biography"+str(i)+".pickle", "rb"))
        for biography in biographies:
            yield biography



if __name__ == '__main__':
    #When the script is self run
    #dump_biography('enwiki-latest-pages-articles.xml.bz2', 30000)
    TITLE = 0
    TEXT = 1
    bar = 0
    clean_biographies = []
    titles = []
    for i, biography in enumerate(iterator_on_biography()):
        clean_biography = clean_text(biography[TEXT])
        title = biography[TITLE]
        titles_paragraphs,titles_of_pargraphs = get_title_content_paragraph(title,clean_biography)
        clean_biographies.append(titles_paragraphs)
        titles = titles + titles_of_pargraphs
        if i % 1000 == 0 and i != 0 :
            with open('corpus' + str(i) + '.pickle', 'wb') as handle:
                pickle.dump(clean_biographies, handle)
            clean_biographies = []
        if i == 24000:
            break
        time.sleep(0.1)
        if bar != 100:
            bar = (i/24000) * 100
            print(bar)
        pbar.update(bar)
    with open('titles.pickle', 'wb') as handle:
        pickle.dump(titles_of_pargraphs, handle)


