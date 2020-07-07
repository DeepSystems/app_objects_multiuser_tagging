import sys
import json
import os
import threading

import supervisely_lib as sly
from supervisely_lib.api.module_api import ApiField

my_app = sly.AppService()

user2upc = {}
user2upc_remote_path = "/user2upc_demo.json"
user2upc_local_path = os.path.join(my_app.app_dir, "user2upc_demo.json")

anns_lock = threading.Lock()
anns = {}

metas_lock = threading.Lock()
metas = {}

TAG_NAME = 'upc'

#@my_app.callback(sly.app.STOP_COMMAND)
#def stop(api: sly.Api, task_id, context, state):
#    sys.exit(0)


def get_annotation(api: sly.Api, project_id, image_id):
    global anns
    if image_id not in anns:
        meta = get_project_meta(api, project_id)
        ann_json = api.annotation.download(image_id).annotation
        ann = sly.Annotation.from_json(ann_json, meta)

        global anns_lock
        anns_lock.acquire()
        anns[image_id] = ann
        anns_lock.release()

    return anns[image_id]


def get_project_meta(api: sly.Api, project_id):
    global metas
    if project_id not in metas:
        meta_json = api.project.get_meta(project_id)
        meta = sly.ProjectMeta.from_json(meta_json)

        upc_tag_meta = meta.get_tag_meta(TAG_NAME)
        if upc_tag_meta is None:
            meta = meta.add_tag_meta(sly.TagMeta(TAG_NAME, sly.TagValueType.ANY_STRING))
            api.project.update_meta(project_id, meta.to_json())

            # get meta from server again to access tag_id (tag_meta_id)
            meta_json = api.project.get_meta(project_id)
            meta = sly.ProjectMeta.from_json(meta_json)

        global metas_lock
        metas_lock.acquire()
        metas[project_id] = meta
        metas_lock.release()

    return metas[project_id]


def get_first_id(ann: sly.Annotation):
    return ann.labels[0].geometry.sly_id


def get_prev_id(ann: sly.Annotation, active_figure_id):
    for idx, label in enumerate(ann.labels):
        if label.geometry.sly_id == active_figure_id:
            if idx == 0:
                return None
            return ann.labels[idx - 1].geometry.sly_id


def get_next_id(ann: sly.Annotation, active_figure_id):
    for idx, label in enumerate(ann.labels):
        if label.geometry.sly_id == active_figure_id:
            if idx == len(ann.labels) - 1:
                return None
            return ann.labels[idx + 1].geometry.sly_id


def select_object(api: sly.Api, task_id, context, find_func, show_msg=False):
    user_id = context["userId"]
    image_id = context["imageId"]
    project_id = context["projectId"]
    ann_tool_session = context["sessionId"]

    ann = get_annotation(api, project_id, image_id)

    active_figure_id = context["figureId"]
    if active_figure_id is None:
        active_figure_id = get_first_id(ann)
    else:
        active_figure_id = find_func(ann, active_figure_id)
        if show_msg is True and active_figure_id is None:
            api.app.set_field(task_id, "state.dialogVisible", True)

    if active_figure_id is not None:
        api.img_ann_tool.set_figure(ann_tool_session, active_figure_id)


@my_app.callback("prev_object")
@sly.timeit
def prev_object(api: sly.Api, task_id, context, state):
    select_object(api, task_id, context, get_prev_id)


@my_app.callback("next_object")
@sly.timeit
def next_object(api: sly.Api, task_id, context, state):
    select_object(api, task_id, context, get_next_id, show_msg=True)


@my_app.callback("assign_tag")
@sly.timeit
def assign_tag(api: sly.Api, task_id, context, state):
    global user2upc

    project_id = context["projectId"]
    meta = get_project_meta(api, project_id)

    user_id = context["userId"]
    user2selectedUpc = api.app.get_field(task_id, 'state.user2selectedUpc')
    selected_tag_index = user2selectedUpc[str(user_id)]
    selected_upc = user2upc[str(user_id)][selected_tag_index]["upc"]

    active_figure_id = context["figureId"]
    if active_figure_id is None:
        sly.logger.warn("Figure is not selected.")

    tag_meta = meta.get_tag_meta(TAG_NAME)
    api.advanced.add_tag_to_object(tag_meta.sly_id, active_figure_id, value=selected_upc)


def main():
    # data
    api = sly.Api.from_env()

    #@TODO: how to access app start team_id?
    team_id = 1

    #files_info = api.file.list(team_id, "/")
    api.file.download(team_id, user2upc_remote_path, user2upc_local_path)

    global user2upc
    user2upc = sly.io.json.load_json_file(user2upc_local_path)

    user2selectedUpc = {}
    for key, value in user2upc.items():
        user2selectedUpc[key] = 0

    data = {
        "user2upc": user2upc
    }

    # state
    state = {
        "dialogVisible": False,
        "user2selectedUpc": user2selectedUpc
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