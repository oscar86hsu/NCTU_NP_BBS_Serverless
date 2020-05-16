from cmd import Cmd
import requests, json

class BBSClient(Cmd):
    prompt = '% '

    def __init__(self, completekey, stdin, stdout):
        super().__init__(completekey, stdin, stdout)
        r = requests.get('https://bbs.oscarhsu.me/hello/')
        if r.status_code != 200:
            print("Fail to connect the server!")
            exit(1)
        print(r.json()['message'])

        
    def do_exit(self, inp):
        print("Bye")
        return True
 


if __name__ == "__main__":
    BBSClient('tab', None, None).cmdloop()