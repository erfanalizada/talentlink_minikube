import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  stages: [
    { duration: '20s', target: 50 },
    { duration: '1m', target: 50 },
    { duration: '20s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],  // less than 1% failed
    http_req_duration: ['p(95)<400'], // 95% under 400ms
  },
};

// Ingress base URL
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
    const url = `${BASE}${path}`;
    const res = http.get(url);
    check(res, {
      [`${path} status is 200`]: (r) => r.status === 200,
    });
  }
  sleep(1);
}
