import os
import asyncio
from utils.latex_processing import convert_latex_to_png
from utils.template_image_generator import create_image_with_text
from utils.create_directory import create_directory, load_config

async def generate_latex_image(latex_text: str, output_path: str, filename: str, config) -> str:
    create_directory(output_path)
    file_path = os.path.join(output_path, filename)

    loop = asyncio.get_event_loop()
    # Используем run_in_executor для выполнения синхронной функции в асинхронном контексте
    await loop.run_in_executor(None, convert_latex_to_png, latex_text, config['WIDTH_LATEX_PNG'], config['LATEX_TEMPLATE_PATH'], file_path)

    return file_path

# Остальная часть вашего кода...
async def generate_task_images_with_template(data: list[dict], dir_name: str, template_json_path: str):
    create_directory(dir_name)
    config = load_config(template_json_path)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_name)

    for record in data:
        task_image_path = await generate_latex_image(record['task_text'], output_path,
                                                     generate_image_name_for_task_text(record['id']),
                                                     config)

        record['photo_task'] = await create_image_with_text(
                record['id'],
                record['task_number'],
                task_image_path,
                os.path.join(output_path, generate_image_name_for_photo_task(record['id'])),
                config,
                record['task_image']
            )

        solution_image_path = await generate_latex_image(record['task_solution'], output_path,
                                                          generate_image_name_for_task_solution(record['id']),
                                                          config)

        record['photo_solution'] = await create_image_with_text(
                record['id'],
                record['task_number'],
                solution_image_path,
                os.path.join(output_path, generate_image_name_for_photo_solution(record['id'])),
                config
            )

    return data

def generate_image_name_for_task_text(image_id: int):
    return f'task_text_id_{image_id}.png'

def generate_image_name_for_task_solution(image_id: int):
    return f'task_solution_id_{image_id}.png'

def generate_image_name_for_photo_task(image_id: int):
    return f'task_photo_task_id_{image_id}.png'

def generate_image_name_for_photo_solution(image_id: int):
    return f'task_photo_solution_id_{image_id}.png'