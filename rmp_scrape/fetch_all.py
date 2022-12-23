__author__ = "Peter Bryant, Jarvis Jia"
__credits__ = ["Peter Bryant", "Jarvis Jia",
               "Bryan Li", "Swathi Annamaneni", "Aidan Shine"]
__version__ = "1.0.0"
__maintainer__ = "Peter Bryant"

import requests
import json
import math
from bs4 import BeautifulSoup
from pprint import pprint
import re
from professor import Professor


class RateMyProfApi:
    """
    RateMyProfAPI class contains functions to scrape professor data from RateMyProfessors.com
    """

    def __init__(self, school_id):
        """
        Constructor for RateMyProfApi class.
        Args: school_id (int): Unique School ID that RateMyProfessor assigns to identify each University.
        """
        self.school_id = school_id  # Parameter for the school ID

    def num_professors(self, testing=False):
        """
        Returns the number of professor results for the given school_id.
        """

        url = 'https://www.ratemyprofessors.com/search/teachers?query=*&sid=' + \
            str(self.school_id)

        data = requests.get(url)         # scrape the overall data from request
        soup = BeautifulSoup(data.text, 'html.parser')         # parse the data

        # find all the script tags
        script_tags = soup.find_all('script')

        professor_script = None  # The script tag that contains the professor data

        # loop through the script tags
        for script in script_tags:
            # If the script tag does not contain any text, skip it
            if script.string is None:
                continue
            # If the script starts with window.__RELAY_STORE__ = then we have found the script with the professor data
            if 'window.__RELAY_STORE__ =' in script.string:
                professor_script = script.string
                break

        # Remove leading whitespace
        professor_script = professor_script.lstrip()

        # Get the JSON data from window.__RELAY_STORE__ = part of the string
        data = re.search(r"window\.__RELAY_STORE__ = (.+);", professor_script)

        # Load the JSON data into a dictionary
        json_data = json.loads(data.group(1))

        key = 'client:root:newSearch:__TeacherSearchPagination_teachers_connection(query:{"fallback":true,"schoolID":"U2Nob29sLTEyNTY=","text":""})'
        num_profs = json_data[key]['resultCount']

        return int(num_profs)


    def scrape_professors(self, testing=False):
        """
        Scrapes all professors from the school with the given school_id. 
        Return: a list of Professor objects, defined in professor.py.
        """
        if testing:
            print("-------ScrapeProfessors--------")
            print("Scraping professors from RateMyProfessors.com...")
            print("University ID: ", self.UniversityId)

        professors = dict()
        
        num_of_prof = self.num_professors() # The number of professors with RMP records associated with this university school_id.

        # RMP returns the total number of professors when a page is requested multiple times, so we need to re-run the function until we get the correct number.

        # If the number of professors is greater than 1 million, re-run the function.
        while(num_of_prof > 1000000): 
            num_of_prof = self.num_professors() # Re-run the function to get the correct number of professors.

        print("Number of Professors Total: ", num_of_prof)



        if testing:
            print("Number of Professors Total: ", num_of_prof)

        # The API returns 20 professors per page.
        num_of_pages = math.ceil(num_of_prof/20)
        for i in range(1, num_of_pages + 1):  # the loop insert all professor into list

            # first RMP seed 1256
            if self.UniversityId == '1256':
                page = requests.get(
                    "http://www.ratemyprofessors.com/filter/professor/?&page="
                    + str(i)
                    + "&queryoption=TEACHER&query=*&sid="
                    + str(self.UniversityId)
                )

            # second RMP seed 18418
            else:
                page = requests.get(
                    "http://www.ratemyprofessors.com/filter/professor/?&page="
                    + str(i)
                    + "&queryoption=TEACHER&queryBy=schoolId&sid="
                    + str(self.UniversityId)
                )

            json_response = json.loads(page.content)

            # iterate through the professor
            for json_professor in json_response["professors"]:

                # load in professor information
                professor = Professor(
                    json_professor["tid"],
                    json_professor["tFname"],
                    json_professor["tLname"],
                    json_professor["tNumRatings"],
                    json_professor["overall_rating"],
                    json_professor["rating_class"],
                    json_professor["tDept"]
                )

                professors[professor.ratemyprof_id] = professor

        if testing:
            print("Professors actually added: ", str(len(professors)))

        return professors


if __name__ == "__main__":
    # # Testing
    uw_school_id_1 = RateMyProfApi(1256)

    uw_school_id_1.scrape_professors(testing=False)

    # uw_school_id_2 = RateMyProfApi(18418)
    # uw_school_id_2.scrape_professors(testing=True)
