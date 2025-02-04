import logging
from utils.create_directory import create_directory, load_config
import matplotlib.pyplot as plt
import os
import textwrap
from utils.template_image_generator import build_final_image_from_template

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fit_text_to_area(latex_text: str, initial_fontsize: float, area_width: float, area_height: float) -> (str, float):
    # Начальные параметры
    fontsize = initial_fontsize
    max_attempts = 100  # Максимальное количество попыток уменьшения шрифта
    attempts = 0

    while attempts < max_attempts:
        # Создание фигуры для проверки размера текста
        fig, ax = plt.subplots(figsize=(area_width, area_height))
        ax.axis('off')

        # Разделение текста на строки, чтобы сохранить существующие переносы
        existing_lines = latex_text.splitlines()
        wrapped_lines = []

        for line in existing_lines:
            # Обработка каждой строки с учетом ширины
            wrapped_lines.extend(textwrap.wrap(line, width=100))  # Добавляем новые переносы

        wrapped_text = '\n'.join(wrapped_lines)

        # Добавление текста
        text_obj = ax.text(0, 0.5, wrapped_text, fontsize=fontsize, ha='left', va='center', wrap=True)

        # Получение размеров текста
        fig.canvas.draw()
        text_bbox = text_obj.get_window_extent(renderer=fig.canvas.get_renderer())
        text_width, text_height = text_bbox.width / fig.dpi, text_bbox.height / fig.dpi

        # Проверка, помещается ли текст в заданную область
        if text_width <= area_width and text_height <= area_height:
            plt.close(fig)
            return wrapped_text, fontsize  # Возвращаем текст и размер шрифта

        # Уменьшаем размер шрифта и увеличиваем количество попыток
        fontsize -= 1
        attempts += 1
        plt.close(fig)

    # Если не удалось найти подходящий размер шрифта, возвращаем последний результат
    return wrapped_text, fontsize


def generate_latex_image(latex_text: str, output_path: str, filename: str, task_image: str = None, config: dict = None) -> str:
    if config is None:
        raise ValueError("Configuration dictionary must be provided.")

    create_directory(output_path)
    file_path = os.path.join(output_path, filename)

    # Настройка LaTeX
    plt.rc('text', usetex=config['LATEX']['USE_TEX'])
    plt.rc('font', family=config['LATEX']['FONT_FAMILY'])
    plt.rc('text.latex', preamble=''.join(config['LATEX']['PREAMBLE']))

    # Параметры изображения
    if not task_image:
        dpi = config['LATEX']['DPI']  # Точек на дюйм
        fig_width = config['LATEX']['FIGURE_WIDTH'] / dpi  # Ширина в дюймах
        fig_height = config['LATEX']['FIGURE_HEIGHT'] / dpi  # Высота в дюймах
    else:
        dpi = config['LATEX']['DPI']  # Точек на дюйм
        fig_width = config['LATEX']['FIGURE_WIDTH'] / dpi / 2  # Ширина в дюймах
        fig_height = config['LATEX']['FIGURE_HEIGHT'] / dpi  # Высота в дюймах

    logging.info(f"Input text: {latex_text}")

    #wrapped_text, fontsize = fit_text_to_area(latex_text, config['FONT_SIZE_NUMBER_FOR_TASK_TEXT'], fig_width, fig_height)
    wrapped_text, fontsize = fit_text_to_area(latex_text, config['FONT_SIZE_NUMBER_FOR_TASK_TEXT'], fig_width, fig_height)

    logging.info(f"Wrapped text: {wrapped_text} fontsize {fontsize}")

    # Создание фигуры
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    ax.axis('off')

    # Добавление текста
    ax.text(0, 0.5, wrapped_text, fontsize=fontsize, ha='left', va='center', wrap=True)

    try:
        plt.savefig(file_path, bbox_inches='tight', dpi=dpi, transparent=True)
        plt.close(fig)
    except Exception as e:
        logging.error(f"Error during saving LaTeX image: {e}")

    logging.info(f"Image saved at: {file_path}")
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
                                                 task_image=record['task_image'],
                                                 config=config)

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
                                                    config=config
                                                    )

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
