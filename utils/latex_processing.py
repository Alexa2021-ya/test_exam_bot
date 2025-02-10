import os
import logging
from pdf2image import convert_from_path
import re
import subprocess

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_latex_text(latex_text):
    # Убираем кавычки в начале и в конце
    latex_text = latex_text.strip('"').strip('“').strip('”').strip('«').strip('»')

    # Убираем пробелы и ненужные символы только перед и после конструкций
    latex_text = re.sub(r'(\\\[)\s*(.*?)\s*(\\\])',
                         lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}',
                         latex_text,
                         flags=re.DOTALL)

    latex_text = re.sub(r'(\\\()\s*(.*?)\s*(\\\))',
                         lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}',
                         latex_text,
                         flags=re.DOTALL)

    latex_text = re.sub(r'(\$\$)\s*(.*?)\s*(\$\$)',
                         lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}',
                         latex_text,
                         flags=re.DOTALL)

    return latex_text


def read_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as template_file:
        return template_file.read()


def create_latex_file(latex_text, template_content, output_tex_path):
    with open(output_tex_path, 'w', encoding='utf-8') as tex_file:
        tex_file.write(template_content)
        tex_file.write(r"\footnotesize")
        tex_file.write(latex_text)
        tex_file.write(r"\end{document}")


def compile_latex_to_pdf(tex_file_path):
    logging.info('Компиляция LaTeX-документа в PDF...')
    result = subprocess.call(['pdflatex', tex_file_path])
    if result != 0:
        logging.error('Ошибка при компиляции .tex в .pdf. Код ошибки: %d', result)
        return False
    return True


def crop_pdf(input_pdf_path, output_pdf_path):
    logging.info('Обрезка PDF...')
    result = subprocess.call(['pdfcrop', '--margins', '0 10 0 10', input_pdf_path, output_pdf_path])
    if result != 0:
        logging.error('Ошибка при обрезке PDF. Код ошибки: %d', result)
        return False
    return True


def convert_pdf_to_png(pdf_file_path, image_width, output_path):
    logging.info('Конвертация PDF в PNG...')
    images = convert_from_path(pdf_file_path, size=(image_width, None))
    for i, image in enumerate(images):
        image.save(output_path, 'PNG')
        logging.info('Сохранено изображение: %s', output_path)


def remove_temp_files(temp_files):
    logging.info('Удаление временных файлов...')
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
        except Exception as e:
            logging.error('Ошибка при удалении временного файла %s: %s', temp_file, e)


def convert_latex_to_png(latex_text, image_width, template_path, output_path):
    latex_text = clean_latex_text(latex_text)
    logging.info(latex_text)

    template_content = read_template(template_path)

    if not latex_text.strip():
        logging.info('Нет текста %s', output_path)
        return

    # Извлечение имени файла без расширения из output_path
    base_filename = os.path.splitext(os.path.basename(output_path))[0]

    # Используем base_filename как имя для .tex и .pdf
    tex_file_path = f'{base_filename}.tex'
    create_latex_file(latex_text, template_content, tex_file_path)

    if not compile_latex_to_pdf(tex_file_path):
        return

    pdf_file = f'{base_filename}.pdf'
    cropped_pdf_file = f'{base_filename}_cropped.pdf'
    if not crop_pdf(pdf_file, cropped_pdf_file):
        return

    convert_pdf_to_png(cropped_pdf_file, image_width, output_path)

    temp_files = [tex_file_path, pdf_file, cropped_pdf_file, f'{base_filename}.aux', f'{base_filename}.log']
    remove_temp_files(temp_files)