import json
import requests

headers = {
    'cache-control': "no-cache",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}
# VINs = ['SHHFK27608U001230', 'JTMCV02J504233319'] #Тест VIN

url = 'https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/history'
text_01 = 'c {} по {}: {}\n\nПоследняя операция - регистрация новых, произведенных в России или ввезенных, ' \
          'а также ввезенных в Россию бывших в эксплуатации, в том числе временно на срок более 6 месяцев, ' \
          'испытательной техники '
text_02 = 'c {} по {}: {}\n\nПоследняя операция - регистрация ранее зарегистрированных в регистрирующих органах'
text_03 = 'c {} по {}: {} \n\nПоследняя операция - изменение собственника (владельца)'
text_04 = 'c {} по {}: {}\n\nПоследняя операция - изменение данных о собственнике (владельце)'
text_05 = 'c {} по {}: {} \n\nПоследняя операция - изменение данных о транспортном средстве, в том числе изменение ' \
          'технических характеристик и (или) назначения (типа) транспортного средства '
text_06 = 'c {} по {}: {}\n\nПоследняя операция - выдача взамен утраченных или пришедших в негодность' \
          'государственных регистрационных знаков, регистрационных документов, паспортов транспортных средств. '
text_07 = 'c {} по {}: {}\n\nПоследняя операция - прекращение регистрации в том числе'
text_08 = 'c {} по {}: {}\n\n Последняя операция - снятие с учета в связи с убытием за пределы Российской Федерации'
text_11 = 'c {} по {}: {}\n\nПоследняя операция - первичная регистрация'
text_15 = 'c {} по {}: {}\n\nПоследняя операция - регистрация ТС, ввезенных из-за пределов Российской Федерации'
text_16 = 'c {} по {}: {}\n\nПоследняя операция - регистрация ТС, прибывших из других регионов Российской Федерации'



result = []


def get_simple_person_type(requests_type):
    if requests_type == 'Legal':
        return 'Юридическое лицо'
    elif requests_type == 'Natural':
        return 'Физическое лицо'
    else:
        return None


def get_text_from_operation(lastOperation, info_car, simplePersonType):
    dict_text = {
        '01': text_01,
        '02': text_02,
        '03': text_03,
        '04': text_04,
        '05': text_05,
        '06': text_06,
        '07': text_07,
        '08': text_08,
        '11': text_11,
        '15': text_15,
        '16': text_16,
    }
    if lastOperation in dict_text:
        if 'from' in info_car:
            from_time = info_car['from']
        else:
            from_time = None

        if 'to' in info_car:
            to_time = info_car['to']
            if info_car['from'] == info_car['to']:
                to_time = 'настроящее время'
        else:
            to_time = 'настроящее время'
        return dict_text[lastOperation].format(from_time, to_time, simplePersonType)
    return None


def get_data_text(r):
    if 'RequestResult' in json.loads(r.text):
        if len(json.loads(r.text)['RequestResult']['ownershipPeriods']['ownershipPeriod']) > 0:
            info_car = json.loads(r.text)['RequestResult']['ownershipPeriods']['ownershipPeriod'][-1]

            lastOperation = info_car['lastOperation']
            data['lastOperation'] = lastOperation
            simplePersonType = get_simple_person_type(info_car['simplePersonType'])
            if simplePersonType is None:
                return 'Нужно проверить лицо'

            return get_text_from_operation(lastOperation, info_car, simplePersonType)

        else:
            return 'Нету "периоды владения транспортным средством"'
    else:
        return '404 ошибка'


with open('vins.txt') as VINs:
    for index, vin in enumerate(VINs):
        vin = vin.strip()
        data = {
            'vin': vin,
            'checkType': 'history'
        }
        r = requests.post(url, headers=headers, data=data)
        data.pop('checkType', None)
        if r.status_code == 200:
            text = get_data_text(r)
            data['text'] = text
            data.pop('checkType', None)
            print(data)
            result.append(data)
        else:
            print(r.status_code)
    print(result)
    with open('vin.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
