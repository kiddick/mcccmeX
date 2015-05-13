import threading
import requests
import Queue
import os
import time
import sys

from itertools import cycle


class UrlReaderX(threading.Thread):
    def __init__(self, queue, output):
        super(UrlReaderX, self).__init__()
        self.setDaemon = True
        self.queue = queue
        self.output = output

    def run(self):
        while True:
            try:
                target = self.queue.get(block = False)
                headers = {'User-Agent': 'Mozilla/5.0'}
                data = requests.get(target, headers = headers)
                # print data.status_code
                current_page = data.url.split('&')[0].split('=')[1]
                if data.status_code == 200:
                    self.queue.task_done()
                    self.output.put((data.text, current_page), block = False)
                elif data.status_code == 404:
                    self.queue.task_done()
                else:
                    self.queue.task_done()
                    self.queue.put(target)
            except Queue.Empty:
                break

errcount = 0

def load(urlrange, num_threads):
    mainqueue = Queue.Queue()
    outq = Queue.Queue()
    mythreads = []

    for url in urlrange:
        mainqueue.put(url)

    for j in xrange(num_threads):
        mythreads.append(UrlReaderX(mainqueue, outq))
        mythreads[-1].start()

    lst = ['|', '/', '-', '\\']
    pool = cycle(lst)
    brd = len(urlrange)
    while True:
        if len(mainqueue.__dict__['queue']) == 0:
            break
        time.sleep(0.1)
        sys.stdout.write("\r%c %f%%" % (next(pool), ((float(brd - len(mainqueue.__dict__['queue']))/brd)*100)))
        sys.stdout.flush()

    mainqueue.join()
    return list(outq.__dict__['queue'])


def main():
    mccme = 'http://informatics.mccme.ru/mod/statements/view3.php?chapterid='

    urlrange = []
    iterrange = range(1, 5001) + range(111000, 113000)
    # print iterrange
    for pid in (x for x in iterrange):
        urlrange.append(mccme + str(pid))
    print len(urlrange)

    mainqueue = Queue.Queue()
    outq = Queue.Queue()
    num_threads = 34
    mythreads = []

    for url in urlrange:
        mainqueue.put(url)

    for j in xrange(num_threads):
        mythreads.append(UrlReaderX(mainqueue, outq))
        mythreads[-1].start()

    # for i in xrange(100):
    #     time.sleep(0.1)
    #     print len(mainqueue.__dict__['queue'])

    # for i in range(100):
    while True:
        if len(mainqueue.__dict__['queue']) == 0:
            break
        time.sleep(0.1)
        sys.stdout.write("\r%f%%" % ((float(7000 - len(mainqueue.__dict__['queue']))/7000)*100))
        sys.stdout.flush()

    mainqueue.join()

    print 'in MAIN THREAD!'
    # print '\n'.join((map(str, list(outq.__dict__['queue']))))

    ####### save problems to files
    for pbl in list(outq.__dict__['queue']):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'problems' , 'problem' + str(pbl[1]) + '.html' ), 'w') as _:
            _.writelines(pbl[3].content)

    global errcount
    print 'err ', errcount
    global nonexistent
    print "missing problems:", ' '.join(nonexistent)
    with open('miss.txt', 'w') as miss_file:
        miss_file.write('\n'.join(nonexistent))

    print 'total:', len(outq.__dict__['queue'])

# main()
