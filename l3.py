import numpy as np


n = 2
X1 = 5
X2 = 4
mu = 1

MAX_TIME = 10
CURRENT_TIME = 0
log = False

requests1, requests2, smo, smo_type = None, None, None, None


def generate_requests(lyambda):
    r = []
    t = 0
    while t < MAX_TIME:
        t += np.random.exponential(1 / lyambda)
        r.append(t)
    return r


def get_next_item():
    global requests1, requests2, smo

    min_request1 = min(requests1)
    min_request2 = min(requests2)
    min_smo = None if len(smo) == 0 else min(smo)

    min_of_min = min([q for q in [min_request1, min_request2, min_smo] if q is not None])
    if min_of_min == min_request1:
        return 'request1', min_of_min
    if min_of_min == min_request2:
        return 'request2', min_of_min
    if min_of_min == min_smo:
        return 'smo', min_of_min
    raise ValueError('смэрть')


def log(type, t):
    if log:
        print(f'Время: {CURRENT_TIME}; Запросы 1: {requests1[:2]}; Запросы 2: {requests2[:2]}; СМО: {smo}; Типы: {smo_type}\n')
        if type == 'request1':
            print(f'В момент времени {t} приходит заявка 1')
        if type == 'request2':
            print(f'В момент времени {t} приходит заявка 2')
        if type == 'smo':
            print(f'СМО покидает заявка в момент времени {t}')

def main():
    global CURRENT_TIME, MAX_TIME, requests1, requests2, smo, smo_type
    requests1 = generate_requests(X1)  # Время захода
    requests2 = generate_requests(X2)  # Время захода
    smo = []  # Время ухода
    smo_type = []

    channels = []
    success1, success2, failure1, failure2 = 0, 0, 0, 0


    while CURRENT_TIME < MAX_TIME:
        event_name, time = get_next_item()

        log(event_name, time)
        channels.append(len(smo))

        if event_name == 'request2':
            requests2.remove(time)

            if len(smo) == n:   # Для заявки 2 не нашлось места
                failure2 += 1
            else:   # Если есть пустое место, добавляем заявку
                smo.append(time + np.random.exponential(1 / mu))
                smo_type.insert(len(smo) - 1, '2')

        if event_name == 'request1':
            requests1.remove(time)
            if len(smo) < n:    # Если есть пустое место, добавляем заявку
                smo.append(time + np.random.exponential(1 / mu))
                smo_type.insert(len(smo) - 1, '1')
            elif '2' in smo_type:   # В смо есть заявка второго типа
                index = smo_type.index('2')
                smo[index] = time + np.random.exponential(1 / mu)
                smo_type[index] = '1'

                failure2 += 1
            else:   # Нет места
                failure1 += 1

        if event_name == 'smo':     # Обработка заявки закончилась
            index = smo.index(time)

            if smo_type[index] == '1':
                success1 += 1
            else:
                success2 += 1

            del smo[index]
            del smo_type[index]

        CURRENT_TIME = time

    print('\n----- Статистика -----')
    print('Вероятность отказа у заявок первого типа:', failure1 / (failure1 + success1))
    print('Вероятность отказа у заявок второго типа:', failure2 / (failure2 + success2))
    print('Среднее число обслуженных заявок первого типа в единицу времени:', success1 / MAX_TIME)
    print('Среднее число обслуженных заявок второго типа в единицу времени:', success2 / MAX_TIME)
    print('Среднее число каналов, занятых обслуживанием:', sum(channels) / len(channels))


if __name__ == '__main__':
    main()
