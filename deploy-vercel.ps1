# Aivesto Dashboard Vercel 배포 스크립트 (PowerShell)
# Usage: .\deploy-vercel.ps1

Write-Host "🚀 Aivesto Dashboard Vercel 배포 시작" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# 1. Vercel CLI 확인
Write-Host "`n📋 단계 1: Vercel CLI 확인..."
$vercelPath = (Get-Command vercel -ErrorAction SilentlyContinue).Source
if (-not $vercelPath) {
    Write-Host "❌ Vercel CLI가 설치되지 않았습니다." -ForegroundColor Red
    Write-Host "다음 명령어로 설치하세요:" -ForegroundColor Yellow
    Write-Host "  npm install -g vercel" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Vercel CLI 설치됨: $vercelPath" -ForegroundColor Green

# 2. 프로젝트 파일 확인
Write-Host "`n📋 단계 2: 프로젝트 파일 확인..."
$files = @("vercel.json", "public/index.html", "requirements.txt")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file 파일 확인" -ForegroundColor Green
    } else {
        Write-Host "❌ $file 파일이 없습니다." -ForegroundColor Red
        exit 1
    }
}

# 3. 환경변수 확인
Write-Host "`n📋 단계 3: 환경변수 확인..."
if (Test-Path ".env") {
    Write-Host "✅ .env 파일 확인" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env 파일이 없습니다. .env.example을 복사합니다." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "👉 .env 파일을 수정하고 다시 실행하세요." -ForegroundColor Yellow
    exit 1
}

# 4. Git 상태 확인
Write-Host "`n📋 단계 4: Git 상태 확인..."
$gitStatus = git status --porcelain
if (-not $gitStatus) {
    Write-Host "✅ Working directory clean" -ForegroundColor Green
} else {
    Write-Host "⚠️  Working directory에 변경사항이 있습니다." -ForegroundColor Yellow
    Write-Host $gitStatus -ForegroundColor Gray

    $response = Read-Host "변경사항을 커밋하시겠습니까? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        git add -A
        git commit -m "Pre-deploy commit"
        Write-Host "✅ 변경사항 커밋 완료" -ForegroundColor Green
    }
}

# 5. Vercel 배포
Write-Host "`n📤 단계 5: Vercel에 배포 중..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# 프리뷰 배포
$response = Read-Host "`n프리뷰로 배포하시겠습니까? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "프리뷰 배포 시작..." -ForegroundColor Yellow
    & vercel
    Write-Host "✅ 프리뷰 배포 완료" -ForegroundColor Green
} else {
    Write-Host "프리뷰 배포를 건너뜁니다." -ForegroundColor Gray
}

# 프로덕션 배포
Write-Host "`n프로덕션에 배포하시겠습니까? (y/n)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "프로덕션 배포 시작..." -ForegroundColor Yellow
    & vercel --prod
    Write-Host "`n✅ 프로덕션 배포 완료!" -ForegroundColor Green

    Write-Host "`n다음 단계:" -ForegroundColor Cyan
    Write-Host "1. 대시보드 URL을 방문하여 확인하세요." -ForegroundColor White
    Write-Host "2. Vercel 환경변수를 설정하세요:" -ForegroundColor White
    Write-Host "   - TELEGRAM_BOT_TOKEN" -ForegroundColor White
    Write-Host "   - TELEGRAM_CHAT_IDS" -ForegroundColor White
    Write-Host "3. API 서버 URL을 설정하세요." -ForegroundColor White
} else {
    Write-Host "프로덕션 배포를 건너뜁니다." -ForegroundColor Gray
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🎉 배포 스크립트 완료" -ForegroundColor Cyan
