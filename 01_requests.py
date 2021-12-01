import requests
import re
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

class CoronaVirusSpider(object):

    def __init__(self):
        self.home_url = 'https://ncov.dxy.cn/ncovh5/view/pneumonia'

    def get_content_from_url(self, url):
        response = requests.get(url)
        return response.content.decode()

    def parse_home_page(self, home_page, id):

        soup = BeautifulSoup(home_page, 'lxml')
        return json.loads(re.findall(r'\[.+\]', soup.find(attrs={'id': id}).text)[0])

    def save(self, data, path):

        with open(path, 'w') as fp:
            json.dump(data, fp, ensure_ascii=False)

    def crawl_last_day_corona_virus(self, domestic):

        home_page = self.get_content_from_url(self.home_url)

        if domestic:
            last_day_corona_virus = self.parse_home_page(home_page, 'getAreaStat')
            self.save(last_day_corona_virus, 'data/last_day_corona_virus_of_china.json')

            corona_virus = []

            for province in tqdm(last_day_corona_virus, '采集1月23日以来的各省疫情信息'):

                statistics_data_url = province['statisticsData']
                statistics_data_json_str = self.get_content_from_url(statistics_data_url)
                statistics_data = json.loads(statistics_data_json_str)['data']

                for one_day in statistics_data:
                    one_day['provinceName'] = province['provinceName']

                corona_virus.extend(statistics_data)

            self.save(corona_virus, 'data/corona_virus_of_china.json')

        else:
            last_day_corona_virus = self.parse_home_page(home_page, 'getListByCountryTypeService2true')
            self.save(last_day_corona_virus, 'data/last_day_corona_virus.json')
            corona_virus = []

            for country in tqdm(last_day_corona_virus, '采集1月23日以来的各国疫情信息'):

                statistics_data_url = country['statisticsData']
                statistics_data_json_str = self.get_content_from_url(statistics_data_url)
                statistics_data = json.loads(statistics_data_json_str)['data']

                for one_day in statistics_data:
                    one_day['provinceName'] = country['provinceName']
                    one_day['countryShortCode'] = country['countryShortCode']

                corona_virus.extend(statistics_data)

            self.save(corona_virus, 'data/corona_virus.json')

    def load(self, domestic):
        self.crawl_last_day_corona_virus(domestic)

if __name__ == '__main__':
    spider = CoronaVirusSpider()
    spider.load(True)
    spider.load(False)
