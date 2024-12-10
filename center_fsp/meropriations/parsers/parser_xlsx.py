import openpyxl
from meropriations.models import Team, Participant, Result


def parse_excel_file(excel_file, meropriation_id):
    try:
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not row or row[0] is None:
                continue

            team_name = row[0]
            status = row[1] if row[1] else "PARTICIPANT"
            members_list = [member for member in row[2:] if member]
            team = Team.objects.create(
                name=team_name,
                status=status,
            )

            for member_name in members_list:
                if member_name.strip():
                    Participant.objects.create(
                        name=member_name,
                        team=team,
                    )

            Result.objects.create(
                meropriation_id=meropriation_id,
                team=team,
            )

        return {"success": True, "message": "Импорт данных завершен успешно."}

    except Exception as e:
        print(f"Ошибка при парсинге файла на строке {row_idx}: {e}")
        return {"success": False, "message": str(e)}
