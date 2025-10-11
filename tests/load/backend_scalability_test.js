import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '2m', target: 400 },
    { duration: '3m', target: 400 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<800'],
  },
};

const BASE = 'http://talentlink.local/api';
const endpoints = [
  '/auth/health',
  '/users/health',
  '/jobs/health',
  '/cv/health',
  '/matching/health',
  '/notifications/health',
];

export default function () {
  for (const path of endpoints) {
    const res = http.get(`${BASE}${path}`);
    check(res, { [`${path} is 200`]: (r) => r.status === 200 });
  }
  sleep(1);
}
