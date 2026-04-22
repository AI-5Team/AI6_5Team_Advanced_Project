import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "개인정보처리방침 | 가게 숏폼 만들기",
};

export default function PrivacyPage() {
  return (
    <main className="legal-page">
      <header className="legal-page__header">
        <Link href="/" className="legal-page__back">← 홈으로</Link>
        <h1>개인정보처리방침</h1>
        <p className="legal-page__date">최종 업데이트: 2026년 4월 22일 · 버전 1.0</p>
      </header>

      <article className="legal-page__body">
        <h2>제1조 (처리하는 개인정보 항목)</h2>
        <p>서비스는 다음의 개인정보를 처리합니다.</p>
        <ul>
          <li>필수: 이메일 주소, 비밀번호(해시 저장), 이름, 생년월일</li>
          <li>서비스 이용 시 자동 수집: IP 주소, 브라우저 정보(User-Agent), 접속 일시</li>
          <li>SNS 연동 시: 해당 플랫폼의 OAuth 액세스 토큰(암호화 저장)</li>
          <li>구독 시: 결제 수단 ID(빌링키 ID만 저장, 카드번호 미저장)</li>
        </ul>

        <h2>제2조 (개인정보의 처리 목적)</h2>
        <ul>
          <li>서비스 회원 가입 및 관리</li>
          <li>본인 인증 및 서비스 제공</li>
          <li>SNS 자동 업로드 기능 제공</li>
          <li>구독 결제 및 청구</li>
          <li>서비스 보안 및 부정 이용 방지</li>
          <li>법정 접속 기록 보관 (통신비밀보호법)</li>
        </ul>

        <h2>제3조 (개인정보의 보유 및 이용 기간)</h2>
        <table className="legal-table">
          <thead>
            <tr><th>항목</th><th>보유 기간</th></tr>
          </thead>
          <tbody>
            <tr><td>이메일, 비밀번호 해시, 이름</td><td>회원 탈퇴 후 30일</td></tr>
            <tr><td>생년월일</td><td>회원 탈퇴 후 30일</td></tr>
            <tr><td>접속 로그 (IP, UA)</td><td>1년 (법정 의무)</td></tr>
            <tr><td>결제 정보 (빌링키 ID)</td><td>거래 종료 후 5년 (전자상거래법)</td></tr>
            <tr><td>동의 이력</td><td>회원 탈퇴 후 1년</td></tr>
          </tbody>
        </table>

        <h2>제4조 (개인정보 처리 위탁)</h2>
        <table className="legal-table">
          <thead>
            <tr><th>수탁자</th><th>위탁 업무</th></tr>
          </thead>
          <tbody>
            <tr><td>클라우드 인프라 제공자</td><td>서버 운영 및 데이터 저장</td></tr>
            <tr><td>PG사 (포트원/토스페이먼츠)</td><td>결제 처리</td></tr>
            <tr><td>이메일 발송 서비스</td><td>인증 메일 발송</td></tr>
          </tbody>
        </table>

        <h2>제5조 (개인정보의 국외 이전)</h2>
        <p>서비스는 아래와 같이 개인정보를 국외로 이전합니다.</p>
        <table className="legal-table">
          <thead>
            <tr><th>이전 국가</th><th>이전 항목</th><th>이전 목적</th></tr>
          </thead>
          <tbody>
            <tr><td>미국 등 (클라우드 리전)</td><td>이메일, IP, 콘텐츠 데이터</td><td>서비스 제공 인프라</td></tr>
            <tr><td>미국 (OpenAI 등 AI API)</td><td>프롬프트, 이미지 데이터</td><td>AI 콘텐츠 생성</td></tr>
            <tr><td>미국 (Meta/Google/TikTok)</td><td>OAuth 토큰, 콘텐츠</td><td>SNS 자동 업로드</td></tr>
          </tbody>
        </table>

        <h2>제6조 (개인정보의 파기)</h2>
        <p>
          회원 탈퇴 시 즉시 soft delete 처리 후 30일 이후 완전 삭제합니다.
          접속 로그는 1년 보관 후 파기하며, 파기 시 복구 불가능한 방법으로 삭제합니다.
        </p>

        <h2>제7조 (정보주체의 권리와 행사 방법)</h2>
        <p>이용자는 다음의 권리를 행사할 수 있습니다.</p>
        <ul>
          <li>개인정보 열람, 정정, 삭제 요청</li>
          <li>처리 정지 요청</li>
          <li>동의 철회</li>
        </ul>
        <p>권리 행사는 서비스 내 계정 설정 또는 개인정보 보호책임자 이메일로 요청할 수 있습니다.</p>

        <h2>제8조 (쿠키 운영)</h2>
        <p>
          서비스는 로그인 세션 유지를 위해 HttpOnly 쿠키를 사용합니다.
          쿠키 거부 시 로그인이 필요한 서비스를 이용할 수 없습니다.
          브라우저 설정에서 쿠키를 차단할 수 있습니다.
        </p>

        <h2>제9조 (개인정보 보호책임자)</h2>
        <p>
          개인정보 관련 문의, 불만 처리, 피해 구제를 위해 아래와 같이 개인정보 보호책임자를 지정합니다.
        </p>
        <ul>
          <li>성명: 운영자</li>
          <li>이메일: privacy@example.com</li>
          <li>신고: <a href="mailto:report@example.com">report@example.com</a></li>
        </ul>

        <h2>제10조 (안전성 확보 조치)</h2>
        <p>
          비밀번호는 argon2id 알고리즘으로 해시 저장합니다.
          SNS 토큰은 AES-256-GCM으로 암호화 저장합니다.
          세션은 HttpOnly 쿠키로 관리하며 서버 측에서 관리합니다.
          접속 기록은 1년간 보관합니다.
        </p>

        <h2>제11조 (방침 변경 시 고지)</h2>
        <p>
          본 방침이 변경될 경우 시행 7일 전 서비스 공지 또는 이메일로 안내합니다.
        </p>
      </article>
    </main>
  );
}
