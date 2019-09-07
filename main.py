import json
import requests
from time import strptime
from bs4 import BeautifulSoup

def get_pages(file_name):
    list_pages = list()
    f=open(file_name, "r")
    if f.mode == 'r':
        contents = f.read()
        contents = contents.splitlines()
        for content in contents:
            list_pages.append(content)
    return list_pages

def get_metadata(revision):
    revision_data = list()

    revision_data.append(revision.attrs['user'])
    revision_data.append(revision.attrs['comment'])
    revision_data.append(revision.attrs['timestamp'])
    revision_data.append(revision.attrs['size'])
    revision_data.append(revision.attrs['revid'])

    return revision_data

def get_url_pages(user_url):
    page = requests.get(user_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    list_articles = soup.find(class_='mw-contributions-list')

    pages = list()

    if(list_articles):
        list_articles = list_articles.find_all('li')
        for article in list_articles:
            article = article.find(class_='mw-contributions-title').text
            if(article in pages):
              pass
            else:
              pages.append(article)


        year = list_articles[len(list_articles) - 1].find(class_='mw-changeslist-date').text.split(' ')[3]

        month = list_articles[len(list_articles) - 1].find(class_='mw-changeslist-date').text.split(' ')[2]
        new = month[0].upper() + month[1:3].lower()
        month = strptime(new,'%b').tm_mon

        day = list_articles[len(list_articles) - 1].find(class_='mw-changeslist-date').text.split(' ')[1]

        complete_date = str(year) + "-" + str(month) + "-" + str(day) 

        pages.append(complete_date)
    return pages

def get_user_pages(user):
    url = 'https://en.wikipedia.org/w/index.php?limit=500&title=Special%3AContributions&contribs=user&namespace=0&tagfilter=&end=2019-08-01'
    pages_collected = get_url_pages(url + '&start=2014-08-01&target=' + user)
    all_pages = pages_collected

    new_date = None

    while(len(pages_collected) != 0):
        if(new_date == pages_collected[len(pages_collected) - 1]):
            break;
        new_url = url + '&start=' + pages_collected[len(pages_collected) - 1] + '&target=' + user
        new_date = pages_collected[len(pages_collected) - 1]

        all_pages.remove(all_pages[len(all_pages) - 1])

        pages_collected = get_url_pages(new_url)

        if(len(pages_collected) != 0):
            all_pages = all_pages + pages_collected
    
    if(all_pages):
        all_pages.remove(all_pages[len(all_pages) - 1])
    all_pages = set(all_pages)

    return all_pages

def save_page_revisions(page_name, revisions_ID, usernames, comments, sizes, timestamps):
    page_dic = {}
    for i in range(len(revisions_ID)):
        revision_name = "Revision " + revisions_ID[i]
        revisionItems_dic = {}
        revisionItems_dic["Contributor's username"] = usernames[i]
        revisionItems_dic["Contributor's comment"] = comments[i]
        revisionItems_dic["ID"] = revisions_ID[i]
        revisionItems_dic["Timestamp"] = timestamps[i]
        revisionItems_dic["Revision's size (bytes)"] = sizes[i]
        page_dic[revision_name] = revisionItems_dic
    final_dic = {}
    final_dic[str(page_name)] = page_dic
    file_name = "Page_revisions"
    filePathNameWExt = file_name + '.json'
    with open(filePathNameWExt, 'a+') as fp:
        json.dump(final_dic, fp)

def save_pages_to_visit(pages):
    file_name = "Pages_to_visit.txt"
    f = open(file_name, "w+")
    for page in pages:
      f.write(str(page) + '\n')
    f.close()

def get_revisions(list_pages):
    url = 'https://en.wikipedia.org/w/api.php?action=query&format=xml&prop=revisions&rvprop=user|timestamp|comment|ids|size&rvlimit=500&titles='

    visited_pages = list()
    pages_to_visit = list_pages

    while(pages_to_visit):
        page_name = pages_to_visit[len(pages_to_visit) - 1]

        revisions_ID = list() 
        usernames = list()
        comments = list() 
        sizes = list() 
        timestamps = list()

        print('\n--- ' + page_name + ' ---')

        page_name.replace(' ', '_')
        final_url = url + page_name

        page = requests.get(final_url)
        soup = BeautifulSoup(page.text, 'html.parser')

        rvcontinue = soup.find('continue')
        revisions = soup.find('revisions').find_all('rev')

        new_pages = set()

        index_revision = 0
        print('\nTotal de revisoes sendo realizadas = ' + str(len(revisions)) + '\n')

        for revision in revisions:
            revision_data = get_metadata(revision)
            revisions_ID.append(revision_data[4])
            usernames.append(revision_data[0])
            comments.append(revision_data[1])
            sizes.append(revision_data[3])
            timestamps.append(revision_data[2])
            
            revision_data = get_metadata(revision)
            new_pages = new_pages | (get_user_pages(str(revision.attrs['user'])))
            index_revision += 1
            print('Numero de revisoes checadas: ' + str(index_revision) + '/' + str(len(revisions)))

        while(rvcontinue != None):
            final_url = final_url + '&rvcontinue=' + str(rvcontinue).split('="')[2].split('">')[0]

            page = requests.get(final_url)
            soup = BeautifulSoup(page.text, 'html.parser')

            rvcontinue = soup.find('continue')
            revisions = soup.find('revisions')

            print('\nTotal de scans sendo realizados = ' + str(len(revisions)) + '\n')

            for revision in revisions:
                revision_data = get_metadata(revision)
                revisions_ID.append(revision_data[4])
                usernames.append(revision_data[0])
                comments.append(revision_data[1])
                sizes.append(revision_data[3])
                timestamps.append(revision_data[2])

                new_pages = new_pages | (get_user_pages(str(revision.attrs['user'])))
                index_revision += 1
                print('Numero de revisoes feitas: ' + str(index_revision) + '/' + str(len(revisions)))
        else:
            pass
        
        visited_pages.append(pages_to_visit[len(pages_to_visit) - 1])

        for page in new_pages:
          if(page in visited_pages):
              pass
          else:
              pages_to_visit.insert(0, page)

        pages_to_visit.remove(pages_to_visit[len(pages_to_visit) - 1])

        save_page_revisions(page_name, revisions_ID, usernames, comments, sizes, timestamps)
        save_pages_to_visit(pages_to_visit)
        print('\nNumero de paginas visitadas: ' + str(len(visited_pages)))
        print('Numero de paginas a serem visitadas: ' + str(len(pages_to_visit)) + '\n')

list_pages = get_pages('pages.txt')
get_revisions(list_pages)
