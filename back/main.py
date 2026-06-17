from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# API 요청 데이터 모델
class SupplementRequest(BaseModel):
    symptoms: List[str]
    supplements: List[str]
    fatigue_level: int
    lifestyle: str

@app.post("/analyze")
async def analyze_supplements(data: SupplementRequest):
    user_supps = set(data.supplements)
    user_symptoms = set(data.symptoms)
    
    conflicts = []
    synergies = []
    
    # 1. 상극 조합 판독
    if {"철분", "칼슘"}.issubset(user_supps):
        conflicts.append({"combination": "철분 × 칼슘", "reason": "칼슘과 철분은 체내 흡수 경로가 같아 동시 복용 시 서로의 흡수를 강력하게 방해합니다. 철분은 공복에, 칼슘은 식후에 2시간 이상 간격을 두고 드세요."})
    
    if {"철분", "마그네슘"}.issubset(user_supps):
        conflicts.append({"combination": "철분 × 마그네슘", "reason": "마그네슘은 철분의 체내 흡수율을 떨어뜨립니다. 두 성분은 최소 2시간의 시간 차를 두고 복용하는 것이 좋습니다."})

    if {"칼슘", "마그네슘"}.issubset(user_supps) and "종합비타민" in user_supps:
        conflicts.append({"combination": "칼슘/마그네슘 × 종합비타민 중복 주의", "reason": "종합비타민에도 미네랄이 포함되어 있어 고함량 칼슘/마그네슘 제품과 동시 복용 시 미네랄 과다로 요로결석이나 위장장애를 유발할 수 있으니 함량을 확인하세요."})

    # 2. 시너지 조합 판독
    if {"철분", "비타민C"}.issubset(user_supps):
        synergies.append({"combination": "철분 + 비타민C", "reason": "비타민C가 철분의 산화를 막고, 흡수하기 좋은 형태로 변형시켜 체내 흡수율을 비약적으로 상승시킵니다."})
        
    if {"칼슘", "마그네슘", "비타민D"}.issubset(user_supps):
        synergies.append({"combination": "칼슘 + 마그네슘 + 비타민D (뼈 건강 황금조합)", "reason": "비타민D가 칼슘의 흡수를 돕고, 마그네슘이 칼슘이 혈관에 쌓이지 않고 뼈로 가도록 이정표 역할을 해주는 최상의 조합입니다."})
    elif {"칼슘", "마그네슘"}.issubset(user_supps):
        synergies.append({ "combination": "칼슘 + 마그네슘", "reason": "칼슘 and 마그네슘은 2:1 혹은 1:1 비율로 함께 복용할 때 부작용을 줄이고 체내 대사 효능이 극대화됩니다."})

    if {"오메가3", "루테인"}.issubset(user_supps):
        synergies.append({"combination": "오메가3 + 루테인", "reason": "루테인은 망막 중심을 보호하고, 오메가3는 눈의 건조함을 막아주어 시각 피로 개선에 뛰어난 복합 효과를 냅니다."})

    if {"비타민B", "밀크씨슬"}.issubset(user_supps):
        synergies.append({"combination": "비타민B 군 + 밀크씨슬", "reason": "밀크씨슬이 간 해독 능력을 도우면, 비타민B군이 간 세포의 에너지 대사를 활성화하여 피로 회복 속도가 배가됩니다."})

    # 3. 사용자 맞춤형 추천 로직
    recs_dict = {}

    def add_rec(supp, reason):
        # 복용 중인 영양제 제외 및 중복 추천 시 이유 병합
        if supp in user_supps:
            return
        if supp not in recs_dict:
            recs_dict[supp] = reason
        else:
            recs_dict[supp] += f" 또한, {reason}"

    # 3-1. 생활 습관 기반 추천
    if data.lifestyle == "☀️ 야외 활동 및 햇빛 노출 부족":
        add_rec("비타민D", "실내 생활로 부족해진 햇빛을 대체하여 뼈 건강과 면역력을 유지하는 데 필수적입니다.")
    elif data.lifestyle == "🥤 커피/카페인 과다 섭취":
        if {"철분", "칼슘", "마그네슘"}.intersection(user_supps):
            conflicts.append({"combination": "카페인 × 미네랄 영양제", "reason": "커피의 탄닌과 카페인이 미네랄과 결합해 몸 밖으로 배출시킵니다. 커피 복용 전후 2시간은 영양제 섭취를 금하세요."})
    elif data.lifestyle == "🍞 탄수화물 및 당류 과다 섭취":
        add_rec("비타민B", "당질과 탄수화물을 에너지로 연산하고 분해하는 데 대량 소모되므로 보충이 필요합니다.")
        add_rec("유산균", "과도한 당류는 장내 유해균의 먹이가 되므로 유익균을 늘려 장내 환경을 방어해야 합니다.")
    elif data.lifestyle == "🚬 잦은 흡연":
        add_rec("비타민C", "흡연 시 발생하는 유해 물질이 체내 항산화 물질을 극심하게 파괴하므로 고함량 보충이 강력히 권장됩니다.")
    elif data.lifestyle == "🍺 잦은 음주":
        add_rec("밀크씨슬", "알코올 분해로 손상되는 간 세포를 보호하고 독성 물질 해독에 직접적인 도움을 줍니다.")
        add_rec("비타민B", "알코올 대사 과정에서 다량 고갈되므로 숙취 및 피로 방지를 위해 필요합니다.")
    elif data.lifestyle == "🏋️ 고강도 운동 취미":
        add_rec("마그네슘", "운동 후 근육의 급격한 수축 및 이완을 정상화하고 쥐가 나는 것을 방지합니다.")
        add_rec("비타민B", "고강도 운동 시 필요한 근육 에너지 생성 및 단백질 대사를 촉진합니다.")

    # 3-2. 건강 증상 기반 추천
    if "만성피로/수면 질 저하" in user_symptoms or "수면부족" in user_symptoms:
        add_rec("마그네슘", "천연 진정제 역할을 하여 신경을 안정시키고 깊은 수면(숙면)을 유도하는 데 탁월합니다.")
    if "안구건조" in user_symptoms:
        add_rec("오메가3", "눈물 막을 기름지게 보호하여 눈 건조감과 뻑뻑함을 개선합니다.")
    if "관절통증" in user_symptoms or "근육통" in user_symptoms:
        add_rec("칼슘", "뼈와 관절 조직을 조밀하게 만들어 골밀도를 강화합니다.")
        add_rec("비타민D", "칼슘의 체내 흡수율을 높여 관절과 뼈 건강을 돕습니다.")
    if "면역력저하" in user_symptoms:
        add_rec("비타민C", "백혈구 기능을 강화하고 외부 바이러스 침입에 저항하는 면역 장벽을 구축합니다.")
        add_rec("유산균", "인체 면역 세포의 70%가 존재하는 장 생태계를 건강하게 만들어 근본적인 면역력을 올립니다.")
    if "소화불량/변비" in user_symptoms:
        add_rec("유산균", "장내 유익균을 증식시키고 유해균을 억제하여 배변 활동 및 소화 효율 개선을 돕습니다.")
        add_rec("마그네슘", "장내 수분을 끌어당겨 변을 부드럽게 만들고 장 운동을 활발하게 촉진합니다.")

    # 3-3. 피로도 수치 기반 추천
    if data.fatigue_level >= 8:
        add_rec("비타민B", "체력이 좋지 않은 상태에서 에너지 부스팅을 위해 흡수가 빠른 활성형 비타민이 필요합니다.")

    # 최종 결과 반환 포맷
    recommendations = [{"supplement": k, "reason": v} for k, v in recs_dict.items()]

    if conflicts:
        status = "danger"
    elif synergies:
        status = "success"
    else:
        status = "info"

    return {
        "status": status,
        "conflicts": conflicts,
        "synergies": synergies,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)