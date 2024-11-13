import requests


def get_students_with_param_mix(role: str, active_project: bool, archived_project: bool):
    url = f"http://127.0.0.1:8000/students/{role}"
    response = requests.get(url, params={"active_project": active_project, "archived_project": archived_project})
    return response.json()


students = get_students_with_param_mix('user', active_project=False, archived_project=True)
print(students)