import os
import base64
import json
import traceback
import requests

from lib.settings import start_animation
from lib.errors import AutoSploitAPIConnectionError
from lib.settings import (
    API_URLS,
    HOST_FILE,
    write_to_file
)


class ZoomEyeAPIHook(object):

    """
    API hook for the ZoomEye API, in order to connect you need to provide a phone number
    so we're going to use some 'lifted' credentials to login for us
    """

    def __init__(self, token=None,query=None, proxy=None, agent=None, save_mode=None, **kwargs):
        self.query = query
        self.host_file = HOST_FILE
        self.proxy = proxy
        self.user_agent = agent
        self.save_mode = save_mode
        self.token=token

    def __get_auth(self):
        """
        get the authorization for the authentication token, you have to login
        before you can access the API, this is where the 'lifted' creds come into
        play.
        """
        return self.token

    def search(self):
        """
        connect to the API and pull all the IP addresses that are associated with the
        given query
        """
        start_animation("searching ZoomEye with given query '{}'".format(self.query))
        discovered_zoomeye_hosts = set()
        try:
            token = self.__get_auth()
            if self.user_agent is None:
                headers = {"API-KEY": "{}".format(str(token))}
            else:
                headers = {
                    "API-KEY": "{}".format(str(token)),
                    "User-Agent": self.user_agent["User-Agent"]  # oops
                }
            params = {"query": self.query, "page": "1", "facet": "ipv4"}
            req = requests.get(
                API_URLS["zoomeye"],
                params=params, headers=headers, proxies=self.proxy
            )
            _json_data = req.json()
            for item in _json_data["matches"]:
                if len(item["ip"]) > 1:
                    for ip in item["ip"]:
                        discovered_zoomeye_hosts.add(ip)
                else:
                    discovered_zoomeye_hosts.add(str(item["ip"][0]))
            write_to_file(discovered_zoomeye_hosts, self.host_file, mode=self.save_mode)
            return True
        except Exception as e:
            traceback.print_exc()
            print(req.text)
            raise AutoSploitAPIConnectionError(str(e))

