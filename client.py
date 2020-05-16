from cmd import Cmd
import hashlib
import requests
import json
import sys
import boto3

base_url = 'http://127.0.0.1'
cognito_client_id = ''
cognito = boto3.client('cognito-idp')


class BBSClient(Cmd):
    prompt = '% '
    auth_token = None
    username = None

    def encode_password(self, password):
        hash_key = "nctu_bbs".encode()
        encode_password = hashlib.sha256(hash_key)
        encode_password.update(password.encode())
        return encode_password.hexdigest()

    def default(self, line):
        self.stdout.write('Unknown command: %s\n' % (line,))

    def do_EOF(self, line):
        return True

    def do_exit(self, arg):
        if len(arg) > 0:
            self.default('exit ' + arg)
        else:
            print("Bye")
            return True

    def do_register(self, arg):
        argv = arg.split(" ")
        if len(argv) != 3:
            self.help_register()
        else:
            try:
                cognito.sign_up(
                    ClientId=cognito_client_id,
                    Username=argv[0],
                    Password=self.encode_password(argv[2]),
                    UserAttributes=[
                        {
                            'Name': 'email',
                            'Value': argv[1]
                        },
                    ]
                )
                requests.post(base_url + '/register', data = json.dumps({"username": argv[0]}))
            except cognito.exceptions.UsernameExistsException:
                print("Username is already used.")
            except Exception as e:
                print(e)

    def help_register(self):
        print("Usage: register <username> <email> <password>")

    def do_login(self, arg):
        argv = arg.split(" ")
        if len(argv) != 2:
            self.help_login()
        elif self.auth_token != None:
            print("Please logout first.")
        else:
            try:
                response = cognito.initiate_auth(
                    AuthFlow='USER_PASSWORD_AUTH',
                    ClientId=cognito_client_id,
                    AuthParameters={
                        'USERNAME': argv[0],
                        'PASSWORD': self.encode_password(argv[1])
                    }
                )
                self.auth_token = response['AuthenticationResult']
                self.username = argv[0]
                print("Welcome, " + self.username + ".")
            except Exception:
                print("Login failed.")

    def help_login(self):
        print("Usage: login <username> <password>")

    def do_logout(self, arg):
        if len(arg) > 0:
            self.default('logout ' + arg)
        elif self.auth_token == None:
            print("Please login first.")
        else:
            print("Bye, " + self.username + ".")
            self.username = None
            self.auth_token = None

    def do_whoami(self, arg):
        if len(arg) > 0:
            self.default('whoami ' + arg)
        elif self.auth_token == None:
            print("Please login first.")
        else:
            print(self.username + ".")
            


if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = 'https://' + sys.argv[1]
    try:
        r = requests.get(base_url + '/hello')
        if r.status_code != 200:
            exit(1)
    except:
        print("Fail to connect the server!")
        exit(1)
    response = r.json()
    cognito_client_id = response['cognito_client_id']
    BBSClient().cmdloop(response['message'])
