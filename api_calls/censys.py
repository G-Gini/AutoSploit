import requests
import traceback
import lib.settings
from lib.errors import AutoSploitAPIConnectionError
from lib.settings import (
    HOST_FILE,
    API_URLS,
    write_to_file
)
import urllib


class CensysAPIHook(object):

    """
    Censys API hook
    """

    def __init__(self, identity=None, token=None, query=None, proxy=None, agent=None, save_mode=None, **kwargs):
        self.id = identity
        self.token = token
        self.query = query
        self.proxy = proxy
        self.user_agent = agent
        self.host_file = HOST_FILE
        self.save_mode = save_mode

    def search(self):
        """
        connect to the Censys API and pull all IP addresses from the provided query
        """
        discovered_censys_hosts = set()
        try:
            lib.settings.start_animation("searching Censys with given query '{}'".format(self.query))
            req = requests.get(
                API_URLS["censys"].format(query=self.query,cursor=""), auth=(self.id, self.token),
                headers=self.user_agent,
                proxies=self.proxy
            )
            json_data = req.json()
            total=1000#json_data["result"]["total"]
            for i in range(100,total,100):
                for item in json_data["result"]["hits"]:
                    discovered_censys_hosts.add(str(item["ip"]))
                next_cursor=json_data["result"]["links"]["next"]
                req = requests.get(
                    API_URLS["censys"].format(query= urllib.quote(self.query),cursor=urllib.quote(next_cursor)), auth=(self.id, self.token),
                    headers=self.user_agent,
                    proxies=self.proxy
                )
                json_data=req.json()
            write_to_file(discovered_censys_hosts, self.host_file, mode=self.save_mode)
            return True
        except Exception as e:
            traceback.print_exc()
            # print(req.text)
            raise AutoSploitAPIConnectionError(str(e))
