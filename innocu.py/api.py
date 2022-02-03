from datetime import date, timedelta
import pprint
from requests import Session
import sys
import vars as ss

pp = pprint.PrettyPrinter(indent = 4)

yesterday_dt = date.today() - timedelta(days = 1)
yesterday_str = yesterday_dt.strftime('%d-%m-%Y00:00:00')

class Elec:
    __iber_domain = "https://www.i-de.es"
    __iber_login_url = __iber_domain + "/consumidores/rest/loginNew/login"
    __iber_contracts_url = __iber_domain + "/consumidores/rest/cto/listaCtos/"    
    __iber_watthourmeter_url = __iber_domain + "/consumidores/rest/escenarioNew/obtenerMedicionOnline/24"
    __iber_icp_status_url = __iber_domain + "/consumidores/rest/rearmeICP/consultarEstado"
    __iber_contract_detail_url = __iber_domain + "/consumidores/rest/detalleCto/detalle/"
    __iber_contract_selection_url = __iber_domain + "/consumidores/rest/cto/seleccion/"
    __iber_obtain_consumption_per_period_url = __iber_domain + "/consumidores/rest/consumoNew/obtenerDatosConsumoPeriodo/fechaInicio/{}00:00:00/fechaFinal/{}00:00:00/" # date format: 07-11-2020 - that's 7 Nov 2020
    __iber_obtain_generation_per_period_url = __iber_domain + "/consumidores/rest/consumoNew/obtenerDatosGeneracionPeriodo/fechaInicio/{}00:00:00/fechaFinal/{}00:00:00/"  # date format: 07-11-2020 - that's 7 Nov 2020
    __iber_headers = {
        'User-Agent': """Mozilla/5.0 (X11; Linux x86_64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Ubuntu Chromium/77.0.3865.90  \
            Chrome/77.0.3865.90 Safari/537.36""",
        'accept': "application/json; charset=utf-8",
        'content-type': "application/json; charset=utf-8",
        'cache-control': "no-cache"
    }

    def __init__(self):
        """Elec class __init__ method."""
        self.__session = None
        #self.__company = "iberdrola"

    def login(self, user, password, 
        company_str = 'iberdrola',):
        """Creates session with your credentials"""
        self.__session = Session()
        if company_str == 'iberdrola':
            login_data = "[\"{}\",\"{}\",null,\"Linux -\", \
                \"PC\",\"Chrome 77.0.3865.90\",\"0\", \
                \"\",\"s\"]".format(user, password)
            #login_data = """[\"{}\",\"{}\",null,\"Linux -\",\"PC\",\"Chrome 77.0.3865.90\",\"0\",\"\",\"s\"]""" \
            #    .format(user, password)
            #print(login_data)
            response = self.__session.request(
                "POST", 
                self.__iber_login_url, data = login_data, 
                headers = self.__iber_headers)
            if response.status_code != 200:
                self.__session = None
                raise Exception("Response error, code: {}".format(response.status_code))
            json_response = response.json()
            if json_response["success"] != "true":
                self.__session = None
                raise Exception("Login error, bad login")
            if json_response["success"] == "true":
                #print("Login OK")
                pass

    def __check_session(self):
        if not self.__session:
            raise Exception("""Session required, 
                use login() method to obtain a session""")            

    def list_contracts(self):
        self.__check_session()
        response = self.__session.request(
            "GET", 
            self.__iber_contracts_url, 
            headers = self.__iber_headers)
        if response.status_code != 200:
            raise Exception
        if not response.text:
            raise Exception
        json_response = response.json()
        if json_response["success"]:
            return json_response["contratos"]    

    def select_contract(self, id):
        self.__check_session()
        response = self.__session.request(
            "GET", 
            self.__iber_contract_selection_url + id, 
            headers = self.__iber_headers)
        if response.status_code != 200:
            raise Exception
        if not response.text:
            raise Exception
        json_response = response.json()
        if not json_response["success"]:
            raise Exception

    def measurement(self):
        """Returns a measurement from the powermeter."""
        self.__check_session()
        response = self.__session.request(
            "GET", 
            self.__iber_watthourmeter_url, 
            headers = self.__iber_headers)
        if response.status_code != 200:
            raise Exception
        if not response.text:
            raise Exception
        json_response = response.json()
        return {
            "id": json_response['codSolicitudTGT'],
            "kilowatt_hour": json_response["valLecturaContador"],
            "power_consumption": json_response['valMagnitud'],
            "icp": json_response['valInterruptor'],
            "status": json_response['valEstado'],
            "raw_response": json_response
        }                    

    def current_kilowatt_hour_read(self):
        """Returns the current read of the electricity meter."""
        return self.measurement()["meter"]

    def current_power_consumption(self):
        """Returns your current power consumption."""
        return self.measurement()['consumption']

    def icpstatus(self):
        """Returns the status of your ICP."""
        self.__check_session()
        response = self.__session.request(
            "POST", 
            self.__iber_icp_status_url, 
            headers=self.__iber_headers)
        if response.status_code != 200:
            raise Exception
        if not response.text:
            raise Exception
        json_response = response.json()
        if str(json_response["icp"]).upper() == "TRUECONECTADO":
            return True
        else:
            return False

    def contract_info(self):
        self.__check_session()
        response = self.__session.request(
            "GET", 
            self.__iber_contract_detail_url, 
            headers = self.__iber_headers)
        if response.status_code != 200:
            raise Exception
        if not response.text:
            raise Exception
        return response.json()

    def _consumption_raw(self, start, end):
        self.__check_session()
        start_str = start.strftime('%d-%m-%Y')
        end_str = end.strftime('%d-%m-%Y')
        response = self.__session.request(
            "GET", 
            self.__iber_obtain_consumption_per_period_url \
                .format(start_str, end_str), 
            headers = self.__iber_headers)
        if response.status_code != 200:
            raise Exception(response.status_code)
        if not response.text:
            raise Exception
        return response.json()

    def consumption(self, start, end):
        json = self._consumption_raw(start, end)
        values = []
        for x in json['y']['data'][0]:
            if x is None:
                values.append(None)
            else:
                values.append(float(x['valor']))
        return values

    def _production_raw(self, start, end):
        self.__check_session()
        start_str = start.strftime('%d-%m-%Y')
        end_str = end.strftime('%d-%m-%Y')
        response = self.__session.request(
            "GET", 
            self.__iber_obtain_generation_per_period_url \
                .format(start_str, end_str),
            headers=self.__iber_headers)
        if response.status_code != 200:
            raise Exception(response.status_code)
        if not response.text:
            raise Exception
        return response.json()

    def production(self, start, end):
        json = self._production_raw(start, end)
        values = []
        for x in json['y']['data'][0]:
            if x is None:
                values.append(None)
            else:
                values.append(float(x['valor']))
        return values