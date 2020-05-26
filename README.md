# NCTU_NP_BBS_Serverless
<br>
Bulletin Board System (BBS).
<br>
The program handles multiple connections and receives user command from standard input.
<br>
This program is built from AWS SAM and can be deploy by AWS CLI.
<br>
---

## Requirement
- Python 3.6 or above
- AWS CLI
- AWS SAM

## User Commands
| Command Format | Description|
| ------------- | -------------|
| register `<username>` `<email>` `<password>` | Register with username, email and password. `<username>` must be unique. `<email>` and `<password>` have no limitation.<br>If username is already used, show failed message, otherwise it is success. |
| login `<username>` `<password>` | Login with username and password.<br>Fail(1): User already login.<br>Fail(2): Username or password is incorrect. |
| logout | Logout account.<br>If login not yet, show failed message, otherwise logout successfully. |
| whoami | Show your username.<br>If login not yet, show failed message, otherwise show username. |
| create-board `<name>` | Create a board which named `<name>`.<br>`<name>` must be unique. If Board's name is already used, show failed message, otherwise it is success. Must be logged in when creating board’s name |
| create-post `<board-name>` --title `<title>` --content `<content>` <br>(command is in the same line ) | Create a post which title is `<title>` and content is `<content>`.<br>Use --title and --content to separate titles and content.<br>`<title>` can have space but only in one line. `<content>` can have space, and key in `<br>` to indicate a new line. |
| list-board ##`<key>` | List all boards in BBS. `<key>` is a keyword, use ##`<key>` to do advanced query. |
| list-post `<board-name>` ##`<key>` | List all posts in a board named `<board-name>` `<key>` is a keyword, use ##`<key>` to do advanced query. |
| read `<post-id>` | Show the post which ID is `<post-id>`. |
| delete-post `<post-id>` | Delete the post which ID is `<post-id>`.<br>Only the post owner can delete the post.<br>If the user is not the post owner, show failed message, otherwise it is success. |
| update-post `<post-id>` --title/content `<new>` | Update the post which ID is `<post-id>`.<Br>Use -- to decide which to modify, title or content, and replaced by `<new>`.<br>Only the post owner can update the post. If the user is not the post owner, show failed message, otherwise it is success. |
| comment `<post-id> <comment>` | Leave a comment `<comment>` at the post which ID is `<post-id>` |
| mail-to `<username>` --subject `<subject>` --content `<content>` | Send a mail whose subject is `<subject>` and content is `<content>` to user `<username>`.<br>Use --subject and --content to separate subject and content.<br>`<subject>` has the same format as `<title>` of the post.<br>`<content>` has the same format as `<content>` of the post. |
| list-mail | List all incoming mails of the current logged in user. |
| retr-mail `<mail#>` | Retrieve the content of the mail `<mail#>` |
| delete-mail `<mail#>` | Delete mail `<mail#>` from your mailbox. |
| exit | Close connection. |

## Usage
- Server : Run `sam build && sam deploy` in server folder.

- Client : `./client.py <Server API Address>`


