import logging
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_font(size, font_path):
    """Попытаться загрузить указанный шрифт, иначе использовать стандартный."""
    try:
        return ImageFont.truetype(font_path, size)
    except Exception as e:
        logging.error(f"Ошибка загрузки шрифта: {e}")
        return ImageFont.load_default()

def load_image_with_transparency(image_path):
    """Загружает изображение и делает белый фон прозрачным."""
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > 200 and item[1] > 200 and item[2] > 200:  # белый фон
            new_data.append((255, 255, 255, 0))  # Сделать прозрачным
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def calculate_new_height(img1, img2=None, config=None):
    """Вычисляет новую высоту изображения с учетом отступов."""
    input_height = img1.height
    if img2:
        input_height += img2.height + 20
    return max(input_height, config["MIN_HEIGHT"] - config["TOP_PADDING"] - config["BOTTOM_PADDING"])

def create_base_image(input_height, config):
    """Создает новое изображение с белым фоном."""
    new_height = config["TOP_PADDING"] + config["BOTTOM_PADDING"] + input_height
    return Image.new('RGB', (config["NEW_WIDTH"], new_height), 'white'), new_height

def draw_text(draw, new_image, font_bot, font_number, font_tg, task_number, id_task, logo_x, new_height, config):
    """Рисует текст на новом изображении."""
    draw.text((config["TITLE_TEXT_X"], config["TITLE_TEXT_Y"]), config["TITLE_TEXT"], font=font_bot, fill=config["COLOR_TITLE"])
    draw.text((config["NUMBER_TEXT_X"], config["NUMBER_TEXT_Y"]), f"№{task_number}", font=font_number, fill=config["COLOR_TITLE"])
    draw.text((config["ID_TEXT_X"], new_height - config["ID_TEXT_Y_OFFSET"]), f"#id{id_task}", font=font_tg, fill=config["COLOR_ID"])

def add_logo(new_image, new_height, config):
    """Добавляет логотип на новое изображение."""
    logo = load_image_with_transparency(config["LOGO_PATH"])
    logo = logo.resize((152, 152))
    logo_x = config["NEW_WIDTH"] - 78 - logo.width
    logo_y = new_height - config["LOGO_Y_OFFSET"] - logo.height
    new_image.paste(logo, (logo_x, logo_y), logo)
    return logo_x

def draw_rotated_text(draw, new_image, text, new_height, config, horizontal_spacing=100):
    """Рисует повернутый текст на новом изображении с увеличенным расстоянием по горизонтали."""
    text_bbox = draw.textbbox((0, 0), text, font=load_font(config["FONT_TG_NAME_SIZE"], config["FONT_PATH"]))
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Устанавливаем расстояния по вертикали и горизонтали
    y_offset_start = 172
    vertical_spacing = 500  # Увеличенное значение расстояния между парами текстов
    for y_offset in range(y_offset_start, new_height - config["BOTTOM_PADDING"], vertical_spacing):
        # Создаем новое изображение для текста
        text_image_rotated = Image.new('RGBA', (text_width, text_height), (255, 255, 255, 0))
        text_draw_rotated = ImageDraw.Draw(text_image_rotated)
        text_draw_rotated.text((0, 0), text, font=load_font(config["FONT_TG_NAME_SIZE"], config["FONT_PATH"]), fill=config["COLOR_TG_NAME_ROTATED_TEXT"])

        rotated_text_image_offset = text_image_rotated.rotate(-30, expand=1)

        # Координаты для вставки с учетом горизонтального расстояния
        rotated_text_x_1 = int(160)
        rotated_text_x_2 = int(config["NEW_WIDTH"] - 221.38 - rotated_text_image_offset.width)

        # Вставка повернутого текста
        new_image.paste(rotated_text_image_offset, (rotated_text_x_1, int(y_offset)), rotated_text_image_offset)
        new_image.paste(rotated_text_image_offset, (rotated_text_x_2 + horizontal_spacing, int(y_offset)), rotated_text_image_offset)



def paste_images(new_image, img1, img2, top_padding):
    """Вставляет изображения в новое изображение с отступами."""
    y_offset = top_padding
    left_offset_img1 = 49
    left_offset_img2 = 49

    # Вставляем первое изображение
    new_image.paste(img1, (left_offset_img1, y_offset), img1)
    y_offset += img1.height

    # Если есть второе изображение, вставляем его
    if img2:
        y_offset += 10  # Добавляем отступ в 10 пикселей перед вторым изображением
        new_image.paste(img2, (left_offset_img2, y_offset), img2)
    else:
        y_offset += 10  # Добавляем отступ в 10 пикселей, если второго изображения нет


def draw_tg_name_text(draw, new_image, text, config, new_height):
    """Рисует текст TG_NAME_TEXT на новом изображении."""
    font_tg_name = load_font(config["FONT_TG_NAME_SIZE"], config["FONT_PATH"])  # Предположим, что у вас есть размер шрифта для TG_NAME_TEXT
    text_bbox = draw.textbbox((0, 0), text, font=font_tg_name)
    text_width = text_bbox[2] - text_bbox[0]

    # Позиции для текста
    text_x = new_image.width - 249 - text_width
    text_y = new_height - 33 - text_bbox[3]  # 33 от нижнего края

    draw.text((text_x, text_y), text, font=font_tg_name, fill=config["COLOR_TG_NAME_TEXT"])  # Предположим, что у вас есть цвет для TG_NAME_TEXT

def create_image_with_text(id_task, task_number, img1_path, output_path, config, img2_path=None):
    logging.info(f'{img1_path}')
    img1 = load_image_with_transparency(img1_path)
    img2 = load_image_with_transparency(img2_path) if img2_path else None

    input_height = calculate_new_height(img1, img2, config)
    new_image, new_height = create_base_image(input_height, config)

    draw = ImageDraw.Draw(new_image)
    font_bot = load_font(config["FONT_BOT_SIZE"], config["FONT_PATH"])
    font_number = load_font(config["FONT_NUMBER_SIZE"], config["FONT_PATH"])
    font_tg = load_font(config["FONT_TG_NAME_SIZE"], config["FONT_PATH"])

    logo_x = add_logo(new_image, new_height, config)
    draw_text(draw, new_image, font_bot, font_number, font_tg, task_number, id_task, logo_x, new_height, config)

    # Заменяем отрисовку повернутого текста на отрисовку TG_NAME_TEXT
    draw_tg_name_text(draw, new_image, config["TG_NAME_TEXT"], config, new_height)

    # Если вы хотите сохранить повернутый текст, вы можете оставить этот вызов
    draw_rotated_text(draw, new_image, config["TG_NAME_TEXT"], new_height, config)

    paste_images(new_image, img1, img2, config["TOP_PADDING"])

    new_image.save(output_path)
    logging.info(f"Изображение сохранено: {output_path}")

    return output_path