from multiprocessing import Process
from queue import Queue
from threading import Thread
import requests
from bs4 import BeautifulSoup
import time


class PrintThread(Thread):

    def __init__(self, q):
        super().__init__()
        self.q = q

    def run(self):
        while True:
            try:
                url = self.q.get()
                html = requests.get(url).text
                soup = BeautifulSoup(html, 'html.parser')
                try:
                    tds = soup.find('table', class_="table table-bordered table-condensed text-smaller2 mt-5").find_all('td')
                    priem = int(tds[1].get_text())
                    podano = int(tds[2].get_text())
                    koef = podano // priem
                    if koef == 0:
                        koef = 1
                    name = soup.find('span', class_='text-muted').get_text()
                    print('На напрвление {} конкурс составляет {} чел. на 1 бюджетное место.'.format(name, koef))
                    self.q.task_done()
                except:
                    pass
            except:
                    pass

class PrintProcess(Process):

    def __init__(self, links):
        super().__init__()
        self.links = links

    def run(self):
        for link in self.links:
            html = requests.get(link).text
            soup = BeautifulSoup(html, 'html.parser')
            try:
                tds = soup.find('table', class_="table table-bordered table-condensed text-smaller2 mt-5").find_all('td')
                priem = int(tds[1].get_text())
                podano = int(tds[2].get_text())
                koef = podano // priem
                if koef==0:
                    koef = 1
                name = soup.find('span', class_='text-muted').get_text()
                print('На напрвление {} конкурс составляет {} чел. на 1 бюджетное место.'.format(name, koef))
            except:
                pass


def main():

    t0 = time.time()
    t1 = time.time()

    url = 'https://apply.tpu.ru/konkurs/index.html?FilterForm%5Bpk_id%5D=15&FilterForm%5Buroven_id%5D=1&FilterForm%5Bforma_id%5D=1#'
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    tds = soup.find('table', class_="table table-bordered table-condensed text-smaller").find_all('a')
    links = []
    for td in tds:
        a = td.get('href')
        link = 'https://apply.tpu.ru' + a
        links.append(link)

    for i in links:
        if len(i) != 53:
            links.remove(i)

    pr1 = PrintProcess(links)
    pr1.start()
    pr1.join()
    print(time.time() - t0)

    pr2 = PrintProcess(links)
    q = Queue()

    for url in links:
        q.put(url)


    for i in range(100):
        th = PrintThread(q)
        th.setDaemon(True)
        th.start()

    q.join()
    pr2.join()
    print(time.time() - t1)


if __name__=='__main__':
    main()