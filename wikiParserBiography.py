import unicodedata
import bz2
import re
from bs4 import BeautifulSoup
import pickle
import string


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii.decode('utf-8')

# global variables
templateA = re.compile("\{\{([a-z,A-Z,0-9]|\s|=|-)+\|[a-z,A-Z,0-9,_]+([a-z,A-Z,0-9]|\s|=)+\}\}")
templateB = re.compile("\[\[([a-z,A-Z,0-9]|\s|=)+\|[a-z,A-Z,0-9]+([a-z,A-Z,0-9]|\s|=)+\]\]")
templateC = re.compile("\{\{([a-z,A-Z,0-9]|\s|=|-)+\|([a-z,A-Z,0-9]|\s|=|-)+\|([a-z,A-Z,0-9]|\s|=|-)+\}\}")
templateD = re.compile("([a-z,A-Z,0-9]|\s|\(|\))+\|([a-z,A-Z,0-9]|\s|\(|\)|=)+")
templateE = re.compile("\[\[([a-z,A-Z,0-9]|\s|=)+:[a-z,A-Z,0-9]+([a-z,A-Z,0-9]|\s|=|_)+\]\]")
templateF = re.compile("\*.+")
templateG = re.compile("\{\|(_ | a-z |A-Z |0-9 |\w)+\|\}")
templateH = re.compile(r"\{\{infobox[\s,a-z,A-Z,0-9,_,\|]+\|\}\}")
# templateI = re.compile("\{\{.*\}\}") #example {{anyStr}}
templateJ = re.compile("(\(|\[)(\)|\])")  # exampe () or []
match_urls = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""",re.DOTALL)
match_file_or_image = re.compile("File:|Image:")
get_titles = re.compile("\=\=([\s,a-z,A-Z,0-9]|\s|=|-)+\=\=")  # find titles ==title==

defaultTitle = "Biography"
curpos_title_paragraphs = []
curpos_wikipedia_biography = []


def get_title(page):
    return remove_accents(page.title.get_text())


def get_text(page):
    text = clean_text(page.text)
    title = get_title(page)
    get_title_content_paragraph(title, text)
    return text


def get_title_content_paragraph(titleOfArticle, cleanText):
    title_paragraph = []
    title_text = []
    titles_of_paragraphs = []
    if cleanText.find('==') > 0:
        templ_title_content = get_titles.finditer(cleanText)  # example {{str1 | str2}}
        for match in templ_title_content:
            title_a_index = match.group().find('==')
            title_b_index = match.group().rfind('==')
            title = match.group()[title_a_index + 2: title_b_index]
            titles_of_paragraphs.append(title)
            text_with_less_titles = cleanText[cleanText.find(title) + len(title) + 2:]
            if text_with_less_titles.find('==') > 0:
                paragraph = text_with_less_titles[:text_with_less_titles.find('==')]
            else:
                paragraph = text_with_less_titles
            title_paragraph.append((title, paragraph))
    else:
        title = defaultTitle
        paragraph = cleanText
        titles_of_paragraphs.append(title)
        title_paragraph.append((title, paragraph))
    title_text.append((titleOfArticle, title_paragraph))
    curpos_wikipedia_biography.append(title_text)
    curpos_title_paragraphs.append(titles_of_paragraphs)


def clean_left_tags(text):
    soup_deeper = BeautifulSoup(text, "lxml")
    [s.extract() for s in soup_deeper('ref')]
    [s.extract() for s in soup_deeper('center')]
    return soup_deeper.text


def find_templates(text):
    templ_urls = match_urls.finditer(text)  # example "http://in.bgu.ac.il/Pages/default.aspx"
    for match in templ_urls:
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
    templ_iteratorC = templateC.finditer(text)  # example {{str1|str2|str3}}
    for match in templ_iteratorC:
        text = text.replace(match.group(), '')

    templ_iteratorD = templateD.finditer(text)  # example str1|str2
    for match in templ_iteratorD:
        text = text.replace(match.group(), match.group()[match.group().find('|') + 1:])
    templ_iteratorE = templateD.finditer(text)  # example [str1:str]
    for match in templ_iteratorE:
        text = text.replace(match.group(), '')
    #
    # templ_iteratorF = templateD.finditer(text) #example [str1:str]
    # for match in templ_iteratorF:
    #     text = text.replace(match.group(), '')

    templ_iteratorG = templateD.finditer(text)  # example [str1:str]
    for match in templ_iteratorG:
        text = text.replace(match.group(), '')
    # templ_iteratorI = templateI.finditer(text) #example {{anyStr}}
    # for match in templ_iteratorI:
    #     text = text.replace(match.group(), '')

    templ_match_file_or_image = match_file_or_image.finditer(text)  # example ()
    for match in templ_match_file_or_image:
        text = text.replace(match.group(), '')

    return text


def clean_text(text):
    if text.find('\'\'\'') > 0:
        text = text[text.find('\''''):]
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
    if text.find('==External links==') > 0:
        text = text[:text.find('==Notes==')]
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
    text = text.replace("lang-grc|", '')
    return text.replace(']]', '').replace('[[', '').replace('}}', '').replace('{{', '')


def most_frequent_titles(listOfTitles):
    pass
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
                print(get_title(soup))
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
    # When the script is self run
    #dump_biography('enwiki-latest-pages-articles.xml.bz2', 15000)
    TITLE = 0
    TEXT = 1
    for i, biography in enumerate(iterator_on_biography()):
       clean = clean_text(biography[TEXT])
