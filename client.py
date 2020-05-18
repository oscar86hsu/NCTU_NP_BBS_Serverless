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

    ####################################### SETUP #######################################
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

    ####################################### AUTH #######################################
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
                r = requests.post(base_url + '/register',
                                  data=json.dumps({"username": argv[0]}))
                if r.status_code == 200:
                    print("Register successfully.")
            except cognito.exceptions.UsernameExistsException:
                print("Username is already used.")
            except Exception as e:
                print(e)

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

    def help_register(self):
        print("Usage: register <username> <email> <password>")

    def help_login(self):
        print("Usage: login <username> <password>")

    ####################################### POST #######################################

    def do_create(self, arg):
        if self.auth_token == None:
            print("Please login first.")
        elif arg.startswith("-board"):
            self.create_board(arg)
        elif arg.startswith("-post"):
            self.create_post(arg)
        else:
            self.default("create" + arg)

    def create_board(self, arg):
        argv = arg.split(" ")
        if len(argv) != 2:
            self.help_create("board")
        else:
            r = requests.post(base_url + '/create-board', data=json.dumps(
                {"boardname": argv[1]}), headers={"Auth": self.auth_token['IdToken']})
            print(r.json())

    def create_post(self, arg):
        argv = arg.split(" ")

        title = ""
        content = ""
        tmp = ""

        try:
            title_index = argv.index("--title")
        except ValueError:
            self.help_create("post")
            return

        try:
            content_index = argv.index("--content")
        except ValueError:
            self.help_create("post")
            return

        while title_index < (len(argv) - 1):
            title_index += 1
            tmp = argv[title_index]
            if tmp == "--content":
                break
            title += argv[title_index] + " "

        tmp = ""
        while content_index < (len(argv) - 1):
            content_index += 1
            tmp = argv[content_index]
            if tmp == "--title":
                break
            content += argv[content_index] + " "

        title = title[:-1]
        content = content[:-1]
        if len(title) == 0:
            print("Title cannot be empty!\n")
            return
        else:
            r = requests.post(base_url + '/create-post',
                              data=json.dumps(
                                  {"board": argv[1], "title": title, "content": content}),
                              headers={"Auth": self.auth_token['IdToken']})
            print(r.json())

    def do_list(self, arg):
        if arg.startswith("-board"):
            self.list_board(arg)
        elif arg.startswith("-post"):
            self.list_post(arg)
        elif arg.startswith("-mail"):
            self.list_mail(arg)
        else:
            self.default("list" + arg)

    def list_board(self, arg):
        argv = arg.split(" ")
        if len(argv) > 2:
            self.help_list("board")
            return
        if len(argv) > 1:
            key = argv[1]
        else:
            key = ""
        r = requests.post(base_url + '/list-board',
                          data=json.dumps({"key": key}))
        print(r.json())

    def list_post(self, arg):
        argv = arg.split(" ")
        if len(argv) > 3 or len(argv) < 2:
            self.help_list("post")
            return
        if len(argv) > 2:
            key = argv[2]
        else:
            key = ""
        r = requests.post(base_url + '/list-post',
                          data=json.dumps({"board": argv[1], "key": key}))
        print(r.json())

    def list_mail(self, arg):
        pass

    def do_read(self, arg):
        r = requests.post(base_url + '/read',
                          data=json.dumps({"post_id": arg}))
        post_path = r.json()
        post = requests.get(post_path).json()
        print("Author  : " + post['username'])
        print("Title   : " + post['title'])
        print("Date    : " + post['date'])
        print("--")
        print(post['content'].replace("<br>", "\n"))
        print("--")
        for c in post['comment']:
            print("{} : {}".format(c['username'], c['comment']))

    def do_delete(self, arg):
        if self.auth_token == None:
            print("Please login first.")
        elif arg.startswith("-post"):
            self.delete_post(arg)
        elif arg.startswith("-mail"):
            self.delete_mail(arg)
        else:
            self.default("delete" + arg)

    def delete_post(self, arg):
        r = requests.post(base_url + '/delete-post',
                          data=json.dumps(
                              {"post_id": arg}),
                          headers={"Auth": self.auth_token['IdToken']})
        print(r.json())

    def delete_mail(self, arg):
        pass

    def help_list(self, arg):
        if arg == "board":
            print("Usage: list-board ##<key>")
        else:
            print("Usage: list-post <board-name> ##<key>")

    def help_create(self, arg):
        if arg == "board":
            print("Usage: create-board <name>")
        else:
            print("Usage: create-post <board-name> --title <title> --content <content>")

    def help_read(self):
        print("Usage: read <post-id>")

    def help_read(self):
        print("Usage: delete-post <post-id>")

    ####################################### MISC #######################################
    def encode_password(self, password):
        hash_key = "nctu_bbs".encode()
        encode_password = hashlib.sha256(hash_key)
        encode_password.update(password.encode())
        return encode_password.hexdigest()


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
