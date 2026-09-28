# Entities 

- User 
    - id
    - name
    - email
- Tasks 
    - id
    - title - str
    - descitpion - str
    - creator - User
    - assignee - User

    - Task Types - enum
        - Feature
        - Bug
        - Story
    - Status - enum 
        - Open
        - In progress
        - Resolved
        - Delayed

# Operations

- create_task(user_id, title, desc, type)
- assign_task(task_id, assignee)
- update_task_status(task_id, status)
- get_tasks(user_id)


