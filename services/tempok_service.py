import requests
import dotenv
import os
from loggs import logging

dotenv.load_dotenv()


class TempokService:

    def __init__(self):
        self.url_base = os.getenv('URL_BASE_TEMPO_OK')
        self.token = os.getenv('TOKEN_TEMPO_OK')
        self.power_source = 'solar'
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _base_body(self):
        return {
            "api_token": self.token,
            "power_source": self.power_source
        }

    def _post(self, endpoint, extra_body=None):
        url = f"{self.url_base}{endpoint}"
        body = self._base_body()
        if extra_body:
            body.update(extra_body)
        try:
            response = requests.post(url, headers=self.headers, json=body)
            if response.status_code == 200:
                return response.json()
            logging.error(f"Status inesperado {response.status_code} em {endpoint}")
        except Exception as e:
            print(f"Erro na requisição {endpoint}: {e}")
            logging.error(f"Erro na requisição {endpoint}: {e}")
        return None

    def variables(self):
        return self._post("/v2/list/variables")

    def obs_variables(self):
        return self._post("/v2/list/obs_variables")

    def plants(self):
        return self._post("/v2/list/plants")

    def multiobserved(self, plant_id, variables):
        return self._post("/v2/observed/multiobserved", {
            "id": plant_id,
            "variables": variables
        })

    def multiobserved_intervalo(self, plant_id, variables, date):
        return self._post("/v2/observed/multiobserved/range", {
            "id": plant_id,
            "variables": variables,
            "start_date": date,
            "end_date": date
        })

    def irradiance(self, date, last_files=12):
        return self._post("/v2/observed/satellite/irradiance", {
            "date": date,
            "last_files": last_files
        })