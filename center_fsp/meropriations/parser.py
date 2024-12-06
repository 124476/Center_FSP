import datetime
import re
import ssl
from urllib.request import urlopen, Request
import os
import PyPDF2

import meropriations.models


def get_discipline(disciplines):
    disciplines_pattern = r"дисциплины?\s*([A-Za-z0-9-]+(?:\s*,\s*[A-Za-z0-9-]+)*)|КЛАСС\s*([A-Za-z0-9-]+(?:\s*,\s*[A-Za-z0-9-]+)*)"
    matches = re.findall(disciplines_pattern, disciplines)
    disciplines = []
    for match in matches:
        if match[0]:
            disciplines.extend(match[0].split(", "))
        elif match[1]:
            disciplines.extend(match[1].split(", "))
    return " ".join(set(disciplines))


def import_pdf():
    url = (
        "https://storage.minsport.gov.ru/cms-uploads/cms/"
        "II_chast_EKP_2024_14_11_24_65c6deea36.pdf"
    )

    pdf_file_path = "media/large_document.pdf"

    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

    context = ssl._create_unverified_context()
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(request, context=context) as response:
        with open(pdf_file_path, "wb") as f:
            while chunk := response.read(1024 * 1024):
                f.write(chunk)

    with open(pdf_file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text

    text = re.sub(r"Стр\. \d+ из \d{4}", "", text)
    lines = text.split("\n")

    meropriations.models.Tip.objects.all().delete()
    meropriations.models.Structure.objects.all().delete()
    meropriations.models.Group.objects.all().delete()
    meropriations.models.Meropriation.objects.all().delete()

    tip_list = (
        "ЧЕМПИОНАТ",
        "КУБОК",
        "МЕЖРЕГИОНАЛЬНОЕ",
        "УЧЕБНО-ТРЕНИРОВОЧНОЕ",
        "МЕЖДУНАРОДНЫЕ",
        "ПЕРВЕНСТВО",
        "ВСЕРОССИЙСКОЕ",
        "ДРУГОЕ",
    )
    for tip_name in tip_list:
        meropriations.models.Tip.objects.create(name=tip_name)

    structures = [
        meropriations.models.Structure(name="Основной состав"),
        meropriations.models.Structure(name="Молодежный (резервный) состав"),
    ]
    meropriations.models.Structure.objects.bulk_create(structures)

    group = None
    meropriation = None
    i_index = 0
    counter = 0
    bulk_meropriations = []

    date_pattern_start = r"(\d{2}\.\d{2}\.\d{4})(.*)"
    date_pattern_end = r"^(.*?)(\d{2}\.\d{2}\.\d{4})$"
    int_pattern = r"(.*?)(\d+)$"
    date_string_int_pattern = r"^(\d{2}\.\d{2}\.\d{4})(.*?)(\d+)$"
    string_pattern = r"^([а-яА-ЯёЁa-zA-Z]+)(\d{2}\.\d{2}\.\d{4})$"

    list_users = (
        "женщины",
        "юниоры",
        "мужчины",
        "юноши",
        "юниорки",
        "мальчики",
        "девушки",
        "девочки",
    )

    for line in lines[15:]:
        if counter % 100 == 0:
            print(f"Обработано строк: {counter}/{len(lines)}")

        if not line:
            break

        if line == "Основной состав":
            structure = meropriations.models.Structure.objects.get(
                name="Основной состав"
            )
        elif line == "Молодежный (резервный) состав":
            structure = meropriations.models.Structure.objects.get(
                name="Молодежный (резервный) состав"
            )

        if i_index == 0 and line[0].isalpha() and line.isupper():
            group = meropriations.models.Group(name=line)
            group.save()

        if i_index == 0 and line[0].isdigit():
            list_line = line.split()
            event_slug = list_line[0]
            event_name = " ".join(list_line[1:])
            for tip_item in meropriations.models.Tip.objects.exclude(
                name="ВСЕ"
            ):
                if tip_item.name[:-3] in event_name:
                    tip = tip_item
                    break
            else:
                tip = meropriations.models.Tip.objects.get(name="ДРУГОЕ")

            meropriation = meropriations.models.Meropriation(
                name=event_name,
                tip=tip,
                group=group,
                slug=event_slug,
                structure=structure,
            )

            i_index = 1

        elif (
            line.split(",")[0] in list_users
            or line.split()[0] in list_users
            or (
                re.match(string_pattern, line)
                and re.match(string_pattern, line).group(1) in list_users
            )
        ):
            remaining_text = line
            i_index = 2
            if re.match(date_pattern_end, line):
                match = re.match(date_pattern_end, line)
                remaining_text = match.group(1)
                date = match.group(2)
                meropriation.date_start = datetime.datetime.strptime(
                    date, "%d.%m.%Y"
                ).date()
                i_index = 3

            if not meropriation.text:
                meropriation.text = remaining_text
            else:
                meropriation.text += "\n" + remaining_text

        elif i_index == 1:
            meropriation.name += " " + line

        elif i_index == 1 or i_index == 2:
            remaining_text = line
            i_index = 2
            if re.match(date_pattern_end, line):
                match = re.match(date_pattern_end, line)
                remaining_text = match.group(1)
                date = match.group(2)
                meropriation.date_start = datetime.datetime.strptime(
                    date, "%d.%m.%Y"
                ).date()
                i_index = 3

            if not meropriation.text:
                meropriation.text = remaining_text
            else:
                meropriation.text += "\n" + remaining_text

        # Завершение обработки мероприятия
        elif i_index == 3 and re.match(date_string_int_pattern, line):
            match = re.match(date_string_int_pattern, line)
            date_part = match.group(1).strip()
            text_part = match.group(2).strip()
            number_part = int(match.group(3))
            meropriation.date_end = datetime.datetime.strptime(
                date_part, "%d.%m.%Y"
            ).date()
            meropriation.place = text_part
            meropriation.count = number_part
            disciplines = re.sub(r"^.*?дисциплины\s*", "", meropriation.text)
            meropriation.disciplines = get_discipline(disciplines)
            meropriation.normal_place = meropriation.place.lower()

            bulk_meropriations.append(meropriation)
            i_index = 0

        elif i_index == 3 and re.match(int_pattern, line):
            match = re.match(int_pattern, line)
            text_part = match.group(1).strip()
            number_part = int(match.group(2))
            meropriation.place += "\n" + text_part
            meropriation.count = number_part
            disciplines = re.sub(r"^.*?дисциплины\s*", "", meropriation.text)
            meropriation.disciplines = get_discipline(disciplines)
            meropriation.normal_place = meropriation.place.lower()

            bulk_meropriations.append(meropriation)
            i_index = 0

        elif i_index == 3 and meropriation.place:
            meropriation.place += "\n" + line
        elif i_index == 3:
            match = re.match(date_pattern_start, line)
            date = match.group(1)
            remaining_text = match.group(2)
            meropriation.date_end = datetime.datetime.strptime(
                date, "%d.%m.%Y"
            ).date()
            meropriation.place = remaining_text

        counter += 1

    meropriations.models.Meropriation.objects.bulk_create(bulk_meropriations)
    print(f"Обработано мероприятий: {len(bulk_meropriations)}")
