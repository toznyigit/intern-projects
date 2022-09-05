import ccmd, signal
from os import geteuid

master = None
def handler(signum, frame):
    master.app.destroy()
    master.do_exit(None)
    exit(0)


if __name__ == "__main__":
    if geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    else:
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGQUIT, handler)
        master = ccmd.CCMD()
        master.cmdloop()
