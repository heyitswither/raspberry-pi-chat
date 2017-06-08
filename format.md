# Packet Formats

## Authentication

### Clients send this to authenticate

```json
{
  "type": "auth",
  "username": "your_username",
  "password": "your_password"
}
```

### Received if new account

```json
{
  "type": "auth",
  "new_account": true,
  "success": true
}
```

### Received if existing account, correct password

```json
{
  "type": "auth",
  "new_account": false,
  "success": "true"
}
```

### Received if existing account, incorrect password

```json
{
  "type": "auth",
  "new_account": false,
  "success": false
}
```

## User statuses

### On user join

```json
{
  "type": "join",
  "username": "user_that_joined"
}
```

### On user quit

```json
{
  "type": "quit",
  "username": "user_that_quit"
}
```

## User list

```json
{
  "type": "user_list",
  "users": [
    "user1",
    "user2",
    "user3",
    "...",
    "usern"
  ]
}
```

## Normal messages

### Sent

```json
{
  "type": "message",
  "message": "message_content"
}
```

### Received

```json
{
  "type": "message",
  "author": "author_of_message",
  "message": "message_content"
}
```

## Private messages

### Sent

```json
{
  "type": "direct_message",
  "recipient": "recipient_of_message",
  "message": "message_content"
}
```

### Received

```json
{
  "type": "direct_message",
  "author": "author_of_message",
  "message": "message_content"
}
```
