import sys
import json
import os
import supervisely_lib as sly

my_app = sly.AppService()

user2upc = {}
user2upc_remote_path = "/user2upc_demo.json"
user2upc_local_path = os.path.join(my_app.app_dir, "user2upc_demo.json")

user2selectedUpc = {}

#@my_app.callback(sly.app.STOP_COMMAND)
#def stop(api: sly.Api, task_id, context, state):
#    sys.exit(0)


# @my_app.callback("assign")
# @sly.timeit
# def assign(api: sly.Api, task_id, context, state):
#     pass


def main():
    # data
    api = sly.Api.from_env()

    #@TODO: how to access app start team_id?
    team_id = 1

    #files_info = api.file.list(team_id, "/")
    api.file.download(team_id, user2upc_remote_path, user2upc_local_path)

    global user2upc
    user2upc = sly.io.json.load_json_file(user2upc_local_path)

    global user2selectedUpc
    for key, value in user2upc.items():
        user2selectedUpc[key] = 0

    data = {
        "user2upc": user2upc,
        "user2selectedUpc": user2selectedUpc
    }

    # state
    state = {
    }

    # # start event after successful service run
    # events = [
    #     {
    #         "state": {},
    #         "context": {},
    #         "command": "calculate"
    #     }
    # ]

    # Run application service
    my_app.run(data=data, state=state)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sly.logger.critical('Unexpected exception in main.', exc_info=True, extra={
            'event_type': sly.EventType.TASK_CRASHED,
            'exc_str': str(e),
        })

#@TODO:
# python -m pip install git+https://github.com/supervisely/supervisely
# python setup.py develop
# context + state по всем юзерам? + там будет labelerLogin, api_token, и тд