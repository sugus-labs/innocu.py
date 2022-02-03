from pickle import STOP
from turtle import clear
from api import Elec
from charts import create_daily_charts
from vars import _iber_user, _iber_pass, \
    _email_user, _email_pass, _main_receiver_email, \
    _email_server, _email_port
from comms import send_email_with_image
import pprint as pp
from datetime import datetime

selected_contract_id = ""
selected_cups = ""
selected_address = ""

from_mail = _email_user
from_password = _email_pass
to_mail = _main_receiver_email
smtp_server = _email_server
smtp_port = _email_port

e = Elec()
login = Elec.login(
    e, user = _iber_user, 
    password = _iber_pass)

contracts_list = Elec.list_contracts(e)   
#pp.pprint(contracts_list)

for contract in contracts_list:
    if contract["estadoAlta"] is True \
        and 'BERANGO' in str(contract["direccion"]).upper():
        selected_contract_id = contract["codContrato"]
        selected_cups = contract["cups"]
        selected_address = contract["direccion"] \
            .replace("  ,", ",").split("-")
        selected_address_formatted = "{0}\r\n{1}, {2}" \
            .format(selected_address[0].strip(), 
                selected_address[1].strip(), 
                selected_address[2].strip())
        #selected_address = contract["direccion"]

Elec.select_contract(
    e, selected_contract_id)  

contract_info = Elec.contract_info(e)     

#measure = Elec.measurement(e)      
#print(measure["id"], measure["kilowatt_hour"], 
#    measure["power_consumption"], measure["status"], 
#    measure["icp"])
#print(measure["raw_response"])

start_dt = datetime.strptime("01-02-2022", '%d-%m-%Y')
end_dt = datetime.strptime("01-02-2022", '%d-%m-%Y')

#raw_consumption_data = Elec._consumption_raw(e, start_dt, end_dt)
#pp.pprint(raw_consumption_data)

consumption_data = Elec.consumption(e, start_dt, end_dt)
#pp.pprint(consumption_data)

#raw_generation_data = Elec._production_raw(e, start_dt, end_dt)
#pp.pprint(raw_generation_data)

#generation_data = Elec.consumption(e, start_dt, end_dt)
#pp.pprint(generation_data)

path_plot, dir = create_daily_charts(list(range(1, 25)), consumption_data)

send_email_with_image(path_plot, dir, smtp_server, smtp_port, from_mail, from_password, to_mail, "report")
