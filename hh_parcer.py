import json
import requests
import time


class Vacancy:
    def __init__(self, works_name=None,
                 area=113,  # Russia
                 industry=None,
                 specialization=None,
                 salary_from=None,
                 salary_to=None,
                 only_with_salary=False,
                 ):
        self.works_name = works_name
        self.area = area
        self.industry = industry
        self.specialization = specialization
        self.only_with_salary = only_with_salary
        self.salary_from = salary_from
        self.salary_to = salary_to

    def getPage(self, page=0):
        """
        hh api at first request returning list of vacancies from page,
        after than, you must make a request to get more info about each vacancy yourself,
        :param page:
        :return:
        """
        params = {
            'text': self.works_name,
            'area': find_area_id(self.area),
            'industry': find_industries_id(self.industry),
            'specialization': find_specialization_id(self.specialization),
            'salary.from': self.salary_from,
            'salary.to': self.salary_to,
            'only_with_salary': self.only_with_salary,
            'page': page,
            'per_page': 50  # default 100 (100 vacancy per each page)
        }
        try:
            req = requests.get('https://api.hh.ru/vacancies', params)
            print(req.url)
            list_of_vacancies = req.content.decode()
            req.close()
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)

        return list_of_vacancies

    def get_inform_from_vacancies(self):
        """
        return information about vacansies
        :return:
        """
        skills_list = []  # list of skills
        demanded = []  # demanded skills

        data = {'popular_skills': []}
        # for page in range(0, 1):  # take only first 10 pages
        page = 0
        jsObj = json.loads(self.getPage(page))
        '''if (jsObj['pages'] - page) <= 1:
            break'''

        time.sleep(0.01)
        print(jsObj)
        for num, v in enumerate(jsObj['items']):
            req = requests.get(v['url'])
            job_info = req.content.decode()
            req.close()
            job_info = json.loads(job_info)

            # if num < 10:
            #     data['vacancies'].append(job_info)
            for job_name in job_info['key_skills']:
                skills_list.append(job_name['name'])

            data['specialization'] = take_specialization(job_info).get('spec')

        temp = []  # use for check dublicated elements
        for skill in skills_list:
            if skill not in temp:
                temp.append(skill)
                demanded.append([skill, skills_list.count(skill)])  # append only single

        demanded.sort(key=take_second, reverse=True)
        for skill_name, popularity in demanded[:15]:
            data['popular_skills'].append({
                'name': skill_name.lower(),
                'popularity': popularity
            })
        data = fill_data(data)
        return data


def take_second(elem):
    return elem[1]