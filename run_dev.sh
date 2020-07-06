DOCKERIMAGE="docker.deepsystems.io/supervisely/five/base-py-sdk:import_alpha_images"
docker pull ${DOCKERIMAGE}

SLY_LIB_PATH="/ssd2/home/ds/work/sly_private/supervisely_lib"
APP_DIR=${PWD} #"/ssd2/home/ds/work/sly_apps/app_report_images_project"

SERVER_ADDRESS="http://78.46.75.100:11111/"
API_TOKEN="A1Q5vAluxaFHCf9lu2x3mECOUYVi0EzSPswruGUUS8zVfmnrLA8hw0S2e9ElhKwu4fKjQe3BOHmUIgNx0DVFKUnqmHV5vnSmynhBedXr45Qr32rt6DfkBn4C7BH2eE2Y"
AGENT_TOKEN="WoVPORZFqX1LlqONfCqQE1hleIEk7ohZ"
TASK_ID=80 #http://78.46.75.100:11111/apps/2/sessions/80

#TODO: do not forget to run agent
PYCHARM_APP_DIR="/home/ds/soft/pycharm"
PYCHARM_PROJECT_DIR="/home/ds/pycharm-settings/app_objects_multiuser_tagging"

docker run \
    --rm \
    -ti \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/.Xauthority:/root/.Xauthority \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --entrypoint="" \
    --shm-size='1G' \
    -e LOGLEVEL="DEBUG" \
    -e PYTHONUNBUFFERED='1' \
    --workdir="/workdir" \
    -v ${APP_DATA_DIR}:/sly_task_data \
    -v ${APP_DIR}:/workdir \
    -v ${SLY_LIB_PATH}:/workdir/supervisely_lib \
    -e SERVER_ADDRESS=${SERVER_ADDRESS} \
    -e API_TOKEN=${API_TOKEN} \
    -e AGENT_TOKEN=${AGENT_TOKEN} \
    -e TASK_ID=${TASK_ID} \
    -v ${PYCHARM_APP_DIR}:/pycharm \
    -v ${PYCHARM_PROJECT_DIR}:/root/.PyCharmCE2018.2 \
    -v "${PYCHARM_PROJECT_DIR}__idea":/workdir/.idea \
    ${DOCKERIMAGE} \
    bash
