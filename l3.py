import numpy as np
import matplotlib.pyplot as plt


n = 2   # const
X1 = 4
X2 = 2
mu = 5

MAX_TIME = 100
CURRENT_TIME = 0
logging = False

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
    if logging:
        print(f'Время: {CURRENT_TIME}; Запросы 1: {requests1[:2]}; Запросы 2: {requests2[:2]}; СМО: {smo}; Типы: {smo_type}\n')
        if type == 'request1':
            print(f'В момент времени {t} приходит заявка 1')
        if type == 'request2':
            print(f'В момент времени {t} приходит заявка 2')
        if type == 'smo':
            print(f'СМО покидает заявка в момент времени {t}')


def get_theor_values():
    full_lyambda = X1 + X2
    ro = full_lyambda / mu

    p0 = 1 / (1 + ro / 1 + (ro ** 2) / 2)
    p1 = ro * p0
    p2 = (ro ** 2) * p0 / 2
    p = [p0, p1, p2]

    n3 = ro * (1 - p2)
    Q = 1 - p2
    A = full_lyambda * (1 - p2)

    return p, n3, Q, A


def get_empir_values(empir_p, s1, s2, f1, f2, channels):
    p = [t / MAX_TIME for t in empir_p]

    p_otk1 = f1 / (f1 + s1)
    p_otk2 = f2 / (f2 + s2)
    p_otk = (f1 + f2) / (f1 + f2 + s1 + s2)

    n3 = channels / MAX_TIME
    Q = 1 - p_otk
    A1 = s1 / MAX_TIME
    A2 = s2 / MAX_TIME

    return p, n3, Q, A1, A2, p_otk1, p_otk2, p_otk


def main():
    global CURRENT_TIME, MAX_TIME, requests1, requests2, smo, smo_type
    requests1 = generate_requests(X1)  # Время захода
    requests2 = generate_requests(X2)  # Время захода
    smo = []  # Время ухода
    smo_type = []

    empir_p = [0 for _ in range(n + 1)]
    channels = 0
    success1, success2, failure1, failure2 = 0, 0, 0, 0


    while CURRENT_TIME < MAX_TIME:
        event_name, time = get_next_item()

        log(event_name, time)
        channels += len(smo) * (time - CURRENT_TIME)
        empir_p[len(smo)] += time - CURRENT_TIME

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

    theor_p, theor_n3, theor_Q, theor_A = get_theor_values()
    empir_p, empir_n3, empir_Q, empir_A1, empir_A2, p_otk1, p_otk2, empir_p_otk = get_empir_values(
        empir_p, success1, success2, failure1, failure2, channels)
    print('------------ Статистика ------------')
    print(f'Вероятность отказа для заявок первого типа: {p_otk1}')
    print(f'Вероятность отказа для заявок второго типа: {p_otk2}')
    print(f'Среднее число обслуженных заявок первого типа: {empir_A1}')
    print(f'Среднее число обслуженных заявок второго типа: {empir_A2}')
    print(f'Среднее число каналов, занятых обслуживанием заявок: {empir_n3}')

    print('------------ Сравнение ------------')
    print(f'Относительная пропускная способность: теор: {theor_Q}, эмпир: {empir_Q}')
    print(f'Абсолютная пропускная способность: теор: {theor_A}, эмпир: {empir_A1 + empir_A2}')
    print(f'Среднее число каналов, занятых обслуживанием заявок: теор: {theor_n3}, эмпир: {empir_n3}')
    print(f'{theor_p} - теоретические финальные вероятности')
    print(f'{empir_p} - эмпирические финальные вероятности')
    print(f'Вероятность отказа: теор: {theor_p[-1]}, эмпир: {empir_p_otk} или {empir_p[-1]}')
    show_plots(theor_p, empir_p)


def show_plots(t_p, e_p):
    s = [60 for _ in range(n + 1)]
    x = [i for i in range(n + 1)]
    plt.scatter(x, t_p, s=s, c='red')
    plt.plot(x, t_p, c='red')
    plt.scatter(x, e_p, s=s, c='blue')
    plt.plot(x, e_p, c='blue')
    plt.legend(['theor', 'empir'])
    plt.show()


if __name__ == '__main__':
    main()
