from uagents import Model


class ContextPrompt(Model):
    context: str
    text: str

class Response(Model):
    text: str

class Message(Model):
    text: str

class Request(Model):
    Judgement: str
    User: str

class ResponseA(Model):
    Input: str