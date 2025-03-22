from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello(self):
        self.client.get("/")
        self.client.get("/register")
        self.client.get("/user-login")