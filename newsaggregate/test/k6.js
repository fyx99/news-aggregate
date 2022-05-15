import http from 'k6/http';
import { sleep } from 'k6';

export default function () {
  http.get('http://127.0.0.1:8000/content/74d06a24-ae32-4cf3-be20-a8d98be251b4');
  sleep(1);
}