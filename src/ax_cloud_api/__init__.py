import http.client
import json
import time


class Client:
    def __init__(self, refresh_token: str, server_url: str = "api.ax-semantics.com"):
        self.__https_connection = http.client.HTTPSConnection(server_url)
        self.__refresh_token = refresh_token
        self.__renew_interval = 1000
        self.__last_update = None
        self.__token = None

        if not self.__generate_token()[0]:
            raise PermissionError("It appears that the refresh token provided is invalid")

    def __generate_token(self):
        """https://developers.ax-semantics.com/docs/ax-nlg-cloud-api/16ada9886f63d-token-exchange"""
        payload = json.dumps({"refresh_token": self.__refresh_token})
        headers = {"content-type": "application/json"}
        self.__https_connection.request("POST", "/v1/token-exchange/", payload, headers)

        response = self.__https_connection.getresponse()
        if response.getcode() == 200:
            self.__token = json.loads(response.read().decode("utf-8"))["id_token"]
            self.__last_update = time.time()
            return True, self.__token
        else:
            return False, response.read()

    def __get_token(self):
        if not self.__last_update or not self.__token:
            self.__generate_token()
        elif (self.__last_update + self.__renew_interval) < time.time():
            self.__generate_token()
        return self.__token

    def __headers(self):
        return {
            "authorization": f"JWT {self.__get_token()}",
            "content-type": "application/json"
        }

    def __request(self, request_method: str, url: str, payload, headers: dict = None):
        if not headers:
            headers = self.__headers()
        self.__https_connection.request(request_method, url, payload, headers)
        response = self.__https_connection.getresponse()

        return response.getcode(), response.read().decode("utf-8")

    def list_storyexports(self):
        response = self.__request(request_method="GET", url="/v3/story-exports", payload="")
        print(response)
