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
    http_req_failed: ['rate<0.05'],   // <5% errors acceptable
    http_req_duration: ['p(95)<800'], // p95 < 800ms target
  },
};

export default function () {
  const res = http.get('http://talentlink.local/');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
