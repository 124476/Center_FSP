from meropriations.models import Team, Participant, Result


def parse_txt_file(txt_file, meropriation_id):
    try:
        content = txt_file.read().decode("utf-8")
        lines = content.splitlines()

        teams = Team.objects.filter(result__meropriation_id=meropriation_id)
        for team in teams:
            team.delete()
        Result.objects.filter(meropriation_id=meropriation_id).delete()

        for line_number, line in enumerate(lines, start=1):
            if line_number == 1:
                continue
            line = line.strip()
            if not line:
                continue

            data = [x.strip() for x in line.split(",")]

            team_name = data[0]
            status = data[1] if data[1] else "PARTICIPANT"
            members = data[2].split(";")
            captain_name = members[0]

            team = Team.objects.create(
                name=team_name,
                status=status,
            )

            captain = Participant.objects.create(
                name=captain_name,
                team=team,
            )

            for member_name in members[1:]:
                Participant.objects.create(
                    name=member_name,
                    team=team,
                )

            Result.objects.create(
                meropriation_id=meropriation_id,
                captain=captain,
                team=team,
            )

        return {"success": True,
                "message": "Импорт данных из TXT завершен успешно."}

    except Exception as e:
        return {"success": False, "message": str(e)}
