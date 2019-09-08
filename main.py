import json
import requests
from time import strptime
from bs4 import BeautifulSoup

#get the page titles from the input .txt file
def retrieve_pages_from_file(file_name):
    list_pages = list()
    f = open(file_name, "r")
    if f.mode == 'r':
        contents = f.read()
        #split the page titles by line
        contents = contents.splitlines()
        for content in contents:
            list_pages.append(content)

    #return a list with the page titles from the input
    return list_pages

#get metadata from a single revision (user, comment, timestamp, size and id)
def get_metadata_from_revision(revision):
    revision_data = list()

    revision_data.append(revision.attrs['user'])
    revision_data.append(revision.attrs['comment'])
    revision_data.append(revision.attrs['timestamp'])
    revision_data.append(revision.attrs['size'])
    revision_data.append(revision.attrs['revid'])

    #return a list with the revision's metadata
    return revision_data

#get some of the pages edited by a user from 2014 to 2019
def get_some_pages_edited_by_user(user_url):
    page = requests.get(user_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    list_articles = soup.find(class_='mw-contributions-list')

    pages = list()

    #if the user has articles edited, create a loop that colects all the titles of these articles
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

    #return a list containing all the pages edited by the input user from 2014 to 2019    
    return pages

#get all the pages edited by a user from 2014 to 2019, creating a loop of the 'get_some_pages_edited_by_user' function, that returns a limited number os pages
def get_all_pages_edited_by_user(user):
    url = 'https://en.wikipedia.org/w/index.php?limit=500&title=Special%3AContributions&contribs=user&namespace=0&tagfilter=&end=2019-08-01'

    #creates a new url that will call the 'get_some_pages_edited_by_user' function where it has stopped in it's last call
    pages_collected = get_some_pages_edited_by_user(url + '&start=2014-08-01&target=' + user)
    all_pages = pages_collected

    new_date = None

    #creates a loop of the 'get_some_pages_edited_by_user' function, to catch all the pages
    while(len(pages_collected) != 0):
        if(new_date == pages_collected[len(pages_collected) - 1]):
            break;
        new_url = url + '&start=' + pages_collected[len(pages_collected) - 1] + '&target=' + user
        new_date = pages_collected[len(pages_collected) - 1]

        all_pages.remove(all_pages[len(all_pages) - 1])

        pages_collected = get_some_pages_edited_by_user(new_url)

        if(len(pages_collected) != 0):
            all_pages = all_pages + pages_collected
    
    if(all_pages):
        all_pages.remove(all_pages[len(all_pages) - 1])
    all_pages = set(all_pages)

    #return all the pages that the input user has edited from 2014 to 2019 
    return all_pages

#appends all the revisions of a page in the 'Page_revisions.json' file
def save_page_revisions(page_name, revisions_ID, usernames, comments, sizes, timestamps):
    page_dic = {}

    #creates a loop that go through all the revisions and save these revisions inside the 'page_dic' dictionary 
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

    #opens the 'Page_revisions.json' file and saves the data colected inside it
    file_name = "Page_revisions"
    filePathNameWExt = file_name + '.json'
    with open(filePathNameWExt, 'a+') as fp:
        json.dump(final_dic, fp)

#saves the pages that need to be visited in the 'Pages_to_visit.txt' file 
def save_pages_to_visit(pages):
    file_name = "Pages_to_visit.txt"
    f = open(file_name, "w+")
    for page in pages:
      f.write(str(page) + '\n')
    f.close()

#collects and saves all the revisions of a single page
def get_revisions(page_name, visited_pages):
    url = 'https://en.wikipedia.org/w/api.php?action=query&format=xml&prop=revisions&rvprop=user|timestamp|comment|ids|size&rvlimit=500&titles='

    pages_to_visit = list()

    #creates variables to store the data from the revisions
    revisions_ID = list() 
    usernames = list()
    comments = list() 
    sizes = list() 
    timestamps = list()
    
    #print the title os the current page
    print('\n--- ' + page_name + ' ---')

    page_name.replace(' ', '_')
    final_url = url + page_name

    page = requests.get(final_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    #variable that informs if there are more than 500 revisions (the limit per request)
    rvcontinue = soup.find('continue')

    #all the revisions collected
    revisions = soup.find('revisions').find_all('rev')

    new_pages = set()
    index_revision = 0

    #print the total of revisions that need to be checked
    print('\nTotal de revisoes sendo realizadas = ' + str(len(revisions)) + '\n')
    
    #create a loop that saves the data from all the revisions
    for revision in revisions:
        revision_data = get_metadata_from_revision(revision)
        revisions_ID.append(revision_data[4])
        usernames.append(revision_data[0])
        comments.append(revision_data[1])
        sizes.append(revision_data[3])
        timestamps.append(revision_data[2])
        
        revision_data = get_metadata_from_revision(revision)
        new_pages = new_pages | (get_all_pages_edited_by_user(str(revision.attrs['user'])))
        index_revision += 1

        #print the number of revisions checked
        print('Numero de revisoes checadas: ' + str(index_revision) + '/' + str(len(revisions)))

    #creates a loop if there were more than 500 revisions to catch the rest of them
    while(rvcontinue != None):
        final_url = final_url + '&rvcontinue=' + str(rvcontinue).split('="')[2].split('">')[0]

        page = requests.get(final_url)
        soup = BeautifulSoup(page.text, 'html.parser')

        rvcontinue = soup.find('continue')
        revisions = soup.find('revisions')

        #print the total of revisions that need to be checked
        print('\nTotal de revisoes sendo realizadas = ' + str(len(revisions)) + '\n')

        #create a loop that saves the data from all the revisions
        for revision in revisions:
            revision_data = get_metadata_from_revision(revision)
            revisions_ID.append(revision_data[4])
            usernames.append(revision_data[0])
            comments.append(revision_data[1])
            sizes.append(revision_data[3])
            timestamps.append(revision_data[2])

            #merge the pages saved before with the new ones collected
            new_pages = new_pages | (get_all_pages_edited_by_user(str(revision.attrs['user'])))

            index_revision += 1

            #print the number of revisions checked
            print('Numero de revisoes checadas: ' + str(index_revision) + '/' + str(len(revisions)))
    else:
        pass

    #appends new pages to 'pages_to_visit' list
    for page in new_pages:
      if(page in visited_pages):
          pass
      else:
          pages_to_visit.insert(0, page)

    #save the revisions collected inside the 'Page_revisions.json' file
    save_page_revisions(page_name, revisions_ID, usernames, comments, sizes, timestamps)

    return pages_to_visit

def main(list_pages):
    visited_pages = list()
    pages_to_visit = list_pages

    #creates a loop that to collect all the pages revisions
    while(pages_to_visit):
        page_name = pages_to_visit[len(pages_to_visit) - 1]
        pages_to_visit =  pages_to_visit + get_revisions(page_name, visited_pages)
    
        #append the page just collected to the 'visited_pages' list
        visited_pages.append(pages_to_visit[len(pages_to_visit) - 1])

        #remove the page just collected from the 'pages_to_visit' list
        pages_to_visit.remove(page_name)

        #save the pages that still have to be visited inside the 'Pages_to_visit.txt' file
        save_pages_to_visit(pages_to_visit)

        #print the number of pages visited and the number of pages that are still remaining
        print('\nNumero de paginas visitadas: ' + str(len(visited_pages)))
        print('Numero de paginas a serem visitadas: ' + str(len(pages_to_visit)) + '\n')

list_pages = retrieve_pages_from_file('pages.txt')
main(list_pages)
