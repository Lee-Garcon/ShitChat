# ShitChat
The worst irc-like http chat server code you've ever seen

## Installation

This script doesn't come with hosting. Thus, you will need to run it on your own server. I usually use ngrok to host my chat server.

## FAQ

Note: No-one actually asks any questions about this. That has to do with the fact that I have no friends to talk about this to apart from one dude who prefers irc.

### What's the deal with the weird request types?

All of the request types are passed through JSON (be thankful it wasn't just strings).

#### Fields

##### mtype

The type of request.

If 'mtype' is 'message', then the request is a comment post.
If 'mtype' is 'retrieve', then the request is a retrieve request. The request returns a list of all messages.
If 'mtype' is 'shutdown', then the request is a shutdown request. You will need to enter the password you entered when you set up the server to back up your data.

More coming soon (not like it's needed or anything)

##### contents

The content of the message.

Will be blank if 'mtype' is not 'message'.

##### from

Whoever sent the message.

Will be the username of the person who sent the message. Can overlap with others.

##### time

Epoch time the message was sent. Does not include miliseconds. Int type.

#### Why though?

I don't know much about networking.
That's pretty much it.

### Is there any encryption?

Not right now. It's coming soon, but I'm thinking of ways to implement keys and other stuff. SSL is out of the question, though.

