from locust import HttpUser, task, wait_time

class TournamentUser(HttpUser):
    # Simulate a user waiting between 15-25 seconds (matching your auto-refresh)
    wait_time = wait_time.between(15, 25)

    @task
    def view_standings(self):
        self.client.get("/championship/view/")