# CopyFi Frontend (Vue 3 + Vite)

رابط کاربری فارسی/RTL برای سرویس اشتراک‌گذاری متن و فایل (Pastehub-like) با Vue 3، TailwindCSS و DaisyUI.

## Tech Stack

- Vue 3 + Vite
- Vue Router
- Pinia
- Axios
- TailwindCSS + DaisyUI (`silk` theme)
- RTL + Persian-first UI

## Features

- ساخت پیست جدید (متن)
- آپلود فایل برای ساخت پیست فایل
- مشاهده پیست با اکشن‌ها: کپی، اشتراک لینک، نمایش خام، دانلود، گزارش
- پیست‌های عمومی اخیر با صفحه‌بندی
- احراز هویت: ورود، ثبت‌نام، پروفایل
- صفحه ادمین گزارش‌ها (Placeholder)
- Toast و پیام‌های فارسی

## Project Structure

```text
src/
  assets/
  components/
  pages/
  router/
  services/
    api/
    http.js
  stores/
  utils/
  App.vue
  main.js
```

## Prerequisites

- Node.js 18+ (پیشنهاد: Node 20+)
- npm 9+

## Installation

```bash
npm install
```

## Environment Variables

یک فایل `.env` در ریشه پروژه بسازید:

```bash
VITE_API_BASE_URL=http://localhost:5001
```

نکته:
- اگر ست نشود، مقدار پیش‌فرض در کد `http://localhost:5001` است.
- اگر بک‌اند شما مسیر دیگری دارد، همین مقدار را تغییر دهید.

## Run (Development)

```bash
npm run dev
```

Frontend به صورت پیش‌فرض روی:
- `http://localhost:5173`

## Build (Production)

```bash
npm run build
npm run preview
```

## RTL + Theme Defaults

در `src/main.js` تنظیم شده:

- `lang="fa"`
- `dir="rtl"`
- `data-theme="silk"`

## Routing

- `/` ایجاد پیست
- `/p/:id` مشاهده پیست
- `/recent` پیست‌های عمومی اخیر
- `/login` ورود
- `/register` ثبت‌نام
- `/profile` پروفایل کاربر
- `/admin/reports` گزارش‌ها (نیاز به admin)

## API Endpoints Used (Current Frontend)

Frontend فعلی با این endpointها کار می‌کند:

- `POST /api/v1/pastes`
- `POST /api/v1/pastes/file`
- `GET /api/v1/pastes/:slug`
- `GET /api/v1/pastes/:slug/raw`
- `GET /api/v1/pastes/:slug/download`
- `POST /api/v1/pastes/:slug/report`
- `GET /api/v1/pastes/recent`
- `GET /api/v1/me/pastes`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/logout`

فایل‌های API:
- `src/services/api/pastes.js`
- `src/services/api/auth.js`

## Backend Sync Notes

اگر بک‌اند در مسیر `/backend` است:

1. بک‌اند را اجرا کنید (طبق README خودش)
2. مطمئن شوید CORS برای `http://localhost:5173` فعال است
3. مقدار `VITE_API_BASE_URL` را با آدرس واقعی بک‌اند ست کنید

نمونه رایج:
- `http://localhost:5001`

## File Upload Notes

در فرم ساخت پیست:

- آپلود فایل پشتیبانی می‌شود
- فایل‌های متنی مستقیم خوانده و به محتوا تبدیل می‌شوند
- آپلود فایل باینری مثل `pdf/xlsx/pptx/zip` باید از endpoint فایل بک‌اند (`/api/v1/pastes/file`) پشتیبانی شود

اگر نوع فایل خاصی در UI دیده نمی‌شود:
- ورودی فایل و `accept` را در `src/components/PasteForm.vue` بررسی کنید
- از پشتیبانی همان نوع فایل در بک‌اند مطمئن شوید

## Auth & Token

- توکن در `localStorage` ذخیره می‌شود
- در هر درخواست به صورت `Authorization: Bearer ...` ارسال می‌شود
- در خطای `401` (به‌جز خطاهای رمز پیست)، کاربر logout و به `/login` هدایت می‌شود

فایل مرتبط:
- `src/services/http.js`

## Troubleshooting

1. خطای CORS:
- CORS بک‌اند را برای دامنه فرانت فعال کنید.

2. خطای 401 بعد از login:
- بررسی کنید پاسخ login توکن معتبر برمی‌گرداند.

3. لیست اخیر یا مشاهده پیست کار نمی‌کند:
- تطابق آدرس endpointها را با بک‌اند چک کنید.

4. ظاهر یا فونت اعمال نشده:
- مطمئن شوید فایل‌های فونت در `src/assets/fonts` موجودند و CSS لود می‌شود.

## Git / Push Notes

فایل `.gitignore` اضافه شده و شامل موارد اصلی است:

- `node_modules/`
- `dist/`
- فایل‌های env و لاگ‌ها
- کش‌ها و فایل‌های IDE/OS

## Quick Start (One Shot)

```bash
npm install
echo "VITE_API_BASE_URL=http://localhost:5001" > .env
npm run dev
```

---

اگر خواستی، در قدم بعدی یک `README-backend-connection.md` هم اضافه می‌کنم که دقیقا بر اساس ساختار واقعی `/backend` همین پروژه نوشته شود.
