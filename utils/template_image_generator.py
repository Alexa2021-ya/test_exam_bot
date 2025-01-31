import json
from PIL import Image, ImageDraw, ImageFont
import logging
from environs import Env

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_font(size, font_path):
    """Попытаться загрузить указанный шрифт, иначе использовать стандартный."""
    try:
        return ImageFont.truetype(font_path, size)
    except Exception as e:
        print(f"Ошибка загрузки шрифта: {e}")
        return ImageFont.load_default()


def add_text(draw, text, position, font, text_color):
    """Добавить текст на изображение."""
    draw.text(position, text, fill=text_color, font=font)


def resize_image(img, max_width, max_height):
    """Изменить размер изображения с сохранением пропорций."""
    original_width, original_height = img.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return img.resize((new_width, new_height), Image.LANCZOS)


def adjust_font_size_for_text(draw, text, max_width, initial_font_size, font_path):
    """Настроить размер шрифта, чтобы текст не выходил за максимальную ширину."""
    font_size = initial_font_size
    font = load_font(font_size, font_path)

    # Проверяем, вмещается ли текст
    while draw.textbbox((0, 0), text, font=font)[2] > max_width and font_size > 1:
        font_size -= 1
        font = load_font(font_size, font_path)

    return font


def build_final_image_from_template(id_task, task_number, img1_path, output_path, config, img2_path=None):
    # Открываем шаблон
    template = Image.open(config['TEMPLATE_PATH']).convert("RGBA")
    draw = ImageDraw.Draw(template)

    # Получаем размеры шаблона
    width, height = template.size

    # Настраиваем шрифт для номера задания
    text_number = f"№{task_number}"
    font_number = adjust_font_size_for_text(draw, text_number, config['MAX_TEXT_WIDTH_NUMBER'], config['FONT_SIZE_NUMBER'], config['FONT_PATH'])

    # Добавляем текст с номером
    add_text(draw, text_number, (config['TEXT_POSITION_NUMBER_X'], 33), font_number, config['TEXT_COLOR'])

    # Добавляем текст #id4 в левом нижнем углу
    id_text = f'#id{id_task}'
    id_font = adjust_font_size_for_text(draw, id_text, config['MAX_TEXT_WIDTH_ID'], config['FONT_SIZE_ID'], config['FONT_PATH'])
    TEXT_POSITION_ID_Y = height - config['BOTTOM_MARGIN'] + 8
    add_text(draw, id_text, (config['TEXT_POSITION_NUMBER_X'], TEXT_POSITION_ID_Y), id_font, config['TEXT_COLOR'])

    # Рассчитываем доступную высоту для изображений
    available_height = height - config['TOP_MARGIN'] - config['BOTTOM_MARGIN']

    # Вставка первого и второго изображений
    img1 = Image.open(img1_path).convert("RGBA") if img1_path else None
    img2 = Image.open(img2_path).convert("RGBA") if img2_path else None

    # Если первое изображение существует, мы его масштабируем
    if img1:
        img1 = resize_image(img1, (width - 40) // 2, available_height)

    # Если второе изображение существует, мы его масштабируем
    if img2:
        img2 = resize_image(img2, (width - 40) // 2, available_height)

    # Позиции для изображений
    if img1 and img2:
        y = (height - max(img1.height, img2.height)) // 2
        x1 = (width - img1.width - img2.width - 20) // 2
        x2 = x1 + img1.width + 20
        template.paste(img1, (x1, y), img1)
        template.paste(img2, (x2, y + (img1.height - img2.height) // 2), img2)  # Центрируем img2 по высоте относительно img1
    elif img1:
        img1 = resize_image(img1, width - 40, available_height)
        x = (width - img1.width) // 2
        y = (height - img1.height) // 2
        template.paste(img1, (x, y), img1)

    # Сохраняем результат
    template.save(output_path, quality=95)
    logging.info(f"Изображение сохранено как {output_path}")

    return output_path