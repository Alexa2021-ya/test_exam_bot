from PIL import Image, ImageDraw, ImageFont
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_font(size, font_path):
    """Попытаться загрузить указанный шрифт, иначе использовать стандартный."""
    try:
        return ImageFont.truetype(font_path, size)
    except Exception as e:
        logging.error(f"Ошибка загрузки шрифта: {e}")
        return ImageFont.load_default()

def add_text(draw, text, position, font, text_color):
    """Добавить текст на изображение."""
    draw.text(position, text, fill=text_color, font=font)

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
    font_number = adjust_font_size_for_text(draw, text_number, config['MAX_TEXT_WIDTH_NUMBER'], config['FONT_SIZE_NUMBER_FOR_TEMPLATE'], config['FONT_PATH'])

    # Добавляем текст с номером
    add_text(draw, text_number, (config['TEXT_POSITION_NUMBER_X'], 33), font_number, config['TEXT_COLOR'])

    # Добавляем текст #id в левом нижнем углу
    id_text = f'#id{id_task}'
    id_font = adjust_font_size_for_text(draw, id_text, config['MAX_TEXT_WIDTH_ID'], config['FONT_SIZE_ID'], config['FONT_PATH'])
    TEXT_POSITION_ID_Y = height - config['BOTTOM_MARGIN'] + config['MARGIN_BOTTOM_ID']
    add_text(draw, id_text, (config['TEXT_POSITION_NUMBER_X'], TEXT_POSITION_ID_Y), id_font, config['TEXT_COLOR'])

    # Вставка первого изображения без изменения размера
    img1 = Image.open(img1_path).convert("RGBA") if img1_path else None

    # Если первое изображение существует, мы его вставляем без изменения размера
    if img1:
        x1 = config['IMG1_X_POSITION']  # Отступ от левого края
        y1 = config['IMG1_Y_POSITION']  # Отступ от верхнего края
        logging.info(f"Вставка изображения img1 с размерами: {img1.size}, позиции: {(x1, y1)}")
        template.paste(img1, (x1, y1), img1)

    # Вставка второго изображения без изменения размера
    img2 = Image.open(img2_path).convert("RGBA") if img2_path else None

    # Если второе изображение существует, мы его вставляем без изменения размера
    if img2:
        x2 = width - img2.width - config['IMG2_OFFSET_RIGHT']  # Отступ от правого края
        y2 = config['IMG2_Y_POSITION']  # Отступ от верхнего края
        logging.info(f"Вставка изображения img2 с размерами: {img2.size}, позиции: {(x2, y2)}")
        template.paste(img2, (x2, y2), img2)

    # Сохраняем результат
    template.save(output_path, quality=95)
    logging.info(f"Изображение сохранено как {output_path}")

    return output_path