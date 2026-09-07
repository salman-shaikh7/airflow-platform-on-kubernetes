import pendulum

from airflow.sdk import dag, task


@dag(
    dag_id="hello_kubernetes",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    tags=["learning", "kubernetes"],
)
def hello_kubernetes():
    @task
    def say_hello():
        print("Hello from an Airflow task running in Kubernetes!")
        return "Task completed successfully"

    say_hello()


hello_kubernetes()

