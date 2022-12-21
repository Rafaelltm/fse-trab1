import sys

from threads.console_thread import ConsoleThread

def main():
    host = sys.argv[1]
    port = int(sys.argv[2])
    server = ConsoleThread(host, port)
    server.start()

if __name__ == '__main__':
    main()
