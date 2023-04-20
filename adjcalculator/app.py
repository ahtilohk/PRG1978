from flask import Flask, request, render_template
import requests

adverbs = ["väga", "üsna", "päris", "piisavalt", "niivõrd", "suhteliselt", "üpris", "võimalikult", "suht", "liiga", "äärmiselt", "küllaltki", "täiesti", "erakordselt", "võrdlemisi", "täitsa", "tõeliselt", "küllalt", "ülimalt", "sedavõrd", "liialt", "endiselt", "üllatavalt", "üksnes", "igati", "palju", "vähem", "ääretult", "väga-väga", "kuivõrd", "vähemalt", "peamiselt", "enam-vähem", "tohutult", "uskumatult", "niigi", "hästi", "peaaegu", "hoopis", "hirmus", "mõnusalt", "enamvähem", "suuresti", "erinevalt", "kaugeltki", "natuke", "kindlasti", "niisama", "iseenesest", "jätkuvalt", "valdavalt", "kahtlemata", "eeskätt", "absoluutselt", "kasvõi", "meeletult", "tõepoolest", "kaunis", "täielikult", "eriliselt", "iseäranis", "pisut", "ülemäära", "parajalt", "veidi", "mõnevõrra"]

def query_function(query):

    USERNAME = 'ALohk'
    API_KEY = '339e5710e43e47ba8f51761aeb829a02'
    base_url = 'https://api.sketchengine.eu/bonito/run.cgi'


    CORPUS = 'preloaded/estonian_nc21'
    fcrit = 'longtag 0'
    #showresults = '1'
    #showFreqs = '1'
    data_format = 'json'

    data_freq = {
    'corpname': CORPUS,
    'q': query,
    'format': data_format,
    'fcrit': fcrit
    }

    response_freq = requests.get(base_url + '/freqs', params=data_freq, auth=(USERNAME, API_KEY)).json()
    try:
        count = response_freq['Blocks'][0]['totalfrq']
    except:
        count = 0
    return count

def query_function_view(query):

    USERNAME = 'ALohk'
    API_KEY = '339e5710e43e47ba8f51761aeb829a02'
    base_url = 'https://api.sketchengine.eu/bonito/run.cgi'


    CORPUS = 'preloaded/estonian_nc21'
    fcrit = 'longtag 0'
    #showresults = '1'
    #showFreqs = '1'
    data_format = 'json'

    data_view = {
        'corpname': CORPUS,
        'q': query,
        'format': data_format
    }

    response_view = requests.get(base_url + '/view', params=data_view, auth=(USERNAME, API_KEY)).json()
    count = response_view['fullsize']

    return count


def read_words(filename):
    lines = []
    with open(filename, mode = "r", encoding="utf-8") as f:
        for line in f.readlines():
            lines.append(line.strip())
    return lines


def adverbs_in_query(adverbs):
    q = '('
    for adverb in adverbs:
        q += f'[lemma="{adverb}"]|'
    q = q[:-1] + ')'
    return q

def create_adverbs_query(adverbs_with_OR, token_type, word):
    q = adverbs_with_OR
    q += f'[{token_type}="{word}"]'
    return q

def create_adverbs_query_with_Qmark(adverbs_with_OR, token_type, word):
    q = adverbs_with_OR + '?'
    q += f'[{token_type}="{word}"]'
    return q

def is_in_the_range(value, boundaries):
    return 1 if value >=boundaries[0] and value <=boundaries[1] else 0

def format_number(number):
    # Pöörame sisendstringi ümber, et lihtsustada kolmekaupa töötamist
    number = number[::-1]
    # Jagame stringi kolmekaupa ja lisame tühiku
    chunks = [number[i:i+3][::-1] for i in range(0, len(number), 3)]
    # Pöörame uuesti ümber, et saada õige järjekord
    formatted_number = " ".join(chunks[::-1])
    return formatted_number

#adverbs = read_words("Adverbs.txt")
adverbs_with_OR = adverbs_in_query(adverbs)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def search():
    results = []
    search_term  = ''
    tol_dict = {"attr":(0.246, 1), "attr_st":(0.015, 0.193), "adv":(0.01, 1), "pred":(0.036, 0.344)}
    color_dict = {4: "#52BE80;", 3: "#A9DFBF;", 2: "#FCF3CF;", 1: "#F5B7B1;", 0: "#EC7063;"}
    label_dict = {4: "very likely", 3: "likely", 2: "ambiguous", 1: "unlikely", 0: "very unlikely"}

    if request.method == 'POST':
        search_term = request.form['search']

        token_type = 'word' if search_term[-3:] in ['tud', 'nud'] else 'lemma'
        row1 = ["frequency"]
        row2 = ["range match"]


		# total frequency
        total_freq_query = f'q[{token_type}="{search_term}"]'
        total_freq = query_function(total_freq_query)

        row1.append(format_number(str(total_freq)))
        row2.append(search_term)

		#lemma_S pattern
        lemma_S_query = f'q[{token_type}="{search_term}"] [tag="S.*"]'
        lemma_S_freq = query_function(lemma_S_query)
        lemma_S_norm_freq = round(lemma_S_freq / total_freq if total_freq > 0 else 0, 3)

        row1.append(lemma_S_norm_freq)
        row2.append(is_in_the_range(lemma_S_norm_freq, tol_dict['attr']))



		#start_lemma_S pattern
        s_lemma_S_query = f'q<s>[{token_type}="{search_term}"] [tag="S.*"]'
        s_lemma_S_freq = query_function(s_lemma_S_query)
        s_lemma_S_norm_freq = round(s_lemma_S_freq / total_freq if total_freq > 0 else 0, 3)

        row1.append(s_lemma_S_norm_freq)
        row2.append(is_in_the_range(s_lemma_S_norm_freq, tol_dict['attr_st']))


        #D_list_lemma pattern
        D_list_lemma_query = 'q' + create_adverbs_query(adverbs_with_OR, token_type, search_term)
        D_list_lemma_freq = query_function(D_list_lemma_query)
        D_list_lemma_norm_freq = round(D_list_lemma_freq / total_freq if total_freq > 0 else 0, 3)

        row1.append(D_list_lemma_norm_freq)
        row2.append(is_in_the_range(D_list_lemma_norm_freq, tol_dict['adv']))


		#be_D_list_lemma pattern
        tag2 = "olema"
        be_D_listQmark_lemma_query = f'q[lemma="{tag2}"]' + create_adverbs_query_with_Qmark(adverbs_with_OR, token_type, search_term)
        be_D_listQmark_lemma_freq = query_function(be_D_listQmark_lemma_query)
        be_D_listQmark_lemma_norm_freq = round(be_D_listQmark_lemma_freq / total_freq if total_freq > 0 else 0, 3)

        row1.append(be_D_listQmark_lemma_norm_freq)
        row2.append(is_in_the_range(be_D_listQmark_lemma_norm_freq, tol_dict['pred']))


        total_score = is_in_the_range(lemma_S_norm_freq, tol_dict['attr']) \
              + is_in_the_range(s_lemma_S_norm_freq, tol_dict['attr_st']) \
              + is_in_the_range(D_list_lemma_norm_freq, tol_dict['adv']) \
              + is_in_the_range(be_D_listQmark_lemma_norm_freq, tol_dict['pred'])

        row1.append("")
        row2.append(total_score)


        row1.append("")
        row2.append(color_dict[total_score])


        row1.append("")
        row2.append(label_dict[total_score])


        results.append(row1)
        results.append(row2)

    return render_template('search.html', results=results, search_term=search_term)

#if __name__ == '__main__':
#    app.run()
