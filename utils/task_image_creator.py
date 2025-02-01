import logging
from utils.create_directory import create_directory, load_config
import matplotlib.pyplot as plt
import os
import textwrap
from utils.template_image_generator import build_final_image_from_template

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_latex_image(latex_text: str, output_path: str, filename: str, max_width: int) -> str:
    create_directory(output_path)
    file_path = os.path.join(output_path, filename)

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')  # Устанавливаем шрифт
    plt.rc('text.latex', preamble=r'\usepackage[utf8]{inputenc}\usepackage[russian]{babel}\usepackage{amsmath}')

    # Разделяем текст по существующим переносам строк
    lines = latex_text.split('\n')
    wrapped_lines = []

    # Разбиваем каждую строку с учетом ширины
    for line in lines:
        # Форматируем строку для MathText
        wrapped_lines.append(textwrap.fill(line, width=max_width))

    # Объединяем строки обратно с переносами
    wrapped_text = '\n'.join(wrapped_lines)

    # Создаем фигуру и ось с прозрачным фоном
    fig, ax = plt.subplots()
    fig.patch.set_facecolor('none')  # Установка цвета фона фигуры на прозрачный
    ax.set_facecolor('none')  # Установка цвета фона оси на прозрачный
    ax.axis('off')

    # Устанавливаем максимальную ширину текста
    ax.text(0.5, 0.5, rf'{wrapped_text}', fontsize=12, ha='center', va='center', wrap=True)

    try:
        # Сохранение изображения с прозрачным фоном
        plt.savefig(file_path, bbox_inches='tight', dpi=300, transparent=True)
        plt.close(fig)
    except Exception as e:
        logging.error(f"Ошибка при сохранении MathText: {e}")

    logging.info(f"Изображение сохранено по пути: {file_path}")

    return file_path



def generate_task_images_with_template(data: list[dict], dir_name: str, template_json_path: str):
    # Создаем директорию для сохранения изображений
    create_directory(dir_name)  # Создаем директорию, если её
    config = load_config(template_json_path)
    # Получаем полный путь к директории
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_name)

    for record in data:
        # Генерируем изображения для текста задания
        task_image_path = generate_latex_image(record['task_text'], output_path,
                                                 generate_image_name_for_task_text(record['id']),
                                                 config['MAX_MATHTEXT_WIDTH'])

        record['photo_task'] = build_final_image_from_template(
                record['id'],
                record['task_number'],
                task_image_path,
                os.path.join(output_path, generate_image_name_for_photo_task(record['id'])),
                config,
                record['task_image']
            )

        # Генерируем изображения для решения задания
        solution_image_path = generate_latex_image(record['task_solution'], output_path,
                                                    generate_image_name_for_task_solution(record['id']),
                                                    config['MAX_MATHTEXT_WIDTH'])

        record['photo_solution'] = build_final_image_from_template(
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
