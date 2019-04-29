from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import time
import json


def get_version_list(url):
    next_page = url
    version_list = []

    while True:
        # Open repository's tag page.
        try:
            html = urlopen(next_page)
            bs_html = BeautifulSoup(html, features="lxml")
        except HTTPError:
            print('open ' + next_page + ' failed.')
            print('retry...')
            time.sleep(1)
            continue

        # put all version tag into list
        for version_tag in bs_html.findAll('h4', {'class': 'flex-auto min-width-0 pr-2 pb-1 commit-title'}):
            version = version_tag.find('a').get_text().strip()
            version_list.append(version)
            #print(version)

        if len(version_list) == 0:
            print('can not find version tag in url ' + next_page)
            break

        # find next page.
        disable = bs_html.find('span', {'class': 'disabled'})
        if disable is not None and disable.get_text() == 'Next':
            break
        else:
            next_page = url + '?after=' + version_list[-1]
            print(next_page)

        # avoid HTTPError 429: too many request
        time.sleep(0.5)

    return version_list


def output_json(release_list):
    if release_list is None or len(release_list) == 0:
        print('Empty release list, can not output json file')
        return

    with open('release_list.json', 'w') as file:
        json.dump(release_list, file)


if __name__ == '__main__':
    urlsList = dict(apache='https://github.com/apache/kafka/tags',
                    tensorflow='https://github.com/tensorflow/tensorflow/tags',
                    django='https://github.com/django/django/tags')

    apache_list = get_version_list(urlsList['apache'])
    trnsorflow_list = get_version_list(urlsList['tensorflow'])
    django_list = get_version_list(urlsList['django'])
    release_list = dict(apache=apache_list,
                        trnsorflow=trnsorflow_list,
                        django=django_list)
    output_json(release_list)
