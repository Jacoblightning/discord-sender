# Discord Sender
## Description
 A discord module that lets you send messages as a user
## Why this?
Other discord self-bots have more features but take up much more space. This can only send messages (for now) and is much more lightweight.
## Installation
### Install Using pip:
`pip install discord-sender`
## Usage
### Create a User:
```python
# Import the module
import discord_sender.discord
# Create a user
user = discord_sender.discord.DiscordUser()
```
### Authenticate with discord
#### Token Authentication (recommended):
```python
user.login_with_token(<token>)
```
#### Credential Authentication:
```python
user.login_with_credentials(<email>, <password>)
```
### Send a message

```python
user.send_message_to_userID(<message>, <user id of recipient>)
```
## Other commands
### Check if user is logged in
```python
if user.logged_in():
    do_stuff()
```
### Send a message to a channel id
#### Also works in servers
```python
user.send_message_to_channel(<message>, <channel id>)
```
### Get channel id for dm with user by user id
```python
user.get_channel_id(<user id of recipient>)
```
### Get a logged in users token
```python
# Works even if credential auth was used
# Returns None if not logged in
user.user_info.get_token()
```
### Get dms
```python
user.get_dms(<nice formatting, True or False>)
```
### Get user info by id
```python
user.get_user_info_by_id(<user id>)
```
## Experimental:
### Send message to username
```python
user.send_message_to_username(<message>, <username>)
```
### Get channel info
```python
user.get_channel_info(<channel id>)
```
### Get user info by username
```python
user.get_user_info_by_username(<username>)
```
## For the future
- [ ] Add cookie authentication
- [X] Add sending in servers
- [ ] Add tests