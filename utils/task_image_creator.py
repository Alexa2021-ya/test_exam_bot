import subprocess
from utils.create_directory import create_directory, load_config
import os
import logging
from pdf2image import convert_from_path
from utils.template_image_generator import create_image_with_text
from PIL import Image

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_latex_to_png(latex_text, image_width, template_path, output_path):
    # Чтение шаблона из файла
    with open(template_path, "r", encoding='utf-8') as template_file:
        template_content = template_file.read()

    # Проверка на пустое содержимое latex_text
    if not latex_text.strip():  # Если latex_text пустой или содержит только пробелы
        logging.warning("LaTeX текст пуст. Сохраняем пустое изображение.")
        # Сохранение пустого изображения
        empty_image = Image.new("RGB", (image_width, 100), (255, 255, 255))
        empty_image.save(output_path, 'PNG')
        return

    # Создание LaTeX-документа
    with open("filename.tex", "w", encoding='utf-8') as tex_file:
        tex_file.write(template_content)  # Запись содержимого шаблона
        tex_file.write(latex_text)  # Вставка текста из переменной
        tex_file.write(r"\end{document}")  # Завершение документа

    # Компиляция LaTeX-документа в PDF
    logging.info("Компиляция LaTeX-документа в PDF...")
    result = subprocess.call(["pdflatex", "filename.tex"])
    if result != 0:
        logging.error("Ошибка при компиляции .tex в .pdf. Код ошибки: %d", result)
        return

    # Применение pdfcrop к PDF
    logging.info("Обрезка PDF...")
    result = subprocess.call(["pdfcrop", "--margins", "10 10 10 10", "filename.pdf", "filename_cropped.pdf"])
    if result != 0:
        logging.error("Ошибка при обрезке PDF. Код ошибки: %d", result)
        return

    # Конвертация обрезанного PDF в PNG с помощью pdf2image
    pdf_file = "filename_cropped.pdf"

    # Ограничение ширины изображения
    logging.info("Конвертация PDF в PNG...")
    images = convert_from_path(pdf_file, size=(image_width, None))  # Ограничиваем только ширину

    for i, image in enumerate(images):
        image.save(output_path, 'PNG')
        logging.info(f"Сохранено изображение: {output_path}")

    # Удаление временных файлов
    logging.info("Удаление временных файлов...")
    try:
        os.remove("filename.tex")
        os.remove("filename.pdf")
        os.remove("filename_cropped.pdf")
        os.remove("filename.aux")
        os.remove("filename.log")
        logging.info("Временные файлы успешно удалены.")
    except Exception as e:
        logging.error("Ошибка при удалении временных файлов: %s", e)

def generate_latex_image(latex_text: str, output_path: str, filename: str, config) -> str:
    create_directory(output_path)
    file_path = os.path.join(output_path, filename)

    convert_latex_to_png(latex_text, config['WIDTH_LATEX_PNG'], config['LATEX_TEMPLATE_PATH'], file_path)

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
                                                 config)

        record['photo_task'] = create_image_with_text(
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
                                                    config)

        record['photo_solution'] = create_image_with_text(
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
