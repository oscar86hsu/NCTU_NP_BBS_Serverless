#!/usr/bin/env python3
from cmd import Cmd
from datetime import datetime, timedelta
import hashlib
import requests
import json
import sys
import boto3
import threading
import websocket

base_url = 'http://127.0.0.1'
websocket_url = "ws://127.0.0.1"
cognito_client_id = ''
cognito = boto3.client('cognito-idp')

def on_message(ws, message):
    message = json.loads(message)
    print()
    print(message)

class BBSClient(Cmd):
    prompt = '% '
    auth_token = None
    username = None
    mail_list = []

    ####################################### SETUP #######################################
    def default(self, line):
        self.stdout.write('Unknown command: %s\n' % (line,))

    def do_EOF(self, line):
        return True

    def do_exit(self, arg):
        if len(arg) > 0:
            self.default('exit ' + arg)
        else:
            return True

    #################################### WEBSOCKET #####################################
    def websocket_daemon(self):
        self.ws.run_forever()

    def connect_websocket(self, username, password):
        self.ws = websocket.WebSocketApp(websocket_url, 
                                         header={'username:' + username, 'password:' + password}, 
                                         on_message=on_message)
        t = threading.Thread(target=self.websocket_daemon)
        t.setDaemon(True)
        t.start()

    def disconnect_websocket(self):
        self.ws.close()

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
                password = self.encode_password(argv[1])
                response = cognito.initiate_auth(
                    AuthFlow='USER_PASSWORD_AUTH',
                    ClientId=cognito_client_id,
                    AuthParameters={
                        'USERNAME': argv[0],
                        'PASSWORD': password
                    }
                )
                self.auth_token = response['AuthenticationResult']
                self.username = argv[0]
                print("Welcome, " + self.username + ".")
                self.connect_websocket(self.username, password)
            except Exception:
                print("Login failed.")

    def do_logout(self, arg):
        if len(arg) > 0:
            self.default('logout ' + arg)
        elif self.auth_token == None:
            print("Please login first.")
        else:
            print("Bye, " + self.username + ".")
            self.disconnect_websocket()
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
            self.default("create " + arg)

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
        now = datetime.utcnow() + timedelta(hours=8)
        date = now.strftime("%Y-%m-%d")

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
                                  {"board": argv[1], "title": title}),
                              headers={"Auth": self.auth_token['IdToken']})
            if r.status_code != 200:
                print(r.json())
                return

            presigned_url = r.json()
            post_data = {
                "board": argv[1],
                "title": title,
                "content": content,
                "author": self.username,
                "date": date,
                "comment": []
            }
            r = requests.put(presigned_url,
                             json=post_data)
            if r.status_code == 200:
                print("Create post successfully.")

    def do_list(self, arg):
        if arg.startswith("-board"):
            self.list_board(arg)
        elif arg.startswith("-post"):
            self.list_post(arg)
        elif arg.startswith("-mail"):
            self.list_mail(arg)
        elif arg.startswith("-sub"):
            self.list_sub(arg)
        else:
            self.default("list " + arg)

    def list_board(self, arg):
        argv = arg.split(" ")
        if len(argv) > 2:
            self.help_list("board")
            return
        if len(argv) > 1:
            if not argv[1].startswith("##"):
                self.help_list("board")
                return
            key = argv[1][2:]
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
            if not argv[2].startswith("##"):
                self.help_list("board")
                return
            key = argv[2][2:]
        else:
            key = ""
        r = requests.post(base_url + '/list-post',
                          data=json.dumps({"board": argv[1], "key": key}))
        print(r.json())

    def do_read(self, arg):
        r = requests.post(base_url + '/read',
                          data=json.dumps({"post_id": arg}))
        post_path = r.json()
        if not post_path.startswith("http"):
            print(post_path)
            return
        post = requests.get(post_path).json()
        print("    Author  : " + post['author'])
        print("    Title   : " + post['title'])
        print("    Date    : " + post['date'])
        print("    --")
        print("    " + post['content'].replace("<br>", "\n"))
        print("    --")
        for c in post['comment']:
            print("    {} : {}".format(c['username'], c['comment']))

    def do_delete(self, arg):
        if self.auth_token == None:
            print("Please login first.")
        elif arg.startswith("-post"):
            self.delete_post(arg)
        elif arg.startswith("-mail"):
            self.delete_mail(arg)
        else:
            self.default("delete " + arg)

    def delete_post(self, arg):
        argv = arg.split(" ")
        if len(argv) != 2:
            self.help_delete()
            return
        r = requests.post(base_url + '/delete-post',
                          data=json.dumps(
                              {"post_id": argv[1]}),
                          headers={"Auth": self.auth_token['IdToken']})
        print(r.json())

    def do_update(self, arg):
        argv = arg.split(" ")
        if argv[0] != "-post":
            self.default("update ")
            return
        if len(argv) < 4:
            self.help_update()
            return
        if (argv[2] != "--title") and (argv[2] != "--content"):
            self.help_update()
            return
        if self.auth_token == None:
            print("Please login first.")
            return

        content = ""
        for i in range(3, len(argv)):
            content += argv[i] + " "
        r = requests.post(base_url + '/update',
                          data=json.dumps(
                              {"post_id": argv[1], "update": argv[2], "content": content[:-1]}),
                          headers={"Auth": self.auth_token['IdToken']})
        print(r.json())

    def do_comment(self, arg):
        argv = arg.split(" ")
        if len(argv) < 2:
            self.help_comment()
            return
        if self.auth_token == None:
            print("Please login first.")
            return
        comment = ""
        for i in range(1, len(argv)):
            comment += argv[i] + " "

        r = requests.post(base_url + '/update',
                          data=json.dumps(
                              {"post_id": argv[0], "update": "comment", "content": comment[:-1]}),
                          headers={"Auth": self.auth_token['IdToken']})
        print(r.json())

    def help_list(self, arg):
        if arg == "board":
            print("Usage: list-board ##<key>")
        elif arg == "post":
            print("Usage: list-post <board-name> ##<key>")
        elif arg == "sub":
            print("Usage: list-sub")
        else:
            print("Usage: list-mail")

    def help_create(self, arg):
        if arg == "board":
            print("Usage: create-board <name>")
        else:
            print("Usage: create-post <board-name> --title <title> --content <content>")

    def help_read(self):
        print("Usage: read <post-id>")

    def help_delete(self):
        print("Usage: delete-post <post-id>")

    def help_update(self):
        print("Usage: update-post <post-id> --title/content <new>")

    def help_comment(self):
        print("Usage: comment <post-id> <comment>")

    ####################################### MAIL #######################################
    def do_mail(self, arg):
        argv = arg.split(" ")
        if self.auth_token == None:
            print("Please login first.")
            return
        elif len(argv) < 3:
            self.help_mail()
            return
        elif argv[0] != "-to":
            self.default("mail" + arg)
            return

        subject = ""
        content = ""
        tmp = ""

        try:
            subject_index = argv.index("--subject")
        except ValueError:
            self.help_mail()
            return

        try:
            content_index = argv.index("--content")
        except ValueError:
            self.help_mail()
            return

        while subject_index < (len(argv) - 1):
            subject_index += 1
            tmp = argv[subject_index]
            if tmp == "--content":
                break
            subject += argv[subject_index] + " "

        tmp = ""
        while content_index < (len(argv) - 1):
            content_index += 1
            tmp = argv[content_index]
            if tmp == "--subject":
                break
            content += argv[content_index] + " "

        subject = subject[:-1]
        content = content[:-1]
        if len(subject) == 0:
            print("Subject cannot be empty!\n")
            return
        else:
            r = requests.post(base_url + '/mail-to',
                              data=json.dumps(
                                  {"to": argv[1], "subject": subject}),
                              headers={"Auth": self.auth_token['IdToken']})
            if r.status_code != 200:
                print(r.json())
                return

            presigned_url = r.json()
            r = requests.put(presigned_url,
                             data=content)
            if r.status_code == 200:
                print("Sent successfully.")
            elif r.status_code == 404:
                print("{} does not exist.".format(argv[1]))
            else:
                print(r.text)

    def list_mail(self, arg):
        if self.auth_token == None:
            print("Please login first.")
            return
        r = requests.get(base_url + '/list-mail',
                         headers={"Auth": self.auth_token['IdToken']})
        self.mail_list = r.json()
        i = 0
        print("    {:8}{:12}{:12}{:12}".format(
            "ID", "Subject", "From", "Date"))
        for mail in self.mail_list:
            i = i + 1
            print("    {:8}{:12}{:12}{:12}".format(str(
                i), mail[0], mail[1], datetime.fromtimestamp(int(mail[2])).strftime("%m/%d")))

    def do_retr(self, arg):
        argv = arg.split(" ")
        if self.auth_token == None:
            print("Please login first.")
            return
        if argv[0] != "-mail":
            self.default("retr" + arg)
            return
        if len(argv) < 2:
            self.help_retr()
            return
        if len(self.mail_list) == 0:
            r = requests.get(base_url + '/list-mail',
                             headers={"Auth": self.auth_token['IdToken']})
            self.mail_list = r.json()

        try:
            mail = self.mail_list[int(argv[1])-1]
        except IndexError:
            print("No such mail.")
            return

        r = requests.post(base_url + '/retr-mail',
                          data=json.dumps(
                              {"key": '{}|{}|{}'.format(mail[0], mail[1], mail[2])}),
                          headers={"Auth": self.auth_token['IdToken']})

        presigned_url = r.json()
        r = requests.get(presigned_url)
        if r.status_code == 200:
            print("    Subject  : " + mail[0])
            print("    From     : " + mail[1])
            print("    Date     : " +
                  datetime.fromtimestamp(int(mail[2])).strftime("%Y-%m-%d"))
            print("    --")
            print("    " + r.text.replace("<br>", "\n"))
            print("    --")
        elif r.status_code == 404:
            print("No such mail.")
        else:
            print(r.text)

    def delete_mail(self, arg):
        argv = arg.split(" ")
        if len(self.mail_list) == 0:
            r = requests.get(base_url + '/list-mail',
                             headers={"Auth": self.auth_token['IdToken']})
            self.mail_list = r.json()
        try:
            mail = self.mail_list[int(argv[1])-1]
        except IndexError:
            print("No such mail.")
            return

        r = requests.post(base_url + '/delete-mail',
                          data=json.dumps(
                              {"key": '{}|{}|{}'.format(mail[0], mail[1], mail[2])}),
                          headers={"Auth": self.auth_token['IdToken']})

        if r.status_code == 200:
            del self.mail_list[int(argv[1])-1]
            print("Mail deleted.")
        else:
            print(r.text)

    def help_mail(self):
        print("Usage: mail-to <username> --subject <subject> --content <content>")

    def help_retr(self):
        print("Usage: retr-mail <mail#>")

    #################################### SUBSCRIBE #####################################
    def do_subscribe(self, arg):
        argv = arg.split(" ")
        if self.auth_token == None:
            print("Please login first.")
            return

        if argv[0] == "--board":
            index = argv.index("--board")
        elif argv[0] == "--author":
            index = argv.index("--author")
        else:
            self.help_subscribe("")
            return

        try:
            keyword_index = argv.index("--keyword")
        except ValueError:
            self.help_subscribe(argv[0])
            return

        subs = ""
        keyword = ""
        tmp = ""

        while index < (len(argv) - 1):
            index += 1
            tmp = argv[index]
            if tmp == "--keyword":
                break
            subs += argv[index] + " "

        tmp = ""
        while keyword_index < (len(argv) - 1):
            keyword_index += 1
            tmp = argv[keyword_index]
            if tmp == "--author":
                break
            keyword += argv[keyword_index] + " "

        if (len(subs) < 1) or (len(keyword) < 1):
            self.help_subscribe(argv[0])
            return

        subs = subs[:-1]
        keyword = keyword[:-1]

        r = requests.post(base_url + '/subscribe',
                          data=json.dumps(
                              {argv[0][2:]: argv[1], "keyword": keyword}),
                          headers={"Auth": self.auth_token['IdToken']})
        print(r.json())

    def do_unsubscribe(self, arg):
        argv = arg.split(" ")
        if self.auth_token == None:
            print("Please login first.")
            return

        if len(argv) < 1:
            self.help_unsubscribe("")
            return

        if len(argv) < 2:
            self.help_unsubscribe(argv[0])
            return

        if (argv[0] != "--board") and (argv[0] != "--author"):
            self.help_unsubscribe("")
            return

        r = requests.post(base_url + '/unsubscribe',
                          data=json.dumps(
                              {argv[0][2:]: arg.replace(argv[0] + " ", "")}),
                          headers={"Auth": self.auth_token['IdToken']})
        print(r.json())

    def list_sub(self, arg):
        if self.auth_token == None:
            print("Please login first.")
            return
        r = requests.get(base_url + '/list-sub',
                         headers={"Auth": self.auth_token['IdToken']})
        if r.status_code == 200:
            print(r.json())
            return
        else:
            print(r.text)

    def help_unsubscribe(self, arg):
        if arg == "--board":
            print("Usage: unsubscribe --board <board-name>")
        elif arg == "--author":
            print("usage: unsubscribe --author <author-name>")
        else:
            print("Usage: unsubscribe --board <board-name>")
            print("usage: unsubscribe --author <author-name>")

    def help_subscribe(self, arg):
        if arg == "--board":
            print("Usage: subscribe --board <board-name> --keyword <keyword>")
        elif arg == "--author":
            print("usage: subscribe --author <author-name> --keyword <keyword>")
        else:
            print("Usage: subscribe --board <board-name> --keyword <keyword>")
            print("usage: subscribe --author <author-name> --keyword <keyword>")

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
    websocket_url = response['websocket_url']
    BBSClient().cmdloop(response['message'])
