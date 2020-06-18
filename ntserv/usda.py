import math

from .libserver import Response


def GET_calc_bodyfat(request):
    body = request.json

    gender = body["gender"]
    age = body["age"]
    height = body["height"]

    # Navy measurements
    waist = body.get("waist")
    if gender == "female":
        hip = body.get("hip")
    neck = body.get("neck")

    # 3-site calipers
    chest = body.get("chest")
    ab = body.get("ab")
    thigh = body.get("thigh")

    # 7-site calipers
    tricep = body.get("tricep")
    sub = body.get("sub")
    sup = body.get("sup")
    mid = body.get("mid")

    # Navy test
    if gender == "male":
        denom = (
            1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)
        )
    else:
        denom = (
            1.29579
            - 0.35004 * math.log10(waist + hip - neck)
            + 0.22100 * math.log10(height)
        )
    navy = round(495 / denom - 450, 2)

    # 3-site test
    s3 = chest + ab + thigh
    if gender == "male":
        denom = 1.10938 - 0.0008267 * s3 + 0.0000016 * s3 * s3 - 0.0002574 * age
    else:
        denom = 1.089733 - 0.0009245 * s3 + 0.0000025 * s3 * s3 - 0.0000979 * age
    three_site = round(495 / denom - 450, 2)

    # 7-site test
    s7 = chest + ab + thigh + tricep + sub + sup + mid
    if gender == "male":
        denom = 1.112 - 0.00043499 * s7 + 0.00000055 * s7 * s7 - 0.00028826 * age
    else:
        denom = 1.097 - 0.00046971 * s7 + 0.00000056 * s7 * s7 - 0.00012828 * age
    seven_site = round(495 / denom - 450, 2)

    return Response(
        data={"navy": navy, "three-site": three_site, "seven-site": seven_site}
    )


def GET_calc_lblimits(request):
    body = request.json
    height = body["height"]

    desired_bf = body.get("desired-bf")

    wrist = body.get("wrist")
    ankle = body.get("ankle")

    # Martin Berkhan
    min = round((height - 102) * 2.205, 1)
    max = round((height - 98) * 2.205, 1)
    mb = {"notes": "Contest shape (5-6%)", "weight": f"{min} ~ {max} lbs"}

    # Eric Helms
    min = round(4851.00 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
    max = round(5402.25 * height * 0.01 * height * 0.01 / (100.0 - desired_bf), 1)
    eh = {"notes": f"{desired_bf}% bodyfat", "weight": f"{min} ~ {max} lbs"}

    # Casey Butt, PhD
    h = height / 2.54
    w = wrist / 2.54
    a = ankle / 2.54
    weight = round(
        h ** (3 / 2)
        * (math.sqrt(w) / 22.6670 + math.sqrt(a) / 17.0104)
        * (1 + desired_bf / 224),
        1,
    )
    cb = {
        "notes": f"{desired_bf}% bodyfat",
        "weight": f"{weight} lbs",
        "chest": round(1.625 * w + 1.3682 * a + 0.3562 * h, 2),
        "arm": round(1.1709 * w + 0.1350 * h, 2),
        "forearm": round(0.950 * w + 0.1041 * h, 2),
        "neck": round(1.1875 * w + 0.1301 * h, 2),
        "thigh": round(1.4737 * a + 0.1918 * h, 2),
        "calf": round(0.9812 * a + 0.1250 * h, 2),
    }
    return Response(data={"martin-berkhan": mb, "eric-helms": eh, "casey-butt": cb})
