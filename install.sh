#!/bin/bash
# =============================================================================
# Solaar App Launcher - Install Script
# =============================================================================
set -e

echo "🖱️ Solaar App Launcher - 설치 스크립트"
echo "=========================================="

# 1. 실행 파일 복사
echo "[1/3] 실행 파일 복사 중..."
mkdir -p ~/.local/bin
cp src/solaar-app-launcher.py ~/.local/bin/
cp src/solaar-app-launcher.sh ~/.local/bin/
chmod +x ~/.local/bin/solaar-app-launcher.sh
chmod +x ~/.local/bin/solaar-app-launcher.py
echo "  ✔ ~/.local/bin/solaar-app-launcher.py"
echo "  ✔ ~/.local/bin/solaar-app-launcher.sh"

# 2. 기본 설정 파일 (이미 있으면 스킵)
echo "[2/3] 설정 파일 확인 중..."
mkdir -p ~/.config/solaar
if [ ! -f ~/.config/solaar/app-launcher-apps.conf ]; then
    cp config/app-launcher-apps.conf.example ~/.config/solaar/app-launcher-apps.conf
    echo "  ✔ 기본 앱 목록 생성: ~/.config/solaar/app-launcher-apps.conf"
else
    echo "  ⏭ 기존 앱 목록 유지: ~/.config/solaar/app-launcher-apps.conf"
fi

# 3. Solaar 규칙 안내
echo "[3/3] Solaar 규칙 설정..."
echo ""
echo "  ⚠️  Solaar 규칙(rules.yaml)은 수동으로 설정해야 합니다."
echo "  참고 파일: config/rules.yaml.example"
echo ""
echo "  Solaar GUI에서 설정하는 방법:"
echo "    1. Solaar 열기"
echo "    2. 마우스 선택 → 'Rule Editor' 탭"
echo "    3. Gesture Button에 'Mouse Gesture' 규칙 추가"
echo "    4. 제스처 없이 클릭 시 실행할 명령:"
echo "       ~/.local/bin/solaar-app-launcher.sh"
echo ""

echo "=========================================="
echo "✅ 설치 완료!"
echo ""
echo "사용법:"
echo "  MX Master 3S의 Gesture Button(엄지 버튼)을 클릭하세요."
echo "  다시 누르면 런처가 종료됩니다."
