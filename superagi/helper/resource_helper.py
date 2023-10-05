from superagi.config.config import get_config
from superagi.models.resource import Resource
import os
import datetime


class ResourceHelper:

    @staticmethod
    def make_written_file_resource(file_name: str, agent_id: int, file, channel):
        path = get_config("RESOURCES_OUTPUT_ROOT_DIR")
        storage_type = get_config("STORAGE_TYPE")
        file_extension = os.path.splitext(file_name)[1][1:]

        if file_extension in ["png", "jpg", "jpeg"]:
            file_type = f"image/{file_extension}"
        elif file_extension == "txt":
            file_type = "application/txt"
        else:
            file_type = "application/misc"

        root_dir = get_config('RESOURCES_OUTPUT_ROOT_DIR')

        if root_dir is not None:
            root_dir = (
                root_dir
                if root_dir.startswith("/")
                else f"{os.getcwd()}/{root_dir}"
            )
            root_dir = root_dir if root_dir.endswith("/") else f"{root_dir}/"
            final_path = root_dir + file_name
        else:
            final_path = f"{os.getcwd()}/{file_name}"

        file_size = os.path.getsize(final_path)

        if storage_type == "S3":
            file_name_parts = file_name.split('.')
            file_name = (
                f'{file_name_parts[0]}_'
                + str(datetime.datetime.now())
                .replace(' ', '')
                .replace('.', '')
                .replace(':', '')
                + '.'
                + file_name_parts[1]
            )
            path = 'input' if channel == "INPUT" else 'output'
        print(f"{path}/{file_name}")
        return Resource(
            name=file_name,
            path=f"{path}/{file_name}",
            storage_type=storage_type,
            size=file_size,
            type=file_type,
            channel="OUTPUT",
            agent_id=agent_id,
        )
