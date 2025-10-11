import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 50 },   // ramp up
    { duration: '1m', target: 100 },
    { duration: '1m', target: 200 },
    { duration: '1m', target: 400 },
    { duration: '1m', target: 800 },   // max load
    { duration: '1m', target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],  // allow <5% failure rate
    http_req_duration: ['p(95)<1000'], // 95% under 1s
  },
};

export default function () {
  const res = http.get('http://talentlink.local/');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
